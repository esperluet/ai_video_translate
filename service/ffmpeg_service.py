import os
import ffmpeg
import uuid
import logging

def extract_audio(video_path: str, target_dir: str) -> str:
    """
    Extracts audio from a video file using the ffmpeg-python library.

    Args:
        video_path (str): Path to the video file.
        output_dir (str): Directory to save the extracted audio.

    Returns:
        str: Path to the extracted audio file.
    """
    try:
        os.makedirs(target_dir, exist_ok=True)

        # Generate a unique filename for the audio
        audio_file_name = f"{uuid.uuid4()}.mp3"
        audio_file_path = os.path.join(target_dir, audio_file_name)

        # Use ffmpeg-python to extract audio
        ffmpeg.input(video_path).output(audio_file_path, acodec='mp3', vn=None).run(overwrite_output=True)

        logging.info(f"Audio extracted successfully: {audio_file_path}")
        return audio_file_path

    except ffmpeg.Error as e:
        logging.error(f"Audio extraction failed: {e.stderr.decode()}")
        raise RuntimeError(f"Audio extraction failed: {e.stderr.decode()}")
