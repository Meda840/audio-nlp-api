import os
import requests

DATA_DIR = "data/audio/raw"

def download_audio(url: str, filename: str) -> str:
    os.makedirs(DATA_DIR, exist_ok=True)

    ext = os.path.splitext(url)[1]  # get extension from url (.mp3 or .wav)
    if ext not in [".mp3", ".wav"]:
        raise ValueError("Unsupported file type")

    filepath = os.path.join(DATA_DIR, filename + ext)

    response = requests.get(url, stream=True)
    response.raise_for_status()  # raise error if request failed

    with open(filepath, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    if os.path.getsize(filepath) == 0:
        raise ValueError("Downloaded file is empty")

    return filepath
