from deep_translator import GoogleTranslator
import uuid
import logging

def translate_subtitle(file_path: str, target_language: str = 'fr') -> str:
    """
    Translates a subtitle file to the specified language.

    Args:
        file_path (str): Path to the subtitle file (.srt).
        target_language (str): Target language for translation (e.g., 'fr' for French).

    Returns:
        str: Path to the translated subtitle file.
    """
    translator = GoogleTranslator(target=target_language)
    translated_lines = []

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        for line in lines:
            if line.strip() and not line.strip().isdigit() and '-->' not in line:
                # Translate subtitle lines
                translated_line = translator.translate(line.strip())
                translated_lines.append(translated_line)
            else:
                # Keep non-translatable lines (timestamps, empty lines, etc.)
                translated_lines.append(line.strip())

        # Generate a unique file name using uuidv4
        translated_file_name = str(uuid.uuid4())
        translated_file_path = file_path.replace('.srt', f'_{translated_file_name}.srt')

        with open(translated_file_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(translated_lines))

        logging.info("Translated subtitles saved to: %s", translated_file_path)
        return translated_file_path

    except Exception as e:
        logging.error("Translation failed: %s", e)
        raise RuntimeError(f"Translation failed: {e}")
