import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from service.download import download_audio
from service.convert import convert_to_wav
from service.transcribe import transcribe_audio
from service.transcribeAssembly import transcribe_with_assemblyai
from service.extract_infos import extract_infos_from_text

app = FastAPI()
PHP_API_URL = "http://ghandi.local/fiche_ai_data_post.php"

@app.get("/health")
def health_check():
    return {"status": "ok"}

class DownloadRequest(BaseModel):
    fiche_id: int
    audio_url: str

@app.post("/download")
def download_file(request: DownloadRequest):
    fiche_id = request.fiche_id
    url = request.audio_url
    filename = f"{fiche_id}_audiotranscribed"
    
    # Step 1: Download
    raw_path = download_audio(url, filename)
    # Step 2: Convert
    wav_path = convert_to_wav(raw_path, filename)
    # Step 3: Transcribe
    #transcript_path = transcribe_audio(filename)
    transcript_path = transcribe_with_assemblyai(filename)

    # Step 4: Lire le fichier texte
    with open(transcript_path, "r", encoding="utf-8") as f:
        transcript_text = f.read()
    print("Calling Open AI API to extract info")
    # Step 5: Envoyer à OpenAI pour extraction des infos
    extracted_infos = extract_infos_from_text(transcript_text)
    print("Sending Data to PHP server ")
    # Step 6: Send to PHP backend
    backend_response = send_ai_data_to_php(fiche_id, extracted_infos)

# Step 7: Return summary
    return {
        "status": "success",
        "fiche_id": fiche_id,
        "filename": filename,
        "extracted_infos": extracted_infos,
        "backend_response": backend_response,
    }

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
        "client_city_data_ia": extracted_data.get("client_city_data_ia", None),
        "client_address_data_ia": extracted_data.get("adresse", None),
        "client_postal_code_data_ia": extracted_data.get("code_postal", None),
        "proprietaire_data_ia": extracted_data.get("proprietaire", None),
        "mode_chauffage_data_ia": extracted_data.get("mode_chauffage", None),
        "facture_data_ia": extracted_data.get("facture_plus_100euros", None),
        "mensuelle_annuelle_data_ia": extracted_data.get("mensuelle_annuelle", None),
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
        "commentaire_client_suggestion_ia": extracted_data.get("commentaire_client_suggestion_ia", None),
    }

    try:
        response = requests.post(url, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()  # Expecting JSON response from PHP
    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=500, detail=f"Failed to send data to PHP: {e}")
    except json.JSONDecodeError:
        raise HTTPException(status_code=500, detail="PHP backend returned invalid JSON")

