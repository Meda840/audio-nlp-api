"""
===============================================================
 Fichier        : file_cleanup.py
 Auteur         : Mohamed-Amine ELGAOUZI
 Description    : Supprime automatiquement les fichiers audio
                  anciens dans les dossiers 'raw' et 'processed'.
                  Utilisé en tâche cron pour maintenir le stockage propre.
 Créé le        : 15/10/2025
 Dernière maj   : 16/10/2025
===============================================================
 Dépendances    :
 - os
 - logging
 - datetime

 Fonctionnalités clés :
 - Parcourt les dossiers audio
 - Supprime les fichiers plus vieux que 2 heures
 - Log chaque suppression ou erreur dans un fichier de log

 Notes :
 - Ce script est exécuté via une tâche cron toutes les soirs.
===============================================================
"""

import os
import logging
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
if not logger.handlers:
    ch = logging.StreamHandler()
    ch.setFormatter(logging.Formatter('[%(asctime)s] %(levelname)s: %(message)s'))
    logger.addHandler(ch)

#os.chdir("/home/mohamed-amine/Desktop/audio-nlp-api") #local server
os.chdir("/home/m.elgaouzi/audio-nlp-api") # live server

def cleanup_audio_files( raw_dir: str = "data/audio/raw",processed_dir: str = "data/audio/processed",older_than_hours: int = 2) -> None:
    """
    Delete audio files older than X hours from raw and processed directories.
    Logs success and failures without interrupting workflow.
    """
    print("hello")
    cutoff_time = datetime.now().timestamp() - (older_than_hours * 3600)
    dirs = [raw_dir, processed_dir]

    for directory in dirs:
        if not os.path.exists(directory):
            continue

        for file in os.listdir(directory):
            file_path = os.path.join(directory, file)
            try:
                if os.path.isfile(file_path):
                    last_modified = os.path.getmtime(file_path)
                    if last_modified < cutoff_time:
                        os.remove(file_path)
                        logger.info(f"✅ Deleted old file: {file_path}")
            except Exception as e:
                logger.error(f"❌ Failed to delete {file_path}: {e}")

if __name__ == "__main__":
    cleanup_audio_files()
