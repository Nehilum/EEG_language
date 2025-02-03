import os
from pydub import AudioSegment

def convert_to_mono(from_dir, to_dir):
    """
    Convert all audio files in from_dir to mono and save to to_dir.
    
    Parameters:
    - from_dir (str): Path to the input directory containing audio files.
    - to_dir (str): Path to the output directory for mono audio files.
    """
    # 创建目标文件夹（如果不存在）
    os.makedirs(to_dir, exist_ok=True)

    # 遍历输入目录中的所有文件
    for file in os.listdir(from_dir):
        if file.endswith(".wav"):  # 只处理 .wav 文件
            input_path = os.path.join(from_dir, file)
            output_path = os.path.join(to_dir, file)

            # 加载音频文件
            audio = AudioSegment.from_file(input_path)

            # 检查是否为 stereo，并转换为 mono
            if audio.channels > 1:
                audio = audio.set_channels(1)  # 设置为单声道
                print(f"Converted to mono: {file}")
            else:
                print(f"Already mono: {file}")

            # 保存文件到目标目录
            audio.export(output_path, format="wav")
            print(f"Saved mono file: {output_path}")

# 设置输入和输出目录
current_dir = os.getcwd()  # 获取当前脚本所在目录
from_dir = os.path.join(current_dir, "processed", "stim_syllables")
to_dir = os.path.join(current_dir, "processed", "stim_syllables_mono")

# 运行转换函数
convert_to_mono(from_dir, to_dir)
