from service.yt_dlp_service import download_video, download_subtitles, VideoDownloadError, SubtitleDownloadError
from service.translate_service import translate_subtitle
import uuid

if __name__ == "__main__":
    base_dir = str(uuid.uuid4())
    video_url = "https://www.youtube.com/watch?v=W-PIcRurtfs&ab_channel=CTMI"

    try:
        # Step 1: Download Video
        video_result = download_video(video_url, file_dir=base_dir, file_format="mp4")
        print(f"Video Download Success: {video_result['success']}")
        print(f"Video File Path: {video_result['file_path']}")
        print(f"Video File Name: {video_result['file_name']}")

        # Step 2: Download Subtitles
        subtitle_path = download_subtitles(video_url, file_dir=base_dir)
        print(f"Subtitles downloaded to: {subtitle_path}")

        # Step 3: Translate Subtitles
        translated_subtitle_path = translate_subtitle(subtitle_path, target_language='fr')
        print(f"Translated subtitles saved to: {translated_subtitle_path}")

    except (VideoDownloadError, SubtitleDownloadError, RuntimeError) as e:
        print(f"Error: {e}")
