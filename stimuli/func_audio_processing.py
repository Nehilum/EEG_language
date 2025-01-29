import os
import librosa
import soundfile as sf
import noisereduce as nr
import pyloudnorm as pyln
import scipy.signal

# ✅ LUFS 归一化
def normalize_lufs(input_folder, output_folder, target_lufs=-23):
    """ 统一音频强度到目标 LUFS (-23 LUFS by default) """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for file in os.listdir(input_folder):
        if file.endswith('.wav'):
            filepath = os.path.join(input_folder, file)
            y, sr = librosa.load(filepath, sr=None)

            meter = pyln.Meter(sr)
            loudness = meter.integrated_loudness(y)

            # 计算增益调整
            y_normalized = pyln.normalize.loudness(y, loudness, target_lufs)

            output_path = os.path.join(output_folder, file)
            sf.write(output_path, y_normalized, sr)
            print(f"✅ LUFS 归一化: {file} -> {output_path}")

# ✅ 降噪
def denoise_audio(input_folder, output_folder):
    """ 对音频进行降噪处理 """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for file in os.listdir(input_folder):
        if file.endswith('.wav'):
            filepath = os.path.join(input_folder, file)
            y, sr = librosa.load(filepath, sr=None)

            # 降噪
            y_denoised = nr.reduce_noise(y=y, sr=sr, prop_decrease=0.8)

            output_path = os.path.join(output_folder, file)
            sf.write(output_path, y_denoised, sr)
            print(f"✅ 降噪处理: {file} -> {output_path}")

# ✅ 采样率统一
def resample_audio(input_folder, output_folder, target_sr=48000):
    """ 统一音频采样率，默认 48000 Hz """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for file in os.listdir(input_folder):
        if file.endswith('.wav'):
            filepath = os.path.join(input_folder, file)
            y, sr = librosa.load(filepath, sr=None)

            # 重新采样
            y_resampled = librosa.resample(y, orig_sr=sr, target_sr=target_sr)

            output_path = os.path.join(output_folder, file)
            sf.write(output_path, y_resampled, target_sr)
            print(f"✅ 采样率调整: {file} -> {output_path} ({target_sr} Hz)")

# ✅ 频谱平滑
def smooth_spectrum(input_folder, output_folder, cutoff_freq=8000):
    """ 频谱平滑：低通滤波 (默认 8000 Hz) """
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for file in os.listdir(input_folder):
        if file.endswith('.wav'):
            filepath = os.path.join(input_folder, file)
            y, sr = librosa.load(filepath, sr=None)

            # 设计低通滤波器
            sos = scipy.signal.butter(10, cutoff_freq, 'low', fs=sr, output='sos')
            y_smoothed = scipy.signal.sosfilt(sos, y)

            output_path = os.path.join(output_folder, file)
            sf.write(output_path, y_smoothed, sr)
            print(f"✅ 频谱平滑: {file} -> {output_path} (Cutoff: {cutoff_freq} Hz)")
