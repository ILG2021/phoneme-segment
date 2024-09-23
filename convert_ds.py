import click

import glob
import zipfile
import yaml
import os
import csv
import json
import shutil
from pydub import AudioSegment


def move_without_parent(source_dir, dest_dir):
    import os
    import shutil

    # 确保目标文件夹存在,如果不存在则创建
    os.makedirs(dest_dir, exist_ok=True)

    # 遍历源文件夹中的所有文件和子文件夹
    for root, dirs, files in os.walk(source_dir):
        # 构建相对源文件夹的路径
        rel_path = os.path.relpath(root, source_dir)

        # 在目标文件夹中创建相应的路径
        dest_path = os.path.join(dest_dir, rel_path)
        os.makedirs(dest_path, exist_ok=True)

        # 移动文件
        for file in files:
            src_file = os.path.join(root, file)
            dest_file = os.path.join(dest_path, file)
            shutil.move(src_file, dest_file)


def is_excluded(phoneme):
    return phoneme in ["pau", "sil", "del", "vtrash", "ctrash", "axh"]


def get_special_phonemes(lang):
    if lang == "zh":
        # 元音
        vowels = [
            "SP", "AP", "EP", "a", "ai", "an", "ang", "ao", "e", "ei", "en", "eng", "er", "i", "ia", "ian", "iang",
            "iao", "ie", "in", "ing", "iong", "iu", "o", "ong", "ou", "u", "ua", "uai", "uan", "uang", "ui",
            "un", "v", "ve", "ir", "uo", "i0", "van", "vn", "En", "E"
        ]

        # 滑音
        liquids = []
    elif lang == "fr":
        # 法语元音
        vowels = ['ah', 'eh', 'ae', 'ee', 'oe', 'ih', 'oh', 'oo', 'ou', 'uh', 'en', 'in', 'on', 'un', 'ax', 'ay', 'ey',
                  'ow', 'aa',
                  'ae1', 'ah1', 'ao', 'eh1', 'er', 'ih1', 'iy', 'oy', 'uh1', 'uw', 'aw', 'a', 'i', 'e', 'o', 'u', 'nn']

        # 法语滑音
        liquids = ['rx', 'l', 'r', 'rh', 'rr', 'vf', 'EP']

        all_phonemes = ['AP', 'SP', 'ah', 'eh', 'ae', 'ee', 'oe', 'ih', 'oh', 'oo', 'ou', 'uh', 'en', 'in', 'on', 'un',
                        'ax', 'ay', 'ey', 'ow', 'aa', 'ae1', 'ah1', 'ao', 'eh1', 'er', 'ih1', 'iy', 'oy', 'uh1', 'uw',
                        'aw', 'a', 'i', 'e', 'o', 'u', 'nn', 'y', 'w', 'uy', 'tr', 'tx', 'dh', 'dr', 'dz', 'f', 'k',
                        'p', 'rx', 's', 'sh', 't', 'h', 'ts', 'ch', 'th', 'b', 'd', 'g', 'l', 'm', 'n', 'r', 'v', 'z',
                        'j', 'ng', 'rh', 'dx', 'rr', 'jh', 'q', 'vf', 'cl', 'axh', 'ctrash', 'vtrash']
    elif lang == "en":
        vowels = ["aa", "ae", "ah", "ao", "aw", "ay", "ax", "eh", "er", "ey", "ih", "iy", "ow", "oy", "uh", "uw"]
        liquids = ["l", "r"]

    elif lang == 'pt':
        vowels = [
            "SP", "AP", "EP", "a", "a~", "e", "e~", "E", "i", "i~", "o", "o~", "O", "u", "u~",
        ]
        # 滑音
        liquids = [
            'J', 'w'
        ]
    elif lang == 'hi':
        vowels = [
            'a', 'aa', 'i', 'ee', 'u', 'oo', 'r', 'e', 'ai', 'o', 'au', 'an', 'ah'
        ]
        # 滑音
        liquids = [

        ]
    elif lang == "tl":
        # 元音
        vowels = ["a", "i", "e", "o", "u"]

        # 滑音
        liquids = ["ay", "aw", "y", "w"]
        all_phonemes = ['a', 'aw', 'ay', 'b', 'ch', 'cl', 'd', 'e', 'f', 'g', 'h', 'i', 'jh', 'k', 'l', 'm', 'n', 'ng',
                        'ny', 'o', 'p', 'r', 's', 'sh', 't', 'u', 'v', 'w', 'y']
    return vowels, liquids


@click.command()
@click.option(
    "--data_zip_path",
    "-z",
    help="数据集zip文件",
)
@click.option(
    "--max_silence_phoneme_amount",
    "-ms",
    default=2
)
@click.option(
    "--lang",
    "-l",
    default="fr"
)
def main(data_zip_path, max_silence_phoneme_amount, lang):
    # 这里不用自带的音高算法，在后续流程中使用SOME
    estimate_midi = False
    segment_length = 15
    all_shits = "./segments"
    all_shits_not_wav_n_lab = "./segments/diffsinger_db"

    vowel_types, liquid_types = get_special_phonemes(lang)

    if os.path.exists("./segments"):
        shutil.rmtree("./segments")

    if not os.path.exists(all_shits_not_wav_n_lab):
        os.makedirs(all_shits_not_wav_n_lab)

    with zipfile.ZipFile(data_zip_path, 'r') as zip_ref:
        zip_ref.extractall(all_shits_not_wav_n_lab)

    # 获取所有的wav文件
    wav_map = {}
    for root, dirs, files in os.walk(all_shits):
        for file in files:
            if file.endswith('.wav'):
                file_name = os.path.splitext(file)[0]
                file_path = os.path.join(root, file)
                wav_map[file_name] = file_path

    for root, dirs, files in os.walk(all_shits):
        for filename in files:
            if filename.endswith(".lab"):
                file_path = os.path.join(root, filename)

                with open(file_path, "r") as file:
                    file_data = file.read()

                # nnsvs-db-converter后面处理用到的是pau
                file_data = file_data.replace("SP", "pau")
                file_data = file_data.replace("del", "pau")
                file_data = file_data.replace("vf", "pau")
                file_data = file_data.replace("ctrash", "pau")
                file_data = file_data.replace("vtrash", "pau")
                file_data = file_data.replace("br", "AP")
                file_data = file_data.replace("axh", "EP")
                with open(file_path, "w") as file:
                    file.write(file_data)

                # 将pau部分静音，防止数据干扰。获取所有的pau音素的起始时间和结束时间，单位是 毫秒*10000
                pau_arr = []
                lines = file_data.split("\n")
                for line in lines:
                    parts = line.strip().split()
                    if len(parts) >= 3 and parts[2].lower() == 'pau':
                        start = int(parts[0])
                        end = int(parts[1])
                        pau_arr.append({'start': start, 'end': end})

                # 获取lab文件对应的wav文件
                wav_file_name = filename.replace(".lab", "")
                if wav_file_name in wav_map:
                    audio = AudioSegment.from_wav(wav_map[wav_file_name])
                    for interval in pau_arr:
                        start_ms = int(interval['start'] / 10000)  # 转换成毫秒
                        end_ms = int(interval['end'] / 10000)  # 转换成毫秒
                        silence_segment = AudioSegment.silent(duration=end_ms - start_ms,
                                                              frame_rate=audio.frame_rate)  # 创建静音区域
                        audio = audio[:start_ms] + silence_segment + audio[end_ms:]  # 替换到音频中
                    audio.export(wav_map[wav_file_name], format="wav")  # 导出并覆盖原文件

    # for funny auto dict generator lmao
    out = "./dictionary/custom_dict.txt"

    phonemes = set()

    phoneme_folder_path = all_shits
    for root, dirs, files in os.walk(phoneme_folder_path):
        for file in files:
            if file.endswith(".lab"):
                fpath = os.path.join(root, file)
                with open(fpath, "r") as lab_file:
                    for line in lab_file:
                        line = line.strip()
                        if line:
                            print("lab file:", lab_file)
                            print('line', line)
                            phoneme = line.split()[2]
                            if not is_excluded(phoneme):
                                phonemes.add(phoneme)

    with open(out, "w") as f:
        for phoneme in sorted(phonemes):
            f.write(phoneme + "	" + phoneme + "\n")

    dict_path = out
    vowel_data = []
    consonant_data = []
    liquid_data = []

    with open(dict_path, "r") as f:
        for line in f:
            phoneme, _ = line.strip().split("\t")
            if phoneme[0] in vowel_types:
                vowel_data.append(phoneme)
            elif phoneme[0] in liquid_types:
                liquid_data.append(phoneme)
            else:
                consonant_data.append(phoneme)

    vowel_data.sort()
    liquid_data.sort()
    consonant_data.sort()
    directory = os.path.dirname(dict_path)

    # make txt for language json file
    vowel_txt_path = os.path.join(directory, "vowels.txt")
    with open(vowel_txt_path, "w") as f:
        f.write(" ".join(vowel_data))
    liquid_txt_path = os.path.join(directory, "liquids.txt")
    with open(liquid_txt_path, "w") as f:
        f.write(" ".join(liquid_data))
    consonant_txt_path = os.path.join(directory, "consonants.txt")
    with open(consonant_txt_path, "w") as f:
        f.write(" ".join(consonant_data))

    # here's a funny json append
    with open(vowel_txt_path, "r") as f:
        vowel_data = f.read().split()
    with open(liquid_txt_path, "r") as f:
        liquid_data = f.read().split()
    with open(consonant_txt_path, "r") as f:
        consonant_data = f.read().split()
    phones4json = {"vowels": vowel_data, "liquids": liquid_data}

    print("phones4json", phones4json)
    with open("./nnsvs-db-converter/lang.sample.json", "w") as rawr:
        json.dump(phones4json, rawr, indent=4)

    db_converter_script = "./nnsvs-db-converter/db_converter.py"
    for raw_folder_name in os.listdir(all_shits_not_wav_n_lab):
        raw_folder_path = os.path.join(all_shits_not_wav_n_lab, raw_folder_name)
        if os.path.isdir(raw_folder_path):

            raw_speaker_folder_names = [raw_speaker_folder_name for raw_speaker_folder_name in
                                        os.listdir(raw_folder_path)
                                        if os.path.isdir(
                    os.path.join(raw_folder_path, raw_speaker_folder_name)) and raw_speaker_folder_name not in ['lab',
                                                                                                                'wav',
                                                                                                                'diffsinger_db']]
            raw_speaker_folder_paths = []
            if len(raw_speaker_folder_names) > 0:
                for raw_speaker_folder_name in raw_speaker_folder_names:
                    raw_speaker_folder_paths.append(os.path.join(raw_folder_path, raw_speaker_folder_name))
            else:
                raw_speaker_folder_paths.append(raw_folder_path)

            for raw_speaker_folder_path in raw_speaker_folder_paths:
                if estimate_midi:
                    os.system(
                        f'python {db_converter_script} -s {max_silence_phoneme_amount} -S 60 -l {segment_length} -m -c -L "./nnsvs-db-converter/lang.sample.json" --folder {raw_speaker_folder_path}')
                else:
                    os.system(
                        f'python {db_converter_script} -s {max_silence_phoneme_amount} -S 60 -l {segment_length} -L "./nnsvs-db-converter/lang.sample.json" --folder {raw_speaker_folder_path}')

    for raw_folder_name in os.listdir(all_shits_not_wav_n_lab):
        raw_folder_path = os.path.join(all_shits_not_wav_n_lab, raw_folder_name)
        # 获取匹配指定模式的所有.wav文件路径列表
        wav_files = glob.glob(os.path.join(raw_folder_path, "*.wav"))
        # 获取匹配指定模式的所有.lab文件路径列表
        lab_files = glob.glob(os.path.join(raw_folder_path, "*.lab"))
        # 删除所有.wav文件
        for wav_file in wav_files:
            os.remove(wav_file)
        # 删除所有.lab文件
        for lab_file in lab_files:
            os.remove(lab_file)

        parent_folder = raw_folder_path
        source_folder = os.path.join(raw_folder_path, "diffsinger_db")
        to_delete_folders = [source_folder]
        speaker_source_folders = []
        raw_speaker_folder_names = [raw_speaker_folder_name for raw_speaker_folder_name in os.listdir(raw_folder_path)
                                    if
                                    os.path.isdir(os.path.join(raw_folder_path,
                                                               raw_speaker_folder_name)) and raw_speaker_folder_name not in [
                                        'lab', 'wav', 'diffsinger_db']]

        # 如果有多个文件夹说明是多说话人数据集
        if len(raw_speaker_folder_names) > 1:
            to_delete_folders = [raw_folder_path]
            parent_folder = all_shits_not_wav_n_lab
            for raw_speaker_folder_name in raw_speaker_folder_names:
                raw_speaker_folder_path = os.path.join(raw_folder_path, raw_speaker_folder_name)
                source_folder = raw_folder_path
                parent_folder = all_shits_not_wav_n_lab
                # 需要把每个说话人文件夹中的 diffsinger_db 文件内容提取出来
                speaker_source_folders.append(raw_speaker_folder_path)

        if len(speaker_source_folders) > 0:
            for speaker_source_folder in speaker_source_folders:
                move_without_parent(os.path.join(speaker_source_folder, "diffsinger_db"), speaker_source_folder)

                shutil.rmtree(os.path.join(speaker_source_folder, 'lab'))
                shutil.rmtree(os.path.join(speaker_source_folder, 'wav'))
                shutil.rmtree(os.path.join(speaker_source_folder, 'diffsinger_db'))

        move_without_parent(source_folder, parent_folder)

        for to_delete_folder in to_delete_folders:
            shutil.rmtree(to_delete_folder)

    # make it replace the first SP to AP cus it seems like people always forgot about it
    for root, _, files in os.walk(all_shits_not_wav_n_lab):
        for file in files:
            if file.endswith(".csv"):
                file_path = os.path.join(root, file)
                with open(file_path, "r", newline="", encoding='utf-8') as input_file:
                    csv_reader = csv.reader(input_file)
                    data = [row for row in csv_reader]
                    header = data[0]
                    if "ph_seq" in header:
                        ph_seq_index = header.index("ph_seq")
                        if len(data) > 1 and len(data[1]) > ph_seq_index:
                            data[1][ph_seq_index] = data[1][ph_seq_index].replace("SP", "AP", 1)
                with open(file_path, "w", newline="", encoding='utf-8') as output_file:
                    csv_writer = csv.writer(output_file)
                    csv_writer.writerows(data)

    print("extraction complete!")
    print("|")
    print("|")
    print("|")
    print("I'm also nice enough to convert your data and also write your dict.txt lmao. You are welcome :)")


if __name__ == '__main__':
    main()
