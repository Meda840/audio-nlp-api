import os
import subprocess

PROCESSED_DIR = "data/audio/processed"

def convert_to_wav(input_path: str, filename: str) -> str:
    os.makedirs(PROCESSED_DIR, exist_ok=True)

    ext = os.path.splitext(input_path)[1].lower()
    output_path = os.path.join(PROCESSED_DIR, f"{filename}.wav")

    if ext == ".wav":
        # 🔎 Vérifier si déjà en 16kHz mono
        # ffprobe serait plus précis, mais on simplifie ici
        if os.path.abspath(input_path) != os.path.abspath(output_path):
            # Copier le fichier sans reconversion
            import shutil
            shutil.copy(input_path, output_path)
        return output_path

    # Si ce n’est pas un WAV, on convertit avec ffmpeg
    subprocess.run([
        "ffmpeg", "-y", "-i", input_path,
        "-ar", "16000", "-ac", "1",  # 16kHz, mono
        output_path
    ], check=True)

    return output_path
