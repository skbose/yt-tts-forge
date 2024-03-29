import os
import glob
import hydra
from tqdm import tqdm
from dataclasses import dataclass
import logging
import shutil

from utils.text_cleaners import english_cleaners
import pandas as pd
import datasets

import librosa


logging.basicConfig(level=logging.INFO)


class DatasetPreparation:
    def __init__(self, config):
        self.config = config
        self.speaker_name = self.config.tts_prepare.speaker_name
        self.sample_rate = self.config.tts_prepare.sample_rate
    
    def convert_to_ljsynth_format(self):
        '''
        This function prepares the dataset for the TTS model.
        We will use the format of the LJSpeech dataset.
        <audio> | <text> | <text_normalized>
        '''
        # read the wav
        aligned_output_path = self.config.tts_prepare.aligned_path
        audio_files = glob.glob(os.path.join(aligned_output_path, "*.wav"))
        audio_files = sorted(audio_files)

        # read the text
        text_files = glob.glob(os.path.join(aligned_output_path, "*.txt"))
        text_files = sorted(text_files)

        # create speaker directory
        speaker_dir = os.path.join(self.config.tts_prepare.output_path, self.speaker_name)
        os.makedirs(speaker_dir, exist_ok=True)

        # create the metadata file
        metadata_file = os.path.join(speaker_dir, "metadata.txt")

        with open(metadata_file, 'w') as f:
            for audio_file, text_file in tqdm(zip(audio_files, text_files), desc="Preparing dataset..", total=len(audio_files)):
                audio = os.path.basename(audio_file)
                text = open(text_file, 'r').read().strip()
                text_normalized = english_cleaners(text)

                f.write(f"{audio}|{text}|{text_normalized}\n")

        logging.info(f"Saved metadata to {metadata_file}")

        # write the wav files to the speaker directory, under a wav directory
        wav_dir = os.path.join(speaker_dir, "wavs")
        os.makedirs(wav_dir, exist_ok=True)

        for audio_file in audio_files:
            for audio_file in audio_files:
                shutil.copy(audio_file, os.path.join(wav_dir, os.path.basename(audio_file)))

        logging.info(f"Moved wav files to {wav_dir}")
        logging.info("Dataset preparation complete.")

    def load_audio_array(self, audio_file, dir_name, sample_rate):
        '''
        This function loads the audio file as an array.
        '''
        audio_file = os.path.join(dir_name, audio_file)
        audio, _ = librosa.load(audio_file, sr=sample_rate)
        return audio
    
    def create_hugging_face_dataset(self):
        '''
        This function creates the hugging face dataset.
        '''
        data_dir = self.config.tts_prepare.output_path
        speaker_dir = os.path.join(data_dir, self.speaker_name)
        wav_dir = os.path.join(speaker_dir, "wavs")
        metadata_file = os.path.join(speaker_dir, "metadata.txt")

        # create the hugging face dataset
        dataset_name = f"{self.speaker_name}_tts"
        dataset_dir = os.path.join(data_dir, dataset_name)

        # init huggingface Dataset class
        dataset = datasets.Dataset.from_pandas(pd.read_csv(metadata_file, sep="|", names=["audio_id", "text", "text_normalized"]))

        # add speaker_name to all rows
        dataset = dataset.map(lambda x: {"speaker": self.speaker_name})

        # add audio array for all rows
        dataset = dataset.map(lambda x: {
            "audio": self.load_audio_array(x["audio_id"], wav_dir, self.sample_rate),
            "sample_rate": self.sample_rate
        })

        # save the dataset
        dataset.save_to_disk(dataset_dir)

    def prepare_dataset(self):
        self.convert_to_ljsynth_format()
        self.create_hugging_face_dataset()


@hydra.main(config_path="configs", config_name="config")
def main(cfg):
    logging.info(f"Preparing dataset for TTS model..")

    dataset_preparation = DatasetPreparation(cfg)
    dataset_preparation.prepare_dataset()


if __name__ == "__main__":
    main()
