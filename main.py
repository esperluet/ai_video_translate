from service.yt_dlp_service import download_video, VideoDownloadError, SubtitleDownloadError
from service.translate_service import translate_subtitle
import uuid
from service.ffmpeg_service import extract_audio
from service.openai_whisper_service import transcribe_audio_to_srt
import os

if __name__ == "__main__":
    base_dir = str(uuid.uuid4())
    video_url = "https://www.youtube.com/watch?v=W-PIcRurtfs&ab_channel=CTMI"

    try:
        id_process = str(uuid.uuid4())
        target_dir = f'./{os.getenv("VIDEO_DOWNLOAD_DIR")}/{id_process}'

        # Step 1: Download Video
        # video_result = download_video(video_url, target_dir=target_dir, file_format="mp4")
        # print(f"Video Download Success: {video_result['success']}")
        # print(f"Video File Path: {video_result['file_path']}")
        # print(f"Video File Name: {video_result['file_name']}")

        # Step 2: Download Subtitles
        # subtitle_path = download_subtitles(video_url, file_dir=base_dir)
        # print(f"Subtitles downloaded to: {subtitle_path}")

        # Extract audio
        # video_path = video_result['file_path']
        # audio_file_path = extract_audio(video_path=video_path, target_dir=target_dir)

        # Speech to text
        target_dir = f'./{os.getenv("VIDEO_DOWNLOAD_DIR")}/f652f5fa-c7a1-4f36-9434-60d84f31d092'
        audio_file_path = f'./{target_dir}/aae99998-0204-47cb-a410-30c0fc214c87.mp3'
        subtitle_path = transcribe_audio_to_srt(audio_file_path, target_dir=target_dir)

        # Step 3: Translate Subtitles
        translated_subtitle_path = translate_subtitle(subtitle_path, target_language='fr')
        print(f"Translated subtitles saved to: {translated_subtitle_path}")

    except (VideoDownloadError, SubtitleDownloadError, RuntimeError) as e:
        print(f"Error: {e}")
