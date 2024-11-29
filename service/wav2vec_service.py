import os
import uuid
import logging
import torch
import torchaudio
from pydub import AudioSegment
from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC

# Configure logging
logging.basicConfig(level=logging.INFO)

def convert_to_wav(input_audio_path: str, output_dir: str) -> str:
    """
    Converts an audio file to WAV format using pydub.

    Args:
        input_audio_path (str): Path to the input audio file (e.g., .mp3).
        output_dir (str): Directory where the WAV file will be saved.

    Returns:
        str: Path to the converted WAV file.
    """
    os.makedirs(output_dir, exist_ok=True)
    output_audio_path = os.path.join(output_dir, f"{uuid.uuid4()}.wav")
    audio = AudioSegment.from_file(input_audio_path)
    audio = audio.set_frame_rate(16000).set_channels(1)  # Set to 16 kHz mono
    audio.export(output_audio_path, format="wav")
    logging.info(f"Converted audio to WAV format: {output_audio_path}")
    return output_audio_path

def generate_srt_timestamps(transcription: str, duration: float, max_chars_per_line: int = 40) -> list:
    """
    Splits the transcription into lines and generates timestamps for an SRT file.

    Args:
        transcription (str): The transcribed text.
        duration (float): Duration of the audio in seconds.
        max_chars_per_line (int): Maximum number of characters per subtitle line.

    Returns:
        list: List of subtitle entries with index, start time, end time, and text.
    """
    words = transcription.split()
    subtitles = []
    index = 1
    words_per_second = len(words) / duration
    current_words = []
    start_time = 0.0

    for word in words:
        current_words.append(word)
        line_length = len(" ".join(current_words))
        if line_length >= max_chars_per_line or word == words[-1]:
            end_time = start_time + len(current_words) / words_per_second
            text = " ".join(current_words)
            subtitles.append((index, start_time, end_time, text))
            index += 1
            current_words = []
            start_time = end_time

    return subtitles

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

def transcribe_and_generate_srt(audio_path: str, target_dir: str, target_language: str = 'en') -> str:
    """
    Transcribes audio to text using a pre-trained Wav2Vec 2.0 model and generates an SRT file.

    Args:
        audio_path (str): Path to the audio file.
        target_dir (str): Directory where the SRT file will be saved.
        target_language (str): Language code for transcription (default is 'en').

    Returns:
        str: Full path to the generated SRT file.
    """
    try:
        # Ensure the target directory exists
        os.makedirs(target_dir, exist_ok=True)

        # Convert audio to WAV format
        logging.info("Converting audio to WAV format for compatibility.")
        wav_path = convert_to_wav(audio_path, target_dir)

        # Load pre-trained model and processor
        model_name = f"facebook/wav2vec2-large-960h" if target_language == 'en' else f"facebook/wav2vec2-large-xlsr-53"
        processor = Wav2Vec2Processor.from_pretrained(model_name)
        model = Wav2Vec2ForCTC.from_pretrained(model_name)

        # Load and process audio
        waveform, sample_rate = torchaudio.load(wav_path)
        duration = waveform.size(1) / sample_rate
        input_values = processor(waveform.squeeze(), return_tensors="pt", sampling_rate=16000).input_values

        # Perform transcription
        with torch.no_grad():
            logits = model(input_values).logits
        predicted_ids = torch.argmax(logits, dim=-1)
        transcription = processor.batch_decode(predicted_ids)[0]
        logging.info("Transcription completed successfully.")

        # Generate SRT subtitles
        subtitles = generate_srt_timestamps(transcription, duration)
        srt_file_name = f"{uuid.uuid4()}.{target_language}.srt"
        srt_file_path = os.path.join(target_dir, srt_file_name)

        with open(srt_file_path, 'w', encoding='utf-8') as file:
            for index, start_time, end_time, text in subtitles:
                file.write(f"{index}\n")
                file.write(f"{format_srt_time(start_time)} --> {format_srt_time(end_time)}\n")
                file.write(f"{text}\n\n")

        logging.info(f"SRT file generated: {srt_file_path}")
        return srt_file_path

    except Exception as e:
        logging.error(f"Failed to generate SRT: {e}")
        raise RuntimeError(f"Failed to generate SRT: {e}")
