"""
===============================================================
 Fichier        : transcribeAssembly.py
 Auteur         : Mohamed-Amine ELGAOUZI
 Description    : Transcrit des fichiers audio WAV en texte 
                  en utilisant l'API AssemblyAI.
                  Le transcript est sauvegardé dans 'data/transcripts'.
 Créé le        : 16/10/2025
 Dernière maj   : 16/10/2025
===============================================================
 Dépendances    :
 - os
 - assemblyai
 - dotenv

 Fonctionnalités clés :
 - Transcription de fichiers WAV en français
 - Détection des locuteurs (speaker_labels)
 - Punctuation automatique et formatage du texte
 - Gestion des erreurs et retour de l'exception en cas d'échec
 - Sauvegarde des transcriptions dans un dossier dédié

 Notes :
 - Le fichier doit être préalablement traité dans (silence_trimmer.py) 
   et présent dans 'data/audio/processed'.
===============================================================
"""
import os
import assemblyai as aai
from dotenv import load_dotenv

PROCESSED_DIR = "data/audio/processed"
TRANSCRIPTS_DIR = "data/transcripts"
# Charger le fichier .env
load_dotenv()
API_KEY = os.getenv("ASSEMBLY_AI_KEY")

# Configure API key
aai.settings.api_key = API_KEY

def transcribe_with_assemblyai(filename: str) -> str:
    """
    Transcribe an audio file using AssemblyAI API.
    
    Args:
        filename (str): Base filename (without extension).
    
    Returns:
        str: Path to transcript text file.
    """
    os.makedirs(TRANSCRIPTS_DIR, exist_ok=True)

    # Build input file path (look for .wav in processed dir)
    input_path = os.path.join(PROCESSED_DIR, f"{filename}.wav")

    if not os.path.exists(input_path):
        raise FileNotFoundError(f"Processed file not found: {input_path}")

  # Configure transcription
    config = aai.TranscriptionConfig(
        speaker_labels=True,
        format_text=True,
        punctuate=True,
        speech_model=aai.SpeechModel.best,
        language_code="fr"  
    )

    # Run transcription
    print(f"🔊 Sending {input_path} to AssemblyAI for transcription (FR)...")

    transcript = aai.Transcriber(config=config).transcribe(input_path)

    if transcript.status == "error":
        raise RuntimeError(f"❌ Transcription failed: {transcript.error}")

    # Save transcript
    output_path = os.path.join(TRANSCRIPTS_DIR, f"{filename}.txt")
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(transcript.text)

    print(f"✅ Transcript saved at {output_path}")
    return output_path
