# Phoneme Segment

# 介绍

项目基于SOFA(Singing-Oriented Forced Aligner)修改而来，是SOFA的简化版，仅提供音素边界分割，在SOFA不太准确的时候可以使用。分割好边界之后手动在vlabeler中输入音素。

# 使用方法

## 环境配置

1. 使用`git clone`​​下载本仓库的代码
2. 安装conda或使用venv
3. 去[pytorch官网](https://pytorch.org/get-started/locally/)安装torch 
4. （可选，用于提高wav读取速度）去[pytorch官网](https://pytorch.org/get-started/locally/)安装torchaudio
5. 安装其他python库
    ```bash
    pip install -r requirements.txt
    ```

## 训练

1. 参照上文进行环境配置。建议安装torchaudio以获得更快的binarize速度；
2. 执行`python convert_ds.py --data_zip_path xxx.zip --lang xx`将nnsvs数据集转成diffsinger数据集，转换需按语言分开，支持的语言参考convert_ds.py
3. 把训练数据按以下格式放入`data`文件夹：

    ```
    - data
        - full_label
            - singer1
                - wavs
                    - audio1.wav
                    - audio2.wav
                    - ...
                - transcriptions.csv
            - singer2
                - wavs
                    - ...
                - transcriptions.csv
    ```
4. 按需修改`binarize_config.yaml`，然后执行`python binarize.py`；
5. 按需修改`train_config.yaml`，然后执行`python train.py`，如果是resume，`python train.py -r`
6. 训练可视化：`tensorboard --logdir=ckpt/`。

## 推理

1. 准备需要分割的音频放入一个文件夹中（默认放在`/segments`​​文件夹），格式如下
    ```text
    - segments
        - singer1
            - segment1.wav
            - segment2.wav
            - ...
        - singer2
            - segment1.wav
            - ...
    ```
    
2. 命令行推理

    使用`python infer.py`进行推理。

    需要指定的参数：
    - `--ckpt`：（必须指定）模型权重路径；
    - `--folder`：存放待对齐数据的文件夹​（默认为`segments`）；

    ```bash
    python infer.py -c checkpoint_path -f segments_path
    ```
3. 获取最终标注
   在音频文件所在文件夹会生成同名lab文件

