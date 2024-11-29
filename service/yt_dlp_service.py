import yt_dlp
import os
from dotenv import load_dotenv
import logging
import uuid
from typing import Dict, Optional

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class VideoDownloadError(Exception):
    """Custom exception for video download errors."""
    pass

class SubtitleDownloadError(Exception):
    """Custom exception for subtitle download errors."""
    pass

def download_video(
    video_url: str, 
    target_dir: str,
    file_format: str = 'mp4'
) -> Dict[str, str]:
    """
    Downloads a YouTube video in the specified format and resolution.
    """
    try:
        os.makedirs(target_dir, exist_ok=True)

        # Generate a unique file name using uuidv4
        file_name = str(uuid.uuid4())
        output_template = f'{target_dir}/{file_name}'

        ydl_opts = {
            'format': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
            'merge_output_format': file_format,
            'outtmpl': output_template,
        }

        logging.info("Starting download for URL: %s", video_url)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        output_file = f"{output_template}.{file_format}"
        logging.info("Download complete: %s", output_file)
        return {
            "success": True,
            "file_path": output_file,
            "file_format": file_format,
            "file_name": file_name,
            "message": "Download succeeded.",
        }

    except yt_dlp.utils.DownloadError as e:
        logging.error("Download failed: %s", e)
        raise VideoDownloadError(f"Download failed: {e}")
    except Exception as e:
        logging.error("An unexpected error occurred: %s", e)
        raise VideoDownloadError(f"An unexpected error occurred: {e}")




def download_subtitles(
    video_url: str, 
    file_dir: str,
) -> Optional[str]:
    """
    Downloads subtitles for a YouTube video.

    Args:
        video_url (str): The URL of the YouTube video.
        file_dir (str): The directory where the subtitles will be saved.

    Returns:
        str: The path to the downloaded subtitle file.
    """
    try:
        full_path_dir = f'{os.getenv("VIDEO_DOWNLOAD_DIR")}/{file_dir}'
        os.makedirs(full_path_dir, exist_ok=True)

        # Generate a unique file name using uuidv4
        file_name = str(uuid.uuid4())
        output_template = f"{full_path_dir}/{file_name}.%(ext)s"

        ydl_opts = {
            'subtitleslangs': ['en'],  # Download English subtitles
            'skip_download': True,  # Do not download the video
            'writesubtitles': True,  # Write subtitles to file
            'outtmpl': output_template,
        }

        logging.info("Downloading subtitles for URL: %s", video_url)
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])

        subtitle_file = f"{full_path_dir}/{file_name}.en.srt"
        logging.info("Subtitles downloaded to: %s", subtitle_file)
        return subtitle_file

    except yt_dlp.utils.DownloadError as e:
        logging.error("Subtitle download failed: %s", e)
        raise SubtitleDownloadError(f"Subtitle download failed: {e}")
    except Exception as e:
        logging.error("An unexpected error occurred while downloading subtitles: %s", e)
        raise SubtitleDownloadError(f"An unexpected error occurred: {e}")
