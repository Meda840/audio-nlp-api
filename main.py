"""
===============================================================
 Fichier        : main.py
 Auteur         : Mohamed-Amine ELGAOUZI
 Description    : API FastAPI principale pour :
                  - Téléchargement de fichiers audio depuis une URL
                  - Nettoyage audio (suppression des silences)
                  - Transcription audio (AssemblyAI)
                  - Extraction d'informations via OpenAI
                  - Envoi automatique des données extraites vers backend PHP
                  Utilise BackgroundTasks pour traitement asynchrone.
 Créé le        : 15/10/2025
 Dernière maj   : 16/10/2025
===============================================================
 Dépendances    :
 - requests
 - fastapi
 - pydantic
 - dotenv
 - os
 - traceback
 - service.download
 - service.convert
 - service.transcribe
 - service.transcribeAssembly
 - service.extract_infos
 - utils.silence_trimmer

 Fonctionnalités clés :
 - Endpoint GET /health pour vérifier l'état de l'API
 - Endpoint POST /process pour lancer le traitement audio
 - Téléchargement de l'audio
 - Nettoyage automatique des silences
 - Transcription via AssemblyAI
 - Extraction et structuration des informations
 - Envoi des résultats au backend PHP défini dans .env
 - Gestion des erreurs et logging console

 Notes :
 - Les variables d'environnement doivent être définies dans le fichier .env
 - Le traitement est lancé en Background pour ne pas bloquer l'API
===============================================================
"""

import requests
from fastapi import FastAPI, HTTPException, BackgroundTasks
from pydantic import BaseModel
from service.download import download_audio
from service.convert import convert_to_wav
from service.transcribe import transcribe_audio
from service.transcribeAssembly import transcribe_with_assemblyai
from service.extract_infos import extract_infos_from_text
from utils.silence_trimmer import trim_silence

import traceback
from dotenv import load_dotenv
import os


app = FastAPI()
load_dotenv()
PHP_API_URL = os.getenv("php_api_url")

@app.get("/health")
def health_check():
    return {"status": "ok"}

class DownloadRequest(BaseModel):
    fiche_id: int
    audio_url: str

# ✅ Extract data and send to php server
def send_ai_data_to_php(fiche_id: int, extracted_data: dict) -> dict:
    """
    Sends AI-extracted data to the PHP backend.
    Returns backend response or raises an HTTPException on error.
    """
     # Append fiche_id to the URL
    url = f"{PHP_API_URL}?fiche_id={fiche_id}"
    # Prepare payload (PHP reads POST data)
    payload = {
        "fiche_id": fiche_id,
        "client_first_name_data_ia": extracted_data.get("client_first_name_data_ia", None),
        "client_last_name_data_ia": extracted_data.get("client_last_name_data_ia", None),
        "client_phone_number": extracted_data.get("client_phone_number", None),
        "client_city_data_ia": extracted_data.get("ville", None),
        "client_address_data_ia": extracted_data.get("adresse", None),
        "client_postal_code_data_ia": extracted_data.get("code_postal", None),
        "adresse_modifiee": extracted_data.get("adresse_modifiee", None),
        "proprietaire_data_ia": extracted_data.get("proprietaire", None),
        "mode_chauffage_data_ia": extracted_data.get("mode_chauffage", None),
        "facture_data_ia": extracted_data.get("facture_electricite", None),
        "mensuelle_annuelle_data_ia": extracted_data.get("type_facturation", None),
        "superficie_data_ia": extracted_data.get("superficie_maison", None),
        "toiture_data_ia": extracted_data.get("toiture",None),
        "orientation_data_ia": extracted_data.get("orientation", None),
        "20m_data_ia": extracted_data.get("espace_toit_20m2", None),
        "age_mr_data_ia": extracted_data.get("age_monsieur", None),
        "age_mme_data_ia": extracted_data.get("age_madame", None),
        "situation_familiale_data_ia": extracted_data.get("situation_familiale", None),
        "activite_mr_data_ia": extracted_data.get("activite_monsieur", None),
        "activite_mme_data_ia": extracted_data.get("activite_madame", None),
        "revenu_data_ia": extracted_data.get("revenu", None),
        "tel2_data_ia": extracted_data.get("tel2", None),
        "creneau_rappel_data_ia": extracted_data.get("creneau_rappel", None),
        "heure_rappel_data_ia": extracted_data.get("heure_rappel", None),
        "entretien_data_ia": extracted_data.get("entretien", None),
        "commentaire_suggestion_ia": extracted_data.get("commentaire_suggestion_ia", None),
        "score_interet": extracted_data.get("score_interet", None),
        "classement": extracted_data.get("classement", None),
        "interet_exprime": extracted_data.get("interet_exprime", None),
        "disponibilite": extracted_data.get("disponibilite", None),
        "infos_collectees": extracted_data.get("infos_collectees", None),
        "objections": extracted_data.get("objections", None),
        "analyse_agent": extracted_data.get("analyse_agent", None),
        "recommandations_qualiticien": extracted_data.get("recommandations_qualiticien", None),

    }

    print(f"here is data sent {payload}")

    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()  # Expecting JSON response from PHP
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to send data to PHP: {e}")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="PHP backend returned invalid JSON")

def process_fiche_in_background(fiche_id: int, audio_url: str):
    try:
        print(f"🎧 Processing fiche {fiche_id} in background...")

        filename = f"{fiche_id}_audiotranscribed"

        # Step 1: Download
        raw_path = download_audio(audio_url, filename)
        print(raw_path)

        # Step 2 : trim audio to cut when audio is silenced
        wave_path = trim_silence(raw_path)

        # Step 3: Transcribe
        transcript_path = transcribe_with_assemblyai(filename)

        # Step 4: Read transcript
        with open(transcript_path, "r", encoding="utf-8") as f:
            transcript_text = f.read()

        # Step 5: Extract infos with OpenAI
        extracted_infos = extract_infos_from_text(transcript_text)

        # Step 6: Send to PHP backend
        backend_response = send_ai_data_to_php(fiche_id, extracted_infos)

        print(f"✅ Background processing finished for fiche {fiche_id}")
        print(f"➡️ PHP backend response: {backend_response}")

    except Exception as e:
        print(f"❌ Error processing fiche {fiche_id}: {e}")

# ✅ Main endpoint — triggers background task
@app.post("/process")
def download_file(request: DownloadRequest, background_tasks: BackgroundTasks):
    fiche_id = request.fiche_id
    audio_url = request.audio_url

    print(f"📥 Queuing fiche {fiche_id} for background processing...")

    # Schedule background task
    background_tasks.add_task(process_fiche_in_background, fiche_id, audio_url)

    return {
        "status": "queued",
        "fiche_id": fiche_id,
        "message": "Processing started in background. Results will be sent to PHP when ready."
    }