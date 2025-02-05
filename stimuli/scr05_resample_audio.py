import os
from func_audio_processing import resample_audio

# 获取脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))

# 调用脚本所在目录的子文件夹
from_dir = os.path.join(current_dir, "processed", "syllables_denoised")
to_dir = os.path.join(current_dir, "processed", "syllables_resampled")
resample_audio(from_dir, to_dir, target_sr=48000)

# def resample_all_subfolders(from_dir, to_dir, target_sr=44100):
#     """
#     Resample all audio files in the subfolders of 'from_dir' and save them
#     to the corresponding subfolders in 'to_dir'.
    
#     Parameters:
#     - from_dir (str): Path to the parent directory containing subfolders with audio files.
#     - to_dir (str): Path to the output parent directory for resampled audio.
#     - target_sr (int): Target sampling rate for resampled audio (default: 44100 Hz).
#     """
#     # Ensure the output directory exists
#     os.makedirs(to_dir, exist_ok=True)
    
#     # Iterate over all subdirectories in the input directory
#     for subfolder in os.listdir(from_dir):
#         subfolder_path = os.path.join(from_dir, subfolder)
        
#         # Check if it's a directory
#         if os.path.isdir(subfolder_path):
#             # Define corresponding output subfolder
#             output_subfolder = os.path.join(to_dir, subfolder)
            
#             # Call resample_audio function for this subfolder
#             print(f"Processing subfolder: {subfolder_path}")
#             resample_audio(subfolder_path, output_subfolder, target_sr=target_sr)

# # 获取脚本所在目录
# current_dir = os.path.dirname(os.path.abspath(__file__))

# # 输入和输出目录
# from_dir = os.path.join(current_dir, "sequences", "combined_wav_mono")
# to_dir = os.path.join(current_dir, "sequences", "combined_wav_mono_44100")

# # 调用函数
# resample_all_subfolders(from_dir, to_dir, target_sr=44100)
