#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
generate_sequence.py

Concatenate single-syllable .wav files into a combined .wav for each sequence.

Project structure assumption:
  my_project/
   ├─ scr/
   │   └─ generate_sequence.py
   ├─ stimuli/
   │   ├─ syllables_renamed/     (e.g., A1_e_b.wav, B2_u_t.wav, etc.)
   │   ├─ sequences_csv/         (e.g., ADR_grammatical_short.csv, etc.)
   │   └─ combined_wav/          (output folder for final combined .wav)

Usage:
  1) Place this file in `scr/`.
  2) Run `python generate_sequence.py`.
  3) It will read multiple CSVs from stimuli/sequences_csv (ADR/HDR + short/long + grammatical/replacement/concatenation),
     and combine all sequences into .wav files under stimuli/combined_wav/.
"""

import os
import csv
from pydub import AudioSegment

def generate_sequence_wav(seq_id, syllable_files, output_dir, ISI_MS=100, target_sr=48000):
    """
    Merge multiple single-syllable .wav files (with same audio params)
    into one .wav file for the given seq_id.
    """
    os.makedirs(output_dir, exist_ok=True)
    combined = AudioSegment.empty()

    for f in syllable_files:
        audio_path = os.path.join(SYLLABLES_PATH, f)
        if not os.path.isfile(audio_path):
            print(f"[Warning] File not found: {audio_path}, skipping.")
            continue

        segment = AudioSegment.from_wav(audio_path)
        
        # Ensure consistent sampling rate
        segment = segment.set_frame_rate(target_sr)

        # Add segment and insert ISI silence
        combined += segment + AudioSegment.silent(duration=ISI_MS)

    out_wav_path = os.path.join(output_dir, f"{seq_id}.wav")
    combined.export(out_wav_path, format="wav")
    return out_wav_path


def process_csv_file(csv_path, output_subdir, limit_count=None):
    """
    Read `csv_path`, for each row gather syllable filenames, then call `generate_sequence_wav`
    to produce a combined .wav in `output_subdir`.

    :param csv_path: full path to a .csv file (e.g. 'ADR_grammatical_short.csv')
    :param output_subdir: folder to place final .wav
    :param limit_count: if not None, limit how many rows to process
    """
    if not os.path.isfile(csv_path):
        print(f"[Warning] CSV file not found: {csv_path}, skipping.")
        return

    os.makedirs(output_subdir, exist_ok=True)

    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for idx, row in enumerate(reader):
            if limit_count is not None and idx >= limit_count:
                break
            seq_id = row["seqID"]
            syllables = [row[col] for col in row if col.startswith("syll_")]

            if 'pattern' not in row:
                print("[Error] CSV must have a 'pattern' column.")
                continue

            pattern = row['pattern']  # e.g. "A1A2B2B1"

            # 2) Gather all syllable filenames
            # e.g. 'syll_1', 'syll_2', ...
            # to build absolute paths
            syll_files = []
            for k in row:
                if k.startswith("syll_"):
                    wav_name = row[k]  # e.g. "A1_e_b.wav"
                    if wav_name:       # skip empty columns
                        full_path = os.path.join(SYLLABLES_PATH, wav_name)
                        if not os.path.isfile(full_path):
                            print(f"[Warning] File not found: {full_path}. Skipping.")
                            continue
                        syll_files.append(full_path)

            # 3) Output file naming: pattern_index.wav
            out_filename = f"{pattern}_{idx}"  
            
            out_path = generate_sequence_wav(out_filename, syllables, output_subdir)
            print(f"Combined -> {out_path}")


# ----------------------------------------------------------------------------------------
# MAIN SCRIPT
# ----------------------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(SCRIPT_DIR)

SEQUENCES_CSV_DIR = os.path.join(PARENT_DIR, "stimuli", "sequences", "sequences_csv")
SYLLABLES_PATH    = os.path.join(PARENT_DIR, "stimuli", "processed", "stim_syllables_mono")
COMBINED_WAV_DIR  = os.path.join(PARENT_DIR, "stimuli", "sequences","combined_wav_mono")

def main():
    grammars = ['ADR','HDR']
    lengths = ['short','long']
    violation_types = ['replacement','concatenation']

    # 先处理 grammatical
    for g in grammars:
        for l in lengths:
            csv_filename = f"{g}_grammatical_{l}.csv"
            csv_path = os.path.join(SEQUENCES_CSV_DIR, csv_filename)
            # 输出文件夹: stimuli/combined_wav/ e.g. "ADR_short_grammatical"
            out_subdir = os.path.join(COMBINED_WAV_DIR, f"{g}_{l}_grammatical")
            # 调用函数
            process_csv_file(csv_path, out_subdir, limit_count=None)

    # 再处理 ungrammatical
    for g in grammars:
        for l in lengths:
            for vtype in violation_types:
                csv_filename = f"{g}_{vtype}_{l}.csv"
                csv_path = os.path.join(SEQUENCES_CSV_DIR, csv_filename)
                # 输出文件夹: e.g. stimuli/combined_wav/ADR_short_replacement
                out_subdir = os.path.join(COMBINED_WAV_DIR, f"{g}_{l}_{vtype}")
                process_csv_file(csv_path, out_subdir, limit_count=None)

if __name__=="__main__":
    main()
