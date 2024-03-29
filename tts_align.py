# Description: Aligns the text (srt) with the audio file from the downloaded YouTube audio.
import os
import pysrt
from pydub import AudioSegment
import hydra
from tqdm import tqdm
from datetime import datetime


import logging
logging.basicConfig(level=logging.DEBUG)


class AlignTTS:
    '''
    Aligns the text (srt) with the audio file from the downloaded YouTube audio.

    Algorithm:
    - Read the srt file and extract the text and timestamps.
    - Set a threshold for the minimum duration of the audio file.
    - Merge lines of the srt file that are less than the threshold.
    - Use the start and end time to extract the audio from the audio file.
    - Save the audio and text in the output directory
    '''
    def __init__(self, config):
        """
        Initializes the AlignTTS object.

        Args:
            config (dict): Configuration parameters for the alignment process.
        """
        self.config = config
        
        # copy to local variables
        self.audio_path = self.config.tts_align.audio_path
        self.srt_path = self.config.tts_align.srt_path
        self.output_path = self.config.tts_align.output_path

        # create output directory if not exists, else raise error
        if not os.path.exists(self.output_path):
            os.makedirs(self.output_path)
            logging.info(f"Created directory {self.output_path}")
        else:
            raise FileExistsError(f"Directory {self.output_path} already exists")

    def _datetime_to_seconds(self, time: datetime.time) -> int:
        """
        Converts a datetime.time object to seconds.

        Args:
            time (datetime.time): The time object to convert.

        Returns:
            int: The time in seconds.
        """
        return time.hour * 3600 + time.minute * 60 + time.second

    def align(self):
            """
            Aligns the audio and subtitles by extracting audio segments based on the subtitle timings.

            Returns:
                None
            """
            # read the srt file
            srt = pysrt.open(self.srt_path)

            # set the minimum duration of the audio file
            threshold = self.config.tts_align.threshold

            # merge lines that are less than the threshold
            srt = self.merge_lines(srt, threshold)

            # extract audio from the audio file
            for i, line in tqdm(enumerate(srt), desc="Syncing audio & subtitles..", total=len(srt)):
                start = self._datetime_to_seconds(line.start.to_time())
                end = self._datetime_to_seconds(line.end.to_time())

                audio = AudioSegment.from_file(self.audio_path)
                # convert seconds to millis and slice the audio array
                audio = audio[start*1000:end*1000]

                # save the audio and text in the output directory
                output_path = os.path.join(self.output_path, f"{i}.wav")
                audio.export(output_path, format="wav")

                with open(os.path.join(self.output_path, f"{i}.txt"), 'w') as f:
                    f.write(line.text)

    def merge_lines(self, srt: pysrt.SubRipFile, threshold: int) -> pysrt.SubRipFile:
        """
        Merges lines in the srt file that are less than the threshold duration.

        Args:
            srt (pysrt.SubRipFile): The srt file to merge lines from.
            threshold (int): The minimum duration threshold in seconds.

        Returns:
            pysrt.SubRipFile: The modified srt file with merged lines.
        """
        new_srt = pysrt.SubRipFile()
        curr_line = srt[0]

        for i, line in enumerate(srt[1:]):
            duration = line.end - curr_line.start

            # convert duration to seconds
            duration = duration.seconds

            if duration < threshold:
                curr_line.text += " " + line.text
                curr_line.end = line.end
            else:
                new_srt.append(curr_line)
                curr_line = line
                curr_line.start = line.start
                curr_line.end = line.end

        new_srt.append(curr_line)
        return new_srt


@hydra.main(version_base=None, config_path="configs", config_name="config")
def main(cfg):
    align_tts = AlignTTS(cfg)
    align_tts.align()


if __name__ == "__main__":
    main()

    