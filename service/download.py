"""
===============================================================
 Fichier        : download.py
 Auteur         : Mohamed-Amine ELGAOUZI
 Description    : Télécharge les fichiers audio distants (MP3 ou WAV)
                  et les enregistre localement dans le dossier 
                  'data/audio/raw'. Gère automatiquement la conversion
                  d'URL MP3 vers WAV ORIG.
 Créé le        : 16/10/2025
 Dernière maj   : 16/10/2025
===============================================================
 Dépendances    :
 - os
 - requests

 Fonctionnalités clés :
 - Vérifie l'extension du fichier (MP3 ou WAV)
 - Rebasculer automatiquement les fichiers MP3 vers leur version WAV ORIG
 - Crée le répertoire de destination s’il n’existe pas
 - Télécharge le fichier en streaming et vérifie qu’il n’est pas vide

 Notes :
 - Utilisé par le pipeline de traitement audio avant transcription.
===============================================================
"""

import os
import requests

# Répertoire de destination des fichiers audio téléchargés
DATA_DIR = "data/audio/raw"

def download_audio(url: str, filename: str) -> str:
    os.makedirs(DATA_DIR, exist_ok=True)

    ext = os.path.splitext(url)[1].lower()  # get extension from url (.mp3 or .wav)
    
    if ext not in [".mp3", ".wav"]:
        raise ValueError("Unsupported file type")

    #  Construire l'URL ORIG en fonction de l'extension
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

    # Construire le chemin local du fichier
    filepath = os.path.join(DATA_DIR, filename + ext)

    # Télécharger le fichier en streaming
    response = requests.get(orig_url, stream=True)
    response.raise_for_status()  # raise error if request failed

    # Écrire le contenu dans le fichier local
    with open(filepath, "wb") as f:
        for chunk in response.iter_content(chunk_size=8192):
            f.write(chunk)

    # Vérifier que le fichier téléchargé n’est pas vide
    if os.path.getsize(filepath) == 0:
        raise ValueError("Downloaded file is empty")

    return filepath
