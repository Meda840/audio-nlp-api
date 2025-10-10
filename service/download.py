import os
import requests

DATA_DIR = "data/audio/raw"

def download_audio(url: str, filename: str) -> str:
    os.makedirs(DATA_DIR, exist_ok=True)

    ext = os.path.splitext(url)[1].lower()  # get extension from url (.mp3 or .wav)
    
    if ext not in [".mp3", ".wav"]:
        raise ValueError("Unsupported file type")

     # Build ORIG URL based on extension
    if ext == ".mp3":
        orig_url = url.replace("/MP3/", "/ORIG/").replace(".mp3", ".wav")
        ext = ".wav"  # force WAV extension
    elif ext == ".wav":
        # Insert /ORIG/ if not already in URL
        if "/ORIG/" not in url:
            orig_url = url.replace("/RECORDINGS/", "/RECORDINGS/ORIG/")
        else:
            orig_url = url
    else:
        orig_url = url

    filepath = os.path.join(DATA_DIR, filename + ext)

    response = requests.get(orig_url, stream=True)
    response.raise_for_status()  # raise error if request failed

    with open(filepath, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    if os.path.getsize(filepath) == 0:
        raise ValueError("Downloaded file is empty")

    return filepath
