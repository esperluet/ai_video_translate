import os
import uuid
import logging
from moviepy import VideoFileClip
import whisper

# Configure logging
logging.basicConfig(level=logging.INFO)

import torch
from transformers import AutoModelForSpeechSeq2Seq, AutoProcessor, pipeline
from datasets import load_dataset


device = "cuda:0" if torch.cuda.is_available() else "cpu"
torch_dtype = torch.float16 if torch.cuda.is_available() else torch.float32

model_id = "openai/whisper-large-v3"

model = AutoModelForSpeechSeq2Seq.from_pretrained(
    model_id, torch_dtype=torch_dtype, low_cpu_mem_usage=True, use_safetensors=True
)
model.to(device)

processor = AutoProcessor.from_pretrained(model_id)

pipe = pipeline(
    "automatic-speech-recognition",
    model=model,
    tokenizer=processor.tokenizer,
    feature_extractor=processor.feature_extractor,
    torch_dtype=torch_dtype,
    device=device,
)

def extract_audio_from_video(video_path: str, output_dir: str) -> str:
    """
    Extracts audio from a video file and saves it as a WAV file.

    Args:
        video_path (str): Path to the input video file.
        output_dir (str): Directory where the extracted audio will be saved.

    Returns:
        str: Path to the extracted audio file in WAV format.
    """
    os.makedirs(output_dir, exist_ok=True)
    audio_output_path = os.path.join(output_dir, f"{uuid.uuid4()}.wav")
    with VideoFileClip(video_path) as video:
        audio = video.audio
        audio.write_audiofile(audio_output_path, codec='pcm_s16le', fps=16000)
    logging.info(f"Extracted audio to WAV format: {audio_output_path}")
    return audio_output_path

def transcribe_audio_to_srt(audio_path: str, target_dir: str, model_size: str = 'base') -> str:
    """
    Transcribes audio to text using OpenAI's Whisper model and generates an SRT file.

    Args:
        audio_path (str): Path to the audio file.
        target_dir (str): Directory where the SRT file will be saved.
        model_size (str): Size of the Whisper model to use (e.g., 'tiny', 'base', 'small', 'medium', 'large').

    Returns:
        str: Full path to the generated SRT file.
    """
    try:
        # Ensure the target directory exists
        os.makedirs(target_dir, exist_ok=True)

        result = pipe(audio_path, return_timestamps=True)

        print(result)

        # Generate SRT file
        srt_file_name = f"{uuid.uuid4()}.srt"
        srt_file_path = os.path.join(target_dir, srt_file_name)

        with open(srt_file_path, 'w', encoding='utf-8') as srt_file:
            for segment in result['segments']:
                start_time = segment['start']
                end_time = segment['end']
                text = segment['text'].strip()
                srt_file.write(f"{segment['id'] + 1}\n")
                srt_file.write(f"{format_srt_time(start_time)} --> {format_srt_time(end_time)}\n")
                srt_file.write(f"{text}\n\n")

        logging.info(f"SRT file generated: {srt_file_path}")
        return srt_file_path

    except Exception as e:
        logging.error(f"Failed to generate SRT: {e}")
        raise RuntimeError(f"Failed to generate SRT: {e}")

def format_srt_time(seconds: float) -> str:
    """
    Converts seconds to SRT timestamp format.

    Args:
        seconds (float): Time in seconds.

    Returns:
        str: Time in SRT timestamp format (HH:MM:SS,ms).
    """
    milliseconds = int((seconds % 1) * 1000)
    seconds = int(seconds)
    minutes = seconds // 60
    seconds = seconds % 60
    hours = minutes // 60
    minutes = minutes % 60
    return f"{hours:02}:{minutes:02}:{seconds:02},{milliseconds:03}"

