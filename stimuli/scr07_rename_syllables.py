import os
import shutil

# 辅音到前缀的映射关系
consonant_to_prefix = {
    "b": "A1",
    "d": "A2",
    "g": "A3",
    "p": "B1",
    "t": "B2",
    "k": "B3"
}

# 元音拼写归一化规则
vowel_normalization = {
    "e": "e",
    "eh": "e",
    "ie": "i",
    "u": "u",
    "uh": "u",
    "o": "o",
    "oh": "o",
    "i": "i"
}

def rename_and_copy_syllables(input_dir, output_dir):
    """
    读取 input_dir 文件夹中的音频文件，按规则重命名并保存到 output_dir。
    """
    os.makedirs(output_dir, exist_ok=True)  # 创建目标文件夹（如果不存在）

    for filename in os.listdir(input_dir):
        if filename.endswith('.wav'):
            # 获取文件名（去掉扩展名）
            base_name, ext = os.path.splitext(filename)
            
            # 检查文件名格式是否符合 (辅音 + 元音)
            if len(base_name) < 2:
                print(f"Skipping {filename} - unexpected format")
                continue
            
            # 提取辅音和元音部分
            consonant = base_name[0]
            vowel_spelling = base_name[1:]
            
            # 查找辅音对应的前缀
            prefix = consonant_to_prefix.get(consonant)
            if not prefix:
                print(f"Skipping {filename} - unknown consonant '{consonant}'")
                continue
            
            # 查找元音的标准化拼写
            normalized_vowel = vowel_normalization.get(vowel_spelling)
            if not normalized_vowel:
                print(f"Skipping {filename} - unknown vowel spelling '{vowel_spelling}'")
                continue
            
            # 构造新文件名
            new_name = f"{prefix}_{normalized_vowel}_{consonant}{ext}"
            input_path = os.path.join(input_dir, filename)
            output_path = os.path.join(output_dir, new_name)
            
            # 将文件复制并重命名到新文件夹
            shutil.copy(input_path, output_path)
            print(f"Copied and renamed: '{filename}' -> '{new_name}'")

# 运行重命名和复制函数
# 获取脚本所在目录
current_dir = os.path.dirname(os.path.abspath(__file__))

from_dir = os.path.join(current_dir, "processed", "syllables_smoothed")
to_dir = os.path.join(current_dir, "processed", "stim_syllables")
rename_and_copy_syllables(from_dir, to_dir)