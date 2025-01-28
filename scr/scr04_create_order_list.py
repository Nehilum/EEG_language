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

We have 12 categories of folders:
  grammar in [ADR, HDR]
  length in [short, long]
  type in [grammatical, replacement, concatenation]
so total 12 folder names, e.g. "ADR_long_concatenation".

According to your plan:
- short_grammatical: 96 total -> session1=48, session2=48
- long_grammatical: 384 total -> session1=192, session2=192
- short_(replacement|concatenation): each ~24 total -> session1=12, session2=12
- long_(replacement|concatenation): each ~96 total -> session1=48, session2=48

We read all .wav in each folder, shuffle, then the first half goes to session1,
the second half goes to session2. Then we combine short/long & gram/violation
for session1 into a big list, shuffle, and write CSV. Similarly for session2.

Crucial update:
Instead of storing just the file name like "A1_e_b.wav", we store the subfolder
path as well, e.g. "ADR_short_concatenation/A1_e_b.wav" in the CSV. 
This way, later scripts can locate the correct subfolder for the audio.

The resulting CSV columns:
    trial_index, audio_filename, condition
Where 'condition' might be 'short_gram', 'short_replacement', etc.

2023-08, revised to store subfolder in audio_filename.
"""

import os
import csv
import random

# ========================== CONFIG ==========================
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(SCRIPT_DIR)

# Root folder that contains subfolders like "ADR_short_grammatical",
# "HDR_long_concatenation", etc. These subfolders hold .wav audio.
STIM_ROOT = os.path.join(PARENT_DIR, "stimuli", "combined_wav")

# We'll produce 20 random orders per grammar
N_ORDERS = 20

# Where to save the final CSVs
OUTPUT_DIR = os.path.join(PARENT_DIR, "stimuli", "order_lists")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Grammar list
GRAMMARS = ["ADR","HDR"]

# We'll define the subfolder name pattern as: f"{grammar}_{length}_{category}"
# length in [short, long]; category in [grammatical, replacement, concatenation]
LENGTHS = ["short","long"]
CATEGORIES = ["grammatical","replacement","concatenation"]

# The total expected counts for each (length, category).
# Then we split half for session1, half for session2.
# E.g. short_grammatical -> 96 total => session1=48, session2=48
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

def save_csv(rows, out_file):
    """
    Writes a CSV with columns: trial_index, audio_filename, condition
    """
    fieldnames = ["trial_index","audio_filename","condition"]
    with open(out_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for r in rows:
            writer.writerow(r)

def main():
    # For each grammar, produce 20 order CSV sets
    for grammar in GRAMMARS:
        for order_idx in range(1, N_ORDERS+1):
            # Set random seed => reproducible
            seed_val = sum(ord(ch) for ch in grammar) + 1000*order_idx
            random.seed(seed_val)

            # We'll store session1 & session2 items in lists: (audio_path, condition)
            session1_list = []
            session2_list = []

            # Iterate over each (length, category) pair
            for length in LENGTHS:
                for cat in CATEGORIES:
                    # subfolder name, e.g. "ADR_short_concatenation"
                    folder_name = f"{grammar}_{length}_{cat}"
                    folder_path = os.path.join(STIM_ROOT, folder_name)

                    # Gather all .wav (filenames)
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

                    # Now split half for session1, half for session2
                    half = needed_total // 2
                    session1_files = subset[:half]
                    session2_files = subset[half:]

                    # Build condition label, e.g. "short_gram" or "long_concatenation"
                    cond_label = f"{length}_{cat}"

                    # The key difference: store "folder_name/filename.wav" in 'audio_filename'
                    # so scripts can find them in subsequent steps
                    # We can use forward slash to unify:
                    session1_relpaths = [os.path.join(folder_name, f).replace("\\","/") for f in session1_files]
                    session2_relpaths = [os.path.join(folder_name, f).replace("\\","/") for f in session2_files]

                    # Add them to session lists
                    session1_list.extend((rp, cond_label) for rp in session1_relpaths)
                    session2_list.extend((rp, cond_label) for rp in session2_relpaths)

            # Shuffle final pool for each session
            random.shuffle(session1_list)
            random.shuffle(session2_list)

            # Build row dicts for CSV
            session1_rows = []
            for i, (fname, cond) in enumerate(session1_list, start=1):
                row = {
                    "trial_index": i,
                    "audio_filename": fname,  # e.g. "ADR_short_concatenation/A1_e_b.wav"
                    "condition": cond
                }
                session1_rows.append(row)

            session2_rows = []
            for i, (fname, cond) in enumerate(session2_list, start=1):
                row = {
                    "trial_index": i,
                    "audio_filename": fname,
                    "condition": cond
                }
                session2_rows.append(row)

            # Save CSV, e.g. "ADR_order1_session1.csv"
            out_filename_1 = f"{grammar}_order{order_idx}_session1.csv"
            out_filename_2 = f"{grammar}_order{order_idx}_session2.csv"
            out_path_1 = os.path.join(OUTPUT_DIR, out_filename_1)
            out_path_2 = os.path.join(OUTPUT_DIR, out_filename_2)

            save_csv(session1_rows, out_path_1)
            save_csv(session2_rows, out_path_2)

            print(f"[Info] Created {out_filename_1} ({len(session1_rows)} lines), "
                  f"{out_filename_2} ({len(session2_rows)} lines).")


if __name__ == "__main__":
    main()
