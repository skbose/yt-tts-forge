# yt-tts-forge
Your go-to repository for training cutting-edge Text-to-Speech (TTS) models using rich, diverse data sourced from YouTube. Unlock the power of natural-sounding speech synthesis by leveraging our comprehensive collection of YouTube data. Train your TTS models with ease and precision, revolutionizing the way voice is synthesized from text.

# Installation

**Step 1.**
Create a conda environment
```
conda create -n yt-tts-forge python=3.9
```

**Step 2.**
Install poetry
```
pip install poetry
```

**Step 3.**
Install packages
```
poetry install
```

# Prepare TTS dataset from youtube URLs

## Download youtube audio and transcript

**Step 1.**

Edit the config (or add a new one) under `configs/yt_asset` as per the following schema:
```
url: <Youtube video URL>
output_dir: <Output directory path>
```

**Step 2.**

Execute the `asset_downloader.py` script
```
python asset_downloader.py
```

## Align the audio and transcript


**Step 1.**
Edit the config under `configs/tts_align` as per the following schema:
```
threshold: <threshold duration in seconds, audio will be clipped to this duration>
audio_path: <path to downloaded audio (mp4 format)>
srt_path: <path to downloaded subtitle (srt format)>
output_path: <path to store the aligned output>
```

**Step 2.**
Execute `tts_align.py`
```
python tts_align.py
```

## Prepare the dataset in trainable format (huggingface dataset and LJSynth)

**Step 1.**
Edit the config under `configs/tts_prepare` as per the following schema:
```
speaker_name: <speaker name>
output_path: <path to output dataset>
aligned_path: <path to aligned outputs (previous step)>
sample_rate: 16000 (usually 16K for ML models)>
```
**Step 2.**
Execute tts_prepare.py
```
python tts_prepare.py
```


