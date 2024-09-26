# Phoneme Segment

## Introduction

This project is a simplified version of SOFA (Singing-Oriented Forced Aligner) and only provides phoneme boundary segmentation. It can be used when SOFA's results are not accurate enough. After segmenting the boundaries, you can manually input the phonemes in vlabeler.

## Usage

### Environment Setup

1. Use `git clone` to download the repository code.
2. Install conda or use venv.
3. Go to the [PyTorch website](https://pytorch.org/get-started/locally/) to install torch.
4. (Optional, for faster wav file reading) Install torchaudio from the [PyTorch website](https://pytorch.org/get-started/locally/).
5. Install other Python libraries:
    ```bash
    pip install -r requirements.txt
    ```

### Training

1. Follow the steps above to set up the environment. It is recommended to install torchaudio for faster binarization speed.
2. Run `python convert_ds.py --data_zip_path xxx.zip --lang xx` to convert the nnsvs dataset into the diffsinger dataset. Conversion needs to be done separately by language. Supported languages can be found in `convert_ds.py`.
3. Place the training data in the `data` folder in the following format:

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
4. Modify `binarize_config.yaml` as needed, then run `python binarize.py`.
5. Modify `train_config.yaml` as needed, then run `python train.py`. If you want to resume training, use `python train.py -r`.
6. For training visualization, use: `tensorboard --logdir=ckpt/`.

### Inference

1. Prepare the audio files to be segmented and place them in a folder (default is the `/segments` folder) in the following format:
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

2. Inference via Command Line

    Run `python infer.py` for inference.

    Required parameters:
    - `--ckpt`: (mandatory) Path to the model weights.
    - `--folder`: Folder containing the data to be aligned (default is `segments`).

    ```bash
    python infer.py -c checkpoint_path -f segments_path
    ```
3. Obtain the Final Annotations
   A .lab file with the same name will be generated in the folder containing the audio files.
