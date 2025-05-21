import os
import pandas as pd
from pydub import AudioSegment

# 配置参数
TONE_FOLDER = "stimuli/raw_tones"
OUTPUT_FOLDER = "stimuli/generated_sequences"
ISI_MS = 250  # 两个tone之间的间隔时间（毫秒）
TARGET_SR = 48000  # 输出采样率

def generate_audio_from_pattern(pattern, output_path):
    combined = AudioSegment.silent(duration=0)
    for symbol in pattern:
        tone_file = os.path.join(TONE_FOLDER, f"{symbol}.wav")
        if not os.path.exists(tone_file):
            print(f"[警告] 文件未找到：{tone_file}")
            return
        tone = AudioSegment.from_wav(tone_file)
        tone = tone.set_frame_rate(TARGET_SR)
        combined += tone + AudioSegment.silent(duration=ISI_MS)

    combined.export(output_path, format="wav")
    print(f"[生成] {output_path}")

def main():
    os.makedirs(OUTPUT_FOLDER, exist_ok=True)
    df = pd.read_csv("sequences.csv")

    for _, row in df.iterrows():
        pattern = row['pattern']
        filename = f"{pattern}.wav"
        out_path = os.path.join(OUTPUT_FOLDER, filename)

        generate_audio_from_pattern(pattern, out_path)

if __name__ == "__main__":
    main()