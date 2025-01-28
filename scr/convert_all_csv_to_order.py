#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
convert_all_csv_to_order.py

Batch process all CSV files in a folder that match the pattern:
  <grammar>_orderX_sessionY.csv
(e.g. "ADR_order6_session1.csv", "HDR_order2_session2.csv", etc.)

For each file, we create an order_X_partY.txt file where X=order, Y=session,
and convert each CSV row's 'audio_filename' column into the final line format:

  _audio_{basename}.png, 1.0, 1.0, 5, 0.05, , , , {wav_filename}

Usage:
  python convert_all_csv_to_order.py --input-dir path/to/csv_folder --output-dir path/to/txt_folder

Example:
  Suppose the script sees "ADR_order6_session1.csv". It will parse out order=6, session=1,
  and generate "order_6_part1.txt" with the lines from CSV.
"""

import os
import re
import csv
import argparse

# Format for final line:
#   _audio_{base}.png, 1.0, 1.0, 5, 0.05, , , , {wav_file}
# We'll define constant strings for columns that never change
COL2 = " "
COL3 = " "
COL4 = " "
COL5 = " "
EMPTY_COLS = 3  # number of empty columns

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", "-i", required=True, help="Folder containing the CSV files from create_order.py")
    parser.add_argument("--output-dir","-o", required=True, help="Folder to save the .txt order files")
    args = parser.parse_args()

    input_dir = args.input_dir
    output_dir = args.output_dir

    if not os.path.isdir(input_dir):
        print(f"[Error] input_dir not found: {input_dir}")
        return
    os.makedirs(output_dir, exist_ok=True)

    # We'll look for CSV files matching the pattern: <grammar>_order(\d+)_session(\d+).csv
    # e.g. ADR_order6_session1.csv => order=6, session=1
    pattern = re.compile(r"^[A-Za-z]+_order(\d+)_session(\d+)\.csv$")

    all_files = os.listdir(input_dir)
    csv_files = [f for f in all_files if f.lower().endswith(".csv")]

    for csv_filename in csv_files:
        match = pattern.match(csv_filename)
        if not match:
            # skip files that don't match the naming pattern
            continue

        order_no = match.group(1)   # e.g. "6"
        session_no = match.group(2) # e.g. "1"

        # Build output filename, e.g. "order_6_part1.txt"
        out_txt_name = f"order_{order_no}_part{session_no}.txt"

        input_csv_path = os.path.join(input_dir, csv_filename)
        output_txt_path = os.path.join(output_dir, out_txt_name)

        convert_csv_to_order_file(input_csv_path, output_txt_path)

        print(f"[Info] Created {out_txt_name} from {csv_filename}")

def convert_csv_to_order_file(csv_path, txt_path):
    """
    Read CSV with a 'audio_filename' column, produce lines in the final .txt:
      _audio_{base}.png, 1.0, 1.0, 5, 0.05, , , , {wav_file}
    """
    with open(csv_path, 'r', encoding='utf-8') as f_in, open(txt_path, 'w', encoding='utf-8') as f_out:
        reader = csv.DictReader(f_in)

        for row in reader:
            wav_file = row.get("audio_filename","").strip()
            if not wav_file:
                continue
            
            base_name, ext = os.path.splitext(wav_file)
            # Build columns
            # e.g. [f"_audio_{base_name}.png", "1.0", "1.0", "5", "0.05", "", "", "", wav_file]
            # then join with ", "
            # columns = [f"_audio_{base_name}.png", COL2, COL3, COL4, COL5]
            columns = [COL2, COL2, COL3, COL4, COL5]
            # add empty columns
            for _ in range(EMPTY_COLS):
                columns.append("")
            columns.append(wav_file)

            line_str = ", ".join(columns)
            f_out.write(line_str + "\n")

if __name__ == "__main__":
    main()
