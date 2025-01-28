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
the second half goes to session2. Then we combine (short_gram + short_repl + short_conc + long_gram + long_repl + long_conc)
for session1 into a big list, shuffle, and write CSV. Similarly for session2.

The resulting CSV columns:
    trial_index, audio_filename, condition
Where 'condition' might be 'short_gram', 'short_replacement', etc., to track which type of stimulus it is.

You can interpret how to use these in your final experiment.
"""

import os
import csv
import random

# ========================== CONFIG ==========================
# Root folder that contains subfolders like "ADR_short_grammatical", "HDR_long_concatenation", etc.
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PARENT_DIR = os.path.dirname(SCRIPT_DIR)

STIM_ROOT = os.path.join(PARENT_DIR, "stimuli", "combined_wav")

# We'll produce 20 random orders per grammar
N_ORDERS = 20

# Where to save the final CSVs
OUTPUT_DIR = os.path.join(PARENT_DIR, "stimuli", "order_lists")
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Grammar list
GRAMMARS = ["ADR","HDR"]

# We'll define the subfolder name pattern as: f"{grammar}_{length}_{category}"
# length in [short, long]
# category in [grammatical, replacement, concatenation]
LENGTHS = ["short","long"]
CATEGORIES = ["grammatical","replacement","concatenation"]

# The total expected counts for each (length, category).
# We'll read the entire folder, but we only need e.g. 96 for short_gram, etc.
# Then we split half for session1, half for session2.
# Example:
#   short_grammatical -> 96 (session1=48, session2=48)
#   long_grammatical  -> 384 (session1=192, session2=192)
#   short_replacement -> 24 (session1=12, session2=12)
#   short_concatenation -> 24 ...
#   long_replacement -> 96 ...
#   long_concatenation -> 96 ...
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
    """
    if not os.path.isdir(folder_path):
        print(f"[Warning] Folder not found: {folder_path}")
        return []
    all_files = os.listdir(folder_path)
    wavs = [f for f in all_files if f.lower().endswith(".wav")]
    return wavs

def main():
    # For each grammar, we do 20 orders
    for grammar in GRAMMARS:
        for order_idx in range(1, N_ORDERS+1):
            # Set random seed => reproducible
            # e.g. seed grammar name + order_idx
            # Convert grammar to e.g. an integer offset, or just do a custom formula
            # Here let's do sum of ASCII plus order_idx
            seed_val = sum(ord(ch) for ch in grammar) + 1000*order_idx
            random.seed(seed_val)

            # We'll store session1 items & session2 items in lists of (file, condition)
            session1_list = []
            session2_list = []

            # We iterate over each (length, category) pair
            for length in LENGTHS:
                for cat in CATEGORIES:
                    # Build subfolder name, e.g. "ADR_short_concatenation"
                    folder_name = f"{grammar}_{length}_{cat}"
                    folder_path = os.path.join(STIM_ROOT, folder_name)

                    # Read all wav files
                    wav_files = get_wav_list(folder_path)
                    needed_total = NEEDED_TOTAL.get((length, cat), 0)

                    if not wav_files or needed_total == 0:
                        # If category doesn't exist or we set 0, skip
                        continue

                    # Check if we have enough
                    if len(wav_files) < needed_total:
                        print(f"[Error] {folder_name} only has {len(wav_files)}, but need {needed_total}.")
                        continue

                    # Shuffle
                    random.shuffle(wav_files)

                    # We'll take the first 'needed_total' from the shuffled list
                    subset = wav_files[:needed_total]

                    # Now split half for session1, half for session2
                    half = needed_total // 2
                    session1_files = subset[:half]
                    session2_files = subset[half:]

                    # Condition label
                    # e.g. "short_gram", "short_replacement", "long_conc", etc.
                    cond_label = f"{length}_{cat}"

                    # Add them to each session's list
                    # We'll store (audio_filename, cond_label)
                    session1_list.extend((f, cond_label) for f in session1_files)
                    session2_list.extend((f, cond_label) for f in session2_files)

            # Now we shuffle each session's final pool
            random.shuffle(session1_list)
            random.shuffle(session2_list)

            # Build row dicts
            session1_rows = []
            for i, (fname, cond) in enumerate(session1_list, start=1):
                row = {
                    "trial_index": i,
                    "audio_filename": fname,
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

            # Save CSV
            # e.g. "ADR_order1_session1.csv" ...
            out_filename_1 = f"{grammar}_order{order_idx}_session1.csv"
            out_filename_2 = f"{grammar}_order{order_idx}_session2.csv"

            out_path_1 = os.path.join(OUTPUT_DIR, out_filename_1)
            out_path_2 = os.path.join(OUTPUT_DIR, out_filename_2)

            save_csv(session1_rows, out_path_1)
            save_csv(session2_rows, out_path_2)

            print(f"[Info] Created {out_filename_1} with {len(session1_rows)} lines, {out_filename_2} with {len(session2_rows)} lines.")


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


if __name__=="__main__":
    main()
