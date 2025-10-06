import re
import json
import os
from dotenv import load_dotenv
from openai import OpenAI

# Charger le fichier .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
# Initialiser le client OpenAI
client = OpenAI(api_key=api_key)

def extract_infos_from_text(transcript: str) -> dict:
    prompt = f"""
    Analyse la transcription suivante d’une conversation commerciale concernant un projet photovoltaïque.
    Extrait uniquement les informations demandées ci-dessous. 
    Si une information n’est pas présente, mets "inconnu".

    Format de sortie : JSON pur, avec les clés en snake_case.
    Ne mets pas de ```json, pas de markdown.
    Champs à extraire :
    - proprietaire : "oui" / "non"
    - situation_familiale : "celibataire" / "en_couple" / "inconnu"
    - age_monsieur : nombre ou "inconnu"
    - age_madame :  si mentionné → nombre sinon, si info indirecte → approx (ex: "<70", "plus_jeune_que_monsieur") sinon → "inconnu"
     toujours valider si <70 ans ou non  
    - superficie_maison : nombre en m² ou "inconnu"
    - mode_chauffage : "gaz" / "electricite" / "bois" / "autre" / "inconnu"
    - facture_plus_100euros : "oui" / "non" / "inconnu"
    - espace_toit_20m2 : "oui" / "non" / "inconnu"
    - adresse : texte (rue + numero + code_postal + ville ou "inconnu")
    - code_postal : nombre ou "inconnu"
    - activite_madame : "cdi" / "fonctionnaire" / "retraite" / "independant" / "autre" / "inconnu"
    - anciennete_independant_madame : ">3_ans" / "<=3_ans" / "inconnu" 
    (uniquement si activite_madame = "independant")

    - activite_monsieur : "cdi" / "fonctionnaire" / "retraite" / "independant" / "autre" / "inconnu"
    - anciennete_independant_monsieur : ">3_ans" / "<=3_ans" / "inconnu" 
    (uniquement si activite_monsieur = "independant")

    Voici la transcription :

    \"\"\" 
    {transcript}
    \"\"\"
    """

    response = client.chat.completions.create(
        model="gpt-4o-mini",  # rapide et économique
        messages=[{"role": "user", "content": prompt}],
        temperature=0
    )

    content = response.choices[0].message.content.strip()
    #cleaned = clean_json_output(content)

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        data = {"error": "Réponse LLM non valide", "raw": content}

    return data
