import os
import subprocess
import uuid
import logging

def extract_audio(video_path: str, output_dir: str = './extracted_audio/') -> str:
    """
    Extracts the audio from a video file using ffmpeg.

    Args:
        video_path (str): Path to the video file.
        output_dir (str): Directory where the extracted audio will be saved.

    Returns:
        str: Path to the extracted audio file.
    """
    try:
        os.makedirs(output_dir, exist_ok=True)

        # Generate a unique audio filename
        audio_file_name = f"{uuid.uuid4()}.mp3"
        audio_file_path = os.path.join(output_dir, audio_file_name)

        # Extract audio using ffmpeg
        command = [
            "ffmpeg",
            "-i", video_path,
            "-q:a", "0",
            "-map", "a",
            audio_file_path,
            "-y"  # Overwrite if file exists
        ]
        subprocess.run(command, check=True)

        logging.info("Audio extracted successfully: %s", audio_file_path)
        return audio_file_path

    except subprocess.CalledProcessError as e:
        logging.error("Audio extraction failed: %s", e)
        raise RuntimeError(f"Audio extraction failed: {e}")
