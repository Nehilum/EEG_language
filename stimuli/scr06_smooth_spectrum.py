import os
from func_audio_processing import smooth_spectrum

# 获取脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 调用脚本所在目录的子文件夹
from_dir = os.path.join(current_dir, "processed", "syllables_resampled")
to_dir = os.path.join(current_dir, "processed", "syllables_smoothed")

smooth_spectrum(from_dir, to_dir, cutoff_freq=8000)