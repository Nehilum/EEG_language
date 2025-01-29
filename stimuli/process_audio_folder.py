import os
import numpy as np
import librosa
import librosa.display
import soundfile as sf

def find_high_energy_onset(y, sr, threshold_ratio=0.4):
    """
    使用 RMS 能量检测 syllable 主要能量的起始时间
    - 计算短时 RMS 能量
    - 选择高于最大能量 * threshold_ratio（默认 40%）的第一个点作为起点
    """
    rms = librosa.feature.rms(y=y)[0]  # 计算 RMS 能量
    max_rms = np.max(rms)  # 找到最大能量
    onset_frame = np.argmax(rms > max_rms * threshold_ratio)  # 找到第一个超过阈值的帧
    onset_time = librosa.frames_to_time(onset_frame, sr=sr)  # 转换为时间
    return onset_time

def process_audio_folder(input_folder, output_folder, target_length=0.6):
    """
    - 使用 RMS 能量对齐 syllable 主能量部分
    - 统一 syllable 长度，确保 ERP 事件时间锁定
    """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    onset_times = []
    actual_durations = []
    
    audio_files = [f for f in os.listdir(input_folder) if f.endswith('.wav')]
    
    for file in audio_files:
        filepath = os.path.join(input_folder, file)
        y, sr = librosa.load(filepath, sr=None)
        
        onset_time = find_high_energy_onset(y, sr)  # 计算主能量起点
        actual_duration = librosa.get_duration(y=y, sr=sr)  # 获取音频实际长度

        onset_times.append(onset_time)
        actual_durations.append(actual_duration)
    
    # 计算最早的主能量时间点，确保所有 syllable 对齐
    min_onset = min(onset_times)
    max_duration = max(actual_durations)
    final_length = min(target_length, max_duration)

    print(f"最早主能量起点: {min_onset:.3f} 秒, 统一裁剪长度: {final_length:.3f} 秒")

    for file in audio_files:
        filepath = os.path.join(input_folder, file)
        y, sr = librosa.load(filepath, sr=None)

        onset_time = find_high_energy_onset(y, sr)
        onset_sample = int(onset_time * sr)  # 计算主能量起点的采样点
        start_sample = max(0, onset_sample - int(min_onset * sr))  # 对齐 syllable

        # 计算 syllable 真实结束点，确保不会截断
        actual_end_time = librosa.get_duration(y=y, sr=sr)
        end_sample = int(min(actual_end_time * sr, start_sample + final_length * sr))

        y_trimmed = y[start_sample:end_sample]

        # 确保所有 syllable 长度一致
        if len(y_trimmed) < int(final_length * sr):
            padding = int(final_length * sr) - len(y_trimmed)
            y_trimmed = np.pad(y_trimmed, (0, padding), mode='constant')

        # 保存裁剪后的音频
        output_path = os.path.join(output_folder, file)
        sf.write(output_path, y_trimmed, sr)
        print(f"处理完成: {file} -> {output_path}")

    print("所有音频处理完毕！")

# 示例使用
input_folder = "raw_syllables"  # 输入文件夹
output_folder = "processed_syllables"  # 输出文件夹
process_audio_folder(input_folder, output_folder)
