import pandas as pd
import os
import random

def generate_multiple_orders(sequence_csv_path, output_root="presentation_orders", habituation_n=10, n_versions=10):
    # 加载 sequences.csv
    df = pd.read_csv(sequence_csv_path)

    # 分组处理每一个 category + length
    grouped = df.groupby(["category", "length"])

    for (category, length), group in grouped:
        group = group.copy()
        standard_row = group[group["position"] == 0]
        violation_rows = group[group["position"] != 0]

        if standard_row.empty or violation_rows.empty:
            print(f"[跳过] {category}{length} 缺失标准或violation pattern")
            continue

        standard_pattern = standard_row.iloc[0]["pattern"]
        standard_wav = f"{standard_pattern}.wav"
        standard_position = 0

        # violation pattern 与 position 映射
        violations = violation_rows[["pattern", "position"]].to_dict("records")

        # 创建输出子目录
        folder_name = f"{category}{length}"
        folder_path = os.path.join(output_root, folder_name)
        os.makedirs(folder_path, exist_ok=True)

        for version in range(1, n_versions + 1):
            seed_val = sum(ord(c) for c in category) + int(length) + version * 100
            random.seed(seed_val)

            # Habituation 阶段
            habituation_trials = [{
                "trial_index": i + 1,
                "audio_filename": standard_wav,
                "condition": "habituation",
                "position": standard_position
            } for i in range(habituation_n)]

            # Test 阶段：12 standard + 24 violations
            test_trials = []

            # 12 次 standard
            test_trials.extend([{
                "audio_filename": standard_wav,
                "condition": "standard",
                "position": standard_position
            }] * 12)

            # violation 平分到 24 次
            repeat_each = 24 // len(violations)
            for viol in violations:
                test_trials.extend([{
                    "audio_filename": f"{viol['pattern']}.wav",
                    "condition": "violation",
                    "position": viol["position"]
                }] * repeat_each)

            # 打乱并编号
            random.shuffle(test_trials)
            for i, trial in enumerate(test_trials, start=habituation_n + 1):
                trial["trial_index"] = i

            # 合并所有 trial
            all_trials = habituation_trials + test_trials
            out_df = pd.DataFrame(all_trials)

            # 输出文件名
            base_filename = f"{category[:4]}{length}_session_{version}.csv"
            out_path = os.path.join(folder_path, base_filename)
            out_df.to_csv(out_path, index=False)

            print(f"[生成] {base_filename} → {folder_name}/")

# 示例调用
if __name__ == "__main__":
    generate_multiple_orders("sequences.csv")