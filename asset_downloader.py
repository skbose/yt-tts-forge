import os
import pytube
import argparse
import logging
import hydra
from omegaconf import DictConfig, OmegaConf



class AssetDownloader:
    """
    A class that downloads audio and captions from YouTube videos.

    Attributes:
        None

    Methods:
        __init__: Initializes an instance of the AssetDownloader class.
        process_caption: Processes the caption text.
        download: Downloads the audio and captions from a given YouTube URL.
    """

    def __init__(self):
        pass

    def process_caption(self, caption):
        """
        Processes the caption text.

        Args:
            caption (str): The caption text to be processed.

        Returns:
            str: The processed caption text.
        """
        return caption

    def download(self, url, output_dir):
        """
        Downloads the audio and captions from a given YouTube URL.

        Args:
            url (str): The URL of the YouTube video.
            output_dir (str): The directory where the downloaded files will be saved.

        Returns:
            None
        """
        yt = pytube.YouTube(url)
        stream = yt.streams.filter(only_audio=True).first()

        # download the audio and save to output directory
        stream.download(output_dir)

        # get all captions
        for caption_obj in yt.captions.keys():
            caption = yt.captions.get(caption_obj.code)
            srt_caption = caption.generate_srt_captions()
            srt_caption = self.process_caption(srt_caption)

            caption_name = caption.name
            output_path = os.path.join(output_dir, f"{yt.title}_{caption_name}.srt")

            with open(output_path, 'w') as f:
                f.write(srt_caption)
                logging.info(f"Downloaded {caption_name} to {output_path}")

        logging.info(f"Downloaded {yt.title} to {output_path}")


@hydra.main(version_base=None, config_path="configs", config_name="config")
def main(cfg: DictConfig):
    logging.info(OmegaConf.to_yaml(cfg))

    downloader = AssetDownloader()
    downloader.download(cfg.yt_asset.url, cfg.yt_asset.output_dir)


if __name__ == "__main__":
    main()
