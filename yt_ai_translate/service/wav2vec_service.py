from transformers import Wav2Vec2Processor, Wav2Vec2ForCTC
import torchaudio
import torch
import logging

def transcribe_audio_wav2vec(audio_path: str, target_language: str = 'en') -> str:
    """
    Transcribes audio to text using a pre-trained Wav2Vec 2.0 model.

    Args:
        audio_path (str): Path to the audio file.
        target_language (str): Language code for transcription (default is 'en').

    Returns:
        str: Transcribed text.
    """
    try:
        # Load pre-trained model and processor
        model_name = f"facebook/wav2vec2-large-960h" if target_language == 'en' else f"facebook/wav2vec2-large-xlsr-53"
        processor = Wav2Vec2Processor.from_pretrained(model_name)
        model = Wav2Vec2ForCTC.from_pretrained(model_name)

        # Load and process audio
        waveform, sample_rate = torchaudio.load(audio_path)
        resampler = torchaudio.transforms.Resample(orig_freq=sample_rate, new_freq=16000)
        waveform = resampler(waveform).squeeze(0).numpy()

        # Tokenize and predict
        input_values = processor(waveform, return_tensors="pt", sampling_rate=16000).input_values
        logits = model(input_values).logits
        predicted_ids = torch.argmax(logits, dim=-1)

        # Decode prediction
        transcription = processor.decode(predicted_ids[0])
        logging.info("Transcription completed successfully.")
        return transcription

    except Exception as e:
        logging.error("Wav2Vec 2.0 transcription failed: %s", e)
        raise RuntimeError(f"Wav2Vec 2.0 transcription failed: {e}")
