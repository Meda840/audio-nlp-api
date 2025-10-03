from fastapi import FastAPI
from service.download import download_audio
from service.convert import convert_to_wav
from service.transcribe import transcribe_audio
from service.transcribeAssembly import transcribe_with_assemblyai

app = FastAPI()

@app.get("/health")
def health_check():
    return {"status": "ok"}

@app.get("/download")
def download_file(url: str, filename: str):
    # Step 1: Download
    raw_path = download_audio(url, filename)
    # Step 2: Convert
    wav_path = convert_to_wav(raw_path, filename)
    # Step 3: Transcribe
    #transcript_path = transcribe_audio(filename)
    transcript_path = transcribe_with_assemblyai(filename)
    return {
        "filename": filename,
        "raw_file": raw_path,
        "processed_file": wav_path,
        "transcript_file": transcript_path
    }