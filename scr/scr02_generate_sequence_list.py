#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
generate_sequence_list.py

This script generates 12 CSV files under 'sequences_csv/':

  (1)  ADR_grammatical_short.csv
  (2)  ADR_replacement_short.csv
  (3)  ADR_concatenation_short.csv
  (4)  ADR_grammatical_long.csv
  (5)  ADR_replacement_long.csv
  (6)  ADR_concatenation_long.csv
  (7)  HDR_grammatical_short.csv
  (8)  HDR_replacement_short.csv
  (9)  HDR_concatenation_short.csv
  (10) HDR_grammatical_long.csv
  (11) HDR_replacement_long.csv
  (12) HDR_concatenation_long.csv

Grammar types: 'ADR' or 'HDR'
Sequence lengths: 'short' (4 syllables) or 'long' (6 syllables)
Violation types: 'replacement' or 'concatenation'

Each CSV row contains:
  pattern, seqID, syll_1, syll_2, ..., syll_n

Where:
  - 'pattern' is a string like "A1A2B2B1"
  - 'seqID' is an auto-assigned index
  - 'syll_i' are .wav filenames (e.g. A1_e_b.wav)
"""

import os
import csv
import itertools
import random

# ---------------------------------------------------------
# 1) Define sub-class mappings and vowels
# ---------------------------------------------------------
A_CONSONANTS = {'A1': 'b', 'A2': 'd', 'A3': 'g'}
B_CONSONANTS = {'B1': 'p', 'B2': 't', 'B3': 'k'}

A_VOWELS = ['e', 'i']
B_VOWELS = ['o', 'u']

def create_filename(sub_label: str, vowel: str) -> str:
    """
    E.g. sub_label='A1', vowel='e' -> 'A1_e_b.wav'
    """
    if sub_label.startswith('A'):
        consonant = A_CONSONANTS[sub_label]
    else:
        consonant = B_CONSONANTS[sub_label]
    return f"{sub_label}_{vowel}_{consonant}.wav"


# ---------------------------------------------------------
# 2) Define permutations for short(4) and long(6) sequences (Bahlmann 2008)
# ---------------------------------------------------------
HIERARCHICAL_SHORT_PATTERNS = [
    ('A1','A2','B2','B1'),
    ('A2','A1','B1','B2'),
    ('A1','A3','B3','B1'),
    ('A3','A1','B1','B3'),
    ('A2','A3','B3','B2'),
    ('A3','A2','B2','B3')
]
HIERARCHICAL_LONG_PATTERNS = [
    ('A1','A2','A3','B3','B2','B1'),
    ('A2','A3','A1','B1','B3','B2'),
    ('A3','A1','A2','B2','B1','B3'),
    ('A2','A1','A3','B3','B1','B2'),
    ('A1','A3','A2','B2','B3','B1'),
    ('A3','A2','A1','B1','B2','B3')
]
ADJACENT_SHORT_PATTERNS = [
    ('A1','B1','A2','B2'),
    ('A2','B2','A1','B1'),
    ('A1','B1','A3','B3'),
    ('A3','B3','A1','B1'),
    ('A2','B2','A3','B3'),
    ('A3','B3','A2','B2')
]
ADJACENT_LONG_PATTERNS = [
    ('A1','B1','A2','B2','A3','B3'),
    ('A1','B1','A3','B3','A2','B2'),
    ('A2','B2','A1','B1','A3','B3'),
    ('A2','B2','A3','B3','A1','B1'),
    ('A3','B3','A1','B1','A2','B2'),
    ('A3','B3','A2','B2','A1','B1')
]

# ---------------------------------------------------------
# 3) Generate GRAMMATICAL sequences with pattern label
# ---------------------------------------------------------
def generate_grammatical_sequences(grammar: str, seq_length: str):
    """
    Returns a list of tuples: [(patternStr, [syllFile1, syllFile2, ...]), ...]
    """
    if grammar=='HDR' and seq_length=='short':
        patterns = HIERARCHICAL_SHORT_PATTERNS
    elif grammar=='HDR' and seq_length=='long':
        patterns = HIERARCHICAL_LONG_PATTERNS
    elif grammar=='ADR' and seq_length=='short':
        patterns = ADJACENT_SHORT_PATTERNS
    else:
        patterns = ADJACENT_LONG_PATTERNS
    
    results = []
    for pattern_tuple in patterns:
        # pattern_tuple example: ('A1','A2','B2','B1')
        # convert to string e.g. "A1A2B2B1"
        pattern_str = "".join(pattern_tuple)

        a_indices = [i for i, x in enumerate(pattern_tuple) if x.startswith('A')]
        b_indices = [i for i, x in enumerate(pattern_tuple) if x.startswith('B')]

        for a_combo in itertools.product(A_VOWELS, repeat=len(a_indices)):
            for b_combo in itertools.product(B_VOWELS, repeat=len(b_indices)):
                seq = [None]*len(pattern_tuple)
                # Fill A positions
                for idx_a, vow in zip(a_indices, a_combo):
                    seq[idx_a] = create_filename(pattern_tuple[idx_a], vow)
                # Fill B positions
                for idx_b, vow in zip(b_indices, b_combo):
                    seq[idx_b] = create_filename(pattern_tuple[idx_b], vow)

                results.append((pattern_str, seq))

    return results

# ---------------------------------------------------------
# 4) Generate UNGRAMMATICAL sequences
#    returns list of (patternStr, [filename1, filename2, ...])
# ---------------------------------------------------------
def generate_ungrammatical_sequences(grammar: str, seq_length: str, violation_type: str, sample_size=50):
    """
    Minimal random generation of ungrammatical sequences.
    We use the same patternStr from the original grammar pattern, but we break 1 position
    in the tail to produce violation.
    """
    # Start from grammatical
    gram_list = generate_grammatical_sequences(grammar, seq_length)
    if not gram_list:
        return []

    base_samples = random.sample(gram_list, min(sample_size, len(gram_list)))
    results = []

    # short => tail pos in [-2, -1], long => [-3, -2, -1]
    if seq_length=='short':
        tail_positions = [-2, -1]
    else:
        tail_positions = [-3, -2, -1]

    for (pattern_str, seq) in base_samples:
        seq_copy = seq[:]
        pos = random.choice(tail_positions)
        old_filename = seq_copy[pos]

        # parse e.g. "A1_e_b.wav" -> ["A1","e","b"]
        no_ext = old_filename[:-4]  # remove ".wav"
        parts = no_ext.split('_')  # e.g. ['A1','e','b']

        if violation_type=='replacement':
            # A->B or B->A
            if parts[0].startswith('A'):
                from . import B_CONSONANTS, B_VOWELS  # or use global
                new_sub = random.choice(list(B_CONSONANTS.keys()))
                new_vow = random.choice(B_VOWELS)
                seq_copy[pos] = create_filename(new_sub, new_vow)
            else:
                from . import A_CONSONANTS, A_VOWELS
                new_sub = random.choice(list(A_CONSONANTS.keys()))
                new_vow = random.choice(A_VOWELS)
                seq_copy[pos] = create_filename(new_sub, new_vow)

        elif violation_type=='concatenation':
            # keep same A/B category but different sub
            if parts[0].startswith('A'):
                from . import A_CONSONANTS, A_VOWELS
                old_sub = parts[0]
                possible_subs = ['A1','A2','A3']
                possible_subs.remove(old_sub)
                new_sub = random.choice(possible_subs)
                new_vow = random.choice(A_VOWELS)
                seq_copy[pos] = create_filename(new_sub, new_vow)
            else:
                from . import B_CONSONANTS, B_VOWELS
                old_sub = parts[0]
                possible_subs = ['B1','B2','B3']
                possible_subs.remove(old_sub)
                new_sub = random.choice(possible_subs)
                new_vow = random.choice(B_VOWELS)
                seq_copy[pos] = create_filename(new_sub, new_vow)

        # We might keep patternStr the same, or add e.g. "*v" to denote it's violated.
        # For clarity, let's do patternStr + "_X" to indicate ungrammatical:
        # or just keep it the same. I'll keep the same for now, or you could do:
        # pattern_str = pattern_str + "Viol"
        results.append((pattern_str, seq_copy))

    return results


# ---------------------------------------------------------
# 5) Save to CSV with pattern column
# ---------------------------------------------------------
def save_sequences_to_csv(csv_filename, data):
    """
    data: list of (patternStr, [filename1, filename2, ...])

    We'll produce CSV columns:
      pattern, seqID, syll_1, ..., syll_n
    """
    current_dir = os.getcwd()
    parent_dir = os.path.dirname(current_dir)
    out_folder = os.path.join(parent_dir, "stimuli", "sequences_csv")
    os.makedirs(out_folder, exist_ok=True)

    outpath = os.path.join(out_folder, csv_filename)
    if not data:
        with open(outpath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["pattern","seqID","syll_1","syll_2","syll_3","syll_4_or_more..."])
        return

    # check max length
    max_syll_len = max(len(seq) for (_, seq) in data)
    headers = ["pattern", "seqID"] + [f"syll_{i+1}" for i in range(max_syll_len)]

    with open(outpath, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)

        for idx, (pattern_str, seq_list) in enumerate(data):
            row = [pattern_str, f"seq_{idx:04d}"] + seq_list
            writer.writerow(row)


# ---------------------------------------------------------
# 6) Main: generate 12 CSV
# ---------------------------------------------------------
def main():
    random.seed(42)  # reproducible

    grammars = ['ADR','HDR']
    lengths = ['short','long']
    violation_types = ['replacement','concatenation']

    for g in grammars:
        for l in lengths:
            # A) Grammatical
            gramm_data = generate_grammatical_sequences(g, l)
            fname_g = f"{g}_grammatical_{l}.csv"
            save_sequences_to_csv(fname_g, gramm_data)

            # B) Ungrammatical
            for v in violation_types:
                ungram_data = generate_ungrammatical_sequences(g, l, v, sample_size=50)
                fname_u = f"{g}_{v}_{l}.csv"
                save_sequences_to_csv(fname_u, ungram_data)

    print("All CSV (12 types) have been saved under 'stimuli/sequences_csv'.")


if __name__ == "__main__":
    main()
