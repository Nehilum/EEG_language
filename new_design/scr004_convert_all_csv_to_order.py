import os
import re
import csv

# 常量列值
COL2 = " "
COL3 = " "
COL4 = " 4.0"
COL5 = " 0.05"
EMPTY_COLS = 3  # 空列数量

# 输入输出路径定义
INPUT_ROOT = "presentation_orders"
OUTPUT_ROOT = "order_list"

def convert_csv_to_order_file(csv_path, txt_path):
    """
    将 CSV 文件中的每一行转换成最终格式，写入 txt 文件
    """
    with open(csv_path, 'r', encoding='utf-8') as f_in, open(txt_path, 'w', encoding='utf-8') as f_out:
        reader = csv.DictReader(f_in)
        for row in reader:
            wav_file = row.get("audio_filename", "").strip()
            if not wav_file:
                continue
            base_name, _ = os.path.splitext(wav_file)
            columns = [COL2, COL2, COL3, COL4, COL5]
            columns.extend([""] * EMPTY_COLS)
            columns.append(wav_file)
            line_str = ", ".join(columns)
            f_out.write(line_str + "\n")

def process_all_csv_files(input_dir, output_dir):
    """
    遍历输入目录的所有子文件夹和子文件，生成对应 txt 文件到输出目录结构中
    """
    for root, dirs, files in os.walk(input_dir):
        for file in files:
            if not file.lower().endswith(".csv"):
                continue

            csv_path = os.path.join(root, file)

            # 获取当前子文件夹名作为结构依据
            rel_dir = os.path.relpath(root, input_dir)
            output_subdir = os.path.join(output_dir, rel_dir)
            os.makedirs(output_subdir, exist_ok=True)

            # 提取 session 编号（如 Alte_session_3 → 3）
            session_match = re.search(r"_session_(\d+)", file)
            if not session_match:
                print(f"[跳过] 无法解析 session 编号: {file}")
                continue

            session_num = session_match.group(1)
            out_filename = f"order_{session_num}_part1.txt"
            out_path = os.path.join(output_subdir, out_filename)

            convert_csv_to_order_file(csv_path, out_path)
            print(f"[完成] {file} → {out_path}")

if __name__ == "__main__":
    process_all_csv_files(INPUT_ROOT, OUTPUT_ROOT)