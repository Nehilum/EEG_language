import pandas as pd

def find_single_difference_position(std, viol):
    """返回唯一不同位置的索引，如果不唯一或无效则返回 None。"""
    if isinstance(viol, str) and viol.lower() != "xxx":
        differences = [i for i, (a, b) in enumerate(zip(std, viol)) if a != b]
        return differences if len(differences) == 1 else None
    return None

def generate_sequence_csv(input_excel_path, output_csv_path):
    # 1. 读取 Excel 并标准化列名
    df = pd.read_excel(input_excel_path)
    if 'Sequence' in df.columns:
        df.rename(columns={'Sequence': 'Standard'}, inplace=True)

    viol_columns = ['Violation type 1', 'Violation type 2', 'Violation type 3', 'Violation type 4']
    output_rows = []
    seq_counter = 1

    for _, row in df.iterrows():
        std = row['Standard']
        category = row['Category']
        length = row['Length']

        # 忽略空或非法的标准行
        if not isinstance(std, str) or std.lower() == 'xxx':
            continue

        # 添加标准 pattern
        output_rows.append({
            "pattern": std,
            "seqID": f"seq_{seq_counter:04d}",
            "category": category,
            "length": length,
            "position": 0
        })
        seq_counter += 1

        # 添加合法的 violation pattern
        for col in viol_columns:
            viol = row[col]
            diff_pos = find_single_difference_position(std, viol)
            if diff_pos:
                output_rows.append({
                    "pattern": viol,
                    "seqID": f"seq_{seq_counter:04d}",
                    "category": category,
                    "length": length,
                    "position": diff_pos[0] + 1  # 改动位置从 1 开始
                })
                seq_counter += 1

    # 写入 CSV
    out_df = pd.DataFrame(output_rows)
    out_df.to_csv(output_csv_path, index=False, encoding='utf-8')
    print(f"✔️ Generated {output_csv_path} with {len(out_df)} rows.")

# 示例调用
if __name__ == "__main__":
    generate_sequence_csv("sequences.xlsx", "sequences.csv")