import os
from faster_whisper import WhisperModel

#PROCESSED_DIR = "data/audio/processed"
PROCESSED_DIR = "data/audio/processed"
TRANSCRIPT_DIR = "data/transcripts"

def transcribe_audio(filename: str, model_size="small") -> str:
    os.makedirs(TRANSCRIPT_DIR, exist_ok=True)

    input_path = os.path.join(PROCESSED_DIR, f"{filename}.wav")
    output_path = os.path.join(TRANSCRIPT_DIR, f"{filename}.txt")

    # use device="cuda" if GPU available
    model = WhisperModel(model_size, device="cpu", compute_type="int8")

    segments, info = model.transcribe(input_path)

    with open(output_path, "w", encoding="utf-8") as f:
        for segment in segments:
            f.write(segment.text.strip() + " ")

    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
        raise ValueError("Transcription failed or file is empty")

    return output_path
