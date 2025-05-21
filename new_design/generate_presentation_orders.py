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
        violations = violation_rows["pattern"].tolist()

        # 创建输出子目录
        folder_name = f"{category}{length}"
        folder_path = os.path.join(output_root, folder_name)
        os.makedirs(folder_path, exist_ok=True)

        for version in range(1, n_versions + 1):
            # 固定随机种子，确保每次顺序不同但可复现
            seed_val = sum(ord(c) for c in category) + int(length) + version * 100
            random.seed(seed_val)

            # Habituation 阶段
            habituation_trials = [{
                "trial_index": i + 1,
                "audio_filename": standard_wav,
                "condition": "habituation"
            } for i in range(habituation_n)]

            # Test 阶段：12 standard + 24 violations（平分）
            test_trials = []
            test_trials.extend([{
                "audio_filename": standard_wav,
                "condition": "test"
            }] * 12)

            repeat_each = 24 // len(violations)
            for pattern in violations:
                test_trials.extend([{
                    "audio_filename": f"{pattern}.wav",
                    "condition": "test"
                }] * repeat_each)

            # 打乱并编号
            random.shuffle(test_trials)
            for i, trial in enumerate(test_trials, start=habituation_n + 1):
                trial["trial_index"] = i

            # 合并全部 trial
            all_trials = habituation_trials + test_trials
            out_df = pd.DataFrame(all_trials)

            # 输出文件名，例如 Alte_session_1.csv
            base_filename = f"{category[:4]}{length}_session_{version}.csv"
            out_path = os.path.join(folder_path, base_filename)
            out_df.to_csv(out_path, index=False)

            print(f"[生成] {base_filename} → {folder_name}/")

# 示例调用
if __name__ == "__main__":
    generate_multiple_orders("sequences.csv")