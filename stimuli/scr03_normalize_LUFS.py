import os
from func_audio_processing import normalize_lufs

# 获取脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 调用脚本所在目录的子文件夹
from_dir = os.path.join(current_dir, "processed", "final_trimmed_syllables")
to_dir = os.path.join(current_dir, "processed", "syllables_lufs")
normalize_lufs(from_dir, to_dir,  target_lufs=-23)
