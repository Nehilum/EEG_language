import os
import numpy as np
import librosa
import soundfile as sf

def manual_trim_audio(input_folder, output_folder, start_time=0.08, end_time=0.48):
    """
    手动设定裁剪起点和终点，批量处理音频文件
    :param input_folder: 原始音频文件夹
    :param output_folder: 裁剪后音频文件夹
    :param start_time: 开始时间 (单位: 秒)
    :param end_time: 结束时间 (单位: 秒)
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    audio_files = [f for f in os.listdir(input_folder) if f.endswith('.wav')]

    for file in audio_files:
        filepath = os.path.join(input_folder, file)
        y, sr = librosa.load(filepath, sr=None)  # 读取音频
        
        # 计算裁剪的样本索引
        start_sample = int(start_time * sr)
        end_sample = int(end_time * sr)

        # 裁剪音频
        y_trimmed = y[start_sample:end_sample]

        # 确保所有音频长度一致
        target_length = end_sample - start_sample
        if len(y_trimmed) < target_length:
            padding = target_length - len(y_trimmed)
            y_trimmed = np.pad(y_trimmed, (0, padding), mode='constant')

        # 保存裁剪后的音频
        output_path = os.path.join(output_folder, file)
        sf.write(output_path, y_trimmed, sr)
        print(f"✅ 裁剪完成: {file} -> {output_path} ({start_time}s - {end_time}s)")

    print("🎉 所有音频裁剪完毕！")

# === 运行脚本 ===
current_dir = os.path.dirname(os.path.abspath(__file__))
input_folder = os.path.join(current_dir, "processed", "processed_syllables")
output_folder = os.path.join(current_dir, "processed", "final_trimmed_syllables")
manual_trim_audio(input_folder, output_folder, start_time=0.08, end_time=0.48)
