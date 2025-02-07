#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
create_order_list.py

Generate 20 different order files (CSV) for each grammar (ADR/HDR).
Each grammar thus produces 40 CSV files:
  - order_1_session1.csv, order_1_session2.csv
  - order_2_session1.csv, order_2_session2.csv
  ...
  - order_20_session1.csv, order_20_session2.csv

We have subfolders like "ADR_short_grammatical", "ADR_short_replacement", etc.
Each subfolder has a corresponding CSV (from generate_sequence_list.py)
like "ADR_grammatical_short.csv", which includes columns with 'position'.

According to your plan (short/long, grammatical/replacement/concatenation),
we read all .wav in each folder, shuffle, then the first half (or intended portion)
goes to session1, the second half goes to session2, etc.

Crucial update:
We now ALSO read the CSV from generate_sequence_list.py to link each .wav
to its 'position' value and store that in the final output.

The resulting CSV columns now are:
    trial_index, audio_filename, condition, position
"""

import os
import csv
import random

# ========================== CONFIG ==========================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(SCRIPT_DIR)

# Root folder that contains subfolders like "ADR_short_grammatical",
# "HDR_long_concatenation", etc., each with .wav files.
STIM_ROOT = os.path.join(PARENT_DIR, "stimuli", "sequences","combined_wav")

# The CSV folder produced by generate_sequence_list.py
SEQUENCES_CSV_DIR = os.path.join(PARENT_DIR, "stimuli", "sequences","sequences_csv")

# We'll produce 20 random orders per grammar
N_ORDERS = 20

# Where to save the final CSVs
OUTPUT_DIR = os.path.join(PARENT_DIR, "experiment", "order_lists", "short")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Grammar list
GRAMMARS = ["ADR","HDR"]

# We'll define the subfolder name pattern as: f"{grammar}_{length}_{category}"
LENGTHS = ["short"]  # if you also need long, add "long" here
CATEGORIES = ["grammatical","replacement","concatenation"]

# The total expected counts for each (length, category).
NEEDED_TOTAL = {
    ("short","grammatical"): 96,
    ("long","grammatical"): 384,
    ("short","replacement"): 12,
    ("short","concatenation"): 12,
    ("long","replacement"): 48,
    ("long","concatenation"): 48,
}


def get_wav_list(folder_path):
    """
    Return all .wav file names in the given folder (no subdirectories).
    (Just the filename, e.g. 'A1_e_b.wav')
    """
    if not os.path.isdir(folder_path):
        print(f"[Warning] Folder not found: {folder_path}")
        return []
    all_files = os.listdir(folder_path)
    wavs = [f for f in all_files if f.lower().endswith(".wav")]
    return wavs


def load_position_dict(grammar, length, category):
    """
    从 generate_sequence_list.py 生成的 CSV 文件里加载 position 信息。
    假设 CSV 名称规则为: f"{grammar}_{category}_{length}.csv"
      - 每行格式: pattern, seqID, syll_1, ..., syll_n, position
    返回一个字典: { wav_filename: position_int, ... }
    注意:
      - 同一 wav 可能出现在多行，但大多数情况下, grammatical = position 0,
        ungrammatical 行可能是 -1, -2, -3, etc.
      - 如果同一 wav 出现在多行且 position 不同, 视为冲突；这里简单地后写覆盖前写。
    """
    csv_name = f"{grammar}_{category}_{length}.csv"
    csv_path = os.path.join(SEQUENCES_CSV_DIR, csv_name)
    if not os.path.isfile(csv_path):
        # 如果文件不存在，就返回一个空字典
        print(f"[Warning] CSV not found for {csv_name}, position will default to 0.")
        return {}

    pos_dict = {}
    with open(csv_path, 'r', newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        headers = next(reader, None)
        if not headers:
            return pos_dict

        # 找到 position 列的索引
        try:
            pos_idx = headers.index("position")
        except ValueError:
            # 没有 position 字段
            print(f"[Warning] 'position' column not found in {csv_name}.")
            return pos_dict

        # syllable 列可能是从第2列开始到 pos_idx-1
        # 但具体要根据前一个脚本 columns: pattern, seqID, syll_1, ..., syll_n, position
        # 我们简单地取 syll_i 列为 headers[2 : pos_idx]
        for row in reader:
            if len(row) < (pos_idx+1):
                print(f"[Debug] Skipped row because len(row)={len(row)}, pos_idx+1={pos_idx+1}")
                continue
            position_str = row[pos_idx].strip()
            # print(f"[Debug] read position='{position_str}' from row={row}")
            try:
                position_int = int(position_str)
            except ValueError:
                # 如果读不到整数，就当 0 处理
                position_int = 0
            print(f"[Debug] read position='{position_str}' as int={position_int}")
            
            pattern_str = row[0].strip()  # "A2A1B1B2"
            seq_id_str  = row[1].strip()  # e.g. "seq_0008"
            # 解析 seqID 里的数字部分
            if seq_id_str.startswith("seq_"):
                seq_num_str = seq_id_str[4:].lstrip("0")  # 如果想去掉前导 0
                if seq_num_str == "":
                    seq_num_str = "0"  # 万一是 "seq_0000"
            new_filename = f"{pattern_str}_{seq_num_str}.wav"
            pos_dict[new_filename] = position_int

            # # syllable filenames 在区间 [2, pos_idx)
            # for col_i in range(2, pos_idx):
            #     wav_name = row[col_i].strip()
            #     if wav_name:
            #         pos_dict[wav_name] = position_int

    return pos_dict


def save_csv(rows, out_file):
    """
    Writes a CSV with columns: trial_index, audio_filename, condition, position
    """
    fieldnames = ["trial_index", "audio_filename", "condition", "position"]
    with open(out_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)


def main():
    # For each grammar, produce 20 order CSV sets
    for grammar in GRAMMARS:
        for order_idx in range(1, N_ORDERS+1):
            # Set random seed => reproducible shuffle
            seed_val = sum(ord(ch) for ch in grammar) + 1000*order_idx
            random.seed(seed_val)

            session1_list = []
            session2_list = []

            # For each (length, category)
            for length in LENGTHS:
                for cat in CATEGORIES:
                    # subfolder name, e.g. "ADR_short_concatenation"
                    folder_name = f"{grammar}_{length}_{cat}"
                    folder_path = os.path.join(STIM_ROOT, folder_name)

                    # 1) 加载该 folder 对应的 position 字典
                    pos_dict = load_position_dict(grammar, length, cat)

                    # 2) 获取该文件夹内所有 wav 文件
                    wav_files = get_wav_list(folder_path)
                    needed_total = NEEDED_TOTAL.get((length, cat), 0)

                    if not wav_files or needed_total == 0:
                        # skip if none or not needed
                        continue

                    if len(wav_files) < needed_total:
                        print(f"[Error] {folder_name} has {len(wav_files)} wavs, need {needed_total}. Skipping.")
                        continue

                    # Shuffle full list, pick needed_total
                    random.shuffle(wav_files)
                    subset = wav_files[:needed_total]

                    # 在理想情况下，应该拆分一半给 session1，一半给 session2
                    # 但脚本目前只处理 session1。此处先保留原逻辑：
                    half = needed_total
                    session1_files = subset[:half]
                    # session2_files = subset[half:]  # 如果需要 session2，可启用

                    # Build condition label, e.g. "short_grammatical"
                    cond_label = f"{length}_{cat}"

                    # 相对路径: "ADR_short_concatenation/A1_e_b.wav"
                    session1_relpaths = [
                        os.path.join(folder_name, f).replace("\\", "/")
                        for f in session1_files
                    ]

                    # 填入 session1_list
                    for rp in session1_relpaths:
                        # 注意：pos_dict 存储的是纯文件名 -> position
                        # 这里 rp 是带有子文件夹的相对路径
                        # 我们先把纯文件名取出来，在字典里查 position
                        filename_only = os.path.basename(rp)
                        position_val = pos_dict.get(filename_only, 0)  # 默认 0
                        print(f"[Debug] WAV={filename_only}, pos_dict says position={position_val}")
                        session1_list.append((rp, cond_label, position_val))

                    # 如果要给 session2 分配，可自行在此添加类似逻辑：
                    # session2_relpaths = [
                    #     os.path.join(folder_name, f).replace("\\", "/")
                    #     for f in session2_files
                    # ]
                    # for rp in session2_relpaths:
                    #     filename_only = os.path.basename(rp)
                    #     position_val = pos_dict.get(filename_only, 0)
                    #     session2_list.append((rp, cond_label, position_val))

            # Shuffle final pool for session1 (and session2 if needed)
            random.shuffle(session1_list)
            # random.shuffle(session2_list)

            # Build row dicts for CSV
            session1_rows = []
            for i, (fname, cond, pos) in enumerate(session1_list, start=1):
                 # 在这儿打印一下
                print(f"[Debug] final (fname={fname}, cond={cond}, pos={pos})")
                row = {
                    "trial_index": i,
                    "audio_filename": fname,  # e.g. "ADR_short_concatenation/A1_e_b.wav"
                    "condition": cond,
                    "position": pos
                }
                session1_rows.append(row)

            # 如果需要 session2_rows:
            # session2_rows = []
            # for i, (fname, cond, pos) in enumerate(session2_list, start=1):
            #     row = {
            #         "trial_index": i,
            #         "audio_filename": fname,
            #         "condition": cond,
            #         "position": pos
            #     }
            #     session2_rows.append(row)

            # Save CSV for session1
            out_filename_1 = f"{grammar}_order{order_idx}_session1.csv"
            out_path_1 = os.path.join(OUTPUT_DIR, out_filename_1)
            save_csv(session1_rows, out_path_1)
            print(f"[Info] Created {out_filename_1} ({len(session1_rows)} lines)")

            # If needed, also save session2
            # out_filename_2 = f"{grammar}_order{order_idx}_session2.csv"
            # out_path_2 = os.path.join(OUTPUT_DIR, out_filename_2)
            # save_csv(session2_rows, out_path_2)
            # print(f"[Info] Created {out_filename_2} ({len(session2_rows)} lines)")


if __name__ == "__main__":
    main()
