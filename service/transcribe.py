"""
===============================================================
 Fichier        : transcribe.py
 Auteur         : Mohamed-Amine ELGAOUZI
 Description    : Transcrit des fichiers audio WAV en texte 
                  en utilisant le modèle local Faster Whisper.
                  Plus lent que AssemblyAI mais fonctionne localement.
 Créé le        : 16/10/2025
 Dernière maj   : 16/10/2025
===============================================================
 Dépendances    :
 - os
 - faster_whisper

 Fonctionnalités clés :
 - Transcription de fichiers WAV en texte
 - Modèle configurable (taille du modèle, CPU/GPU)
 - Sauvegarde des transcriptions dans 'data/transcripts'
 - Gestion des erreurs si transcription échoue ou fichier vide

 Notes :
 - Le fichier doit être préalablement traité (silence trimming) 
   et présent dans 'data/audio/processed'.
 - Plus lent que la transcription via AssemblyAI mais ne nécessite pas API KEY payante.
===============================================================
"""

import os
from faster_whisper import WhisperModel

PROCESSED_DIR = "data/audio/processed"
TRANSCRIPT_DIR = "data/transcripts"

def transcribe_audio(filename: str, model_size="medium") -> str:
    """
    Transcrit un fichier audio en texte en utilisant Faster Whisper local.
    
    Args:
        filename (str): Nom de base du fichier (sans extension).
        model_size (str): Taille du modèle Whisper ("tiny", "base", "small", "medium", "large").
    
    Returns:
        str: Chemin vers le fichier texte contenant la transcription.
    """
    os.makedirs(TRANSCRIPT_DIR, exist_ok=True)
    print("🚀 Starting transcription...")
    input_path = os.path.join(PROCESSED_DIR, f"{filename}.wav")
    output_path = os.path.join(TRANSCRIPT_DIR, f"{filename}.txt")

    # Utiliser device="cuda" si GPU disponible
    model = WhisperModel(model_size, device="cpu", compute_type="int8")

    segments, info = model.transcribe(input_path)

    with open(output_path, "w", encoding="utf-8") as f:
        for segment in segments:
            f.write(segment.text.strip() + " ")

    if not os.path.exists(output_path) or os.path.getsize(output_path) == 0:
        raise ValueError("Transcription failed or file is empty")

    return output_path
