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
    Tu es un assistant expert en qualification d'appels commerciaux pour des projets photovoltaïques.
    Ton rôle est de lire la transcription d’un appel et d’en extraire les informations demandées ci-dessous 
    comme le ferait un qualiticien humain. 
    Réponds toujours en JSON valide **sans markdown, sans texte explicatif**, avec les clés en snake_case.
    Utilise les indices du dialogue pour déduire les informations implicites.
    Si une information est absente, écris "inconnu".

    ## Informations à extraire :

    - proprietaire : "oui" / "non"
    - situation_familiale : "celibataire" / "en couple" / "veuf" / "divorce" / "inconnu"
    - age_monsieur : nombre / "<70" / ">70" / "inconnu"
    - age_madame : nombre / "<70" / ">70" / "inconnu"
    - superficie_maison : nombre (m²) ou "inconnu"
    - mode_chauffage : texte exact (ex: "gaz", "électricité", "bois", "fuel", "pompe à chaleur", "pellet", "mixte", etc.)
    - facture_electricite : 
        - Si un montant est dit : nombre (ex: 120)
        - Sinon : "plus_de_100" / "moins_de_100" / "inconnu"
    - type_facturation : "mensuelle" / "annuelle" / "inconnu"
    - toiture : texte exact (ex: "tuiles", "ardoises", "terrasse", "bac acier", "inconnu")
    - orientation : texte exact ("sud", "est", "ouest", "est-ouest", "nord", "bien ensoleillée","inconnu", etc.)
    - espace_toit_20m2 : "20m" / "moins de 20m" / "inconnu" 
    - adresse : texte complet si mentionné
    - code_postal : nombre ou "inconnu"
    - ville : nom de la ville si identifiable
    - activite_monsieur : 
        - Si salarié → domaine ou métier précis (ex: "bâtiment", "santé", "chauffeur", "enseignant", etc.) ou CDI
        - Si retraité → "retraité"
        - Si au chômage → "sans emploi"
        - Si indépendant → écrire "indépendant (>3 ans)" ou "indépendant (<=3 ans)" selon ce qui est dit
        - Sinon "inconnu"
    - activite_madame : même logique que pour monsieur
    - revenu : montant mensuel si mentionné, sinon "inconnu"
    - tel2 : autre numéro mentionné, sinon "inconnu"
    - creneau_rappel : si le client donne une préférence d’heure (matin, après-midi, etc.)
    - heure_rappel : si une heure précise est mentionnée

    ### 🧩 Exemples attendus

    **Exemple 1**
    Transcription : "On paie environ 120 euros d'électricité par mois, c’est mensuel."
    →
    "facture_electricite": 120, "type_facturation": "mensuelle"

    **Exemple 2**
    Transcription : "Notre toiture est en tuiles, bien orientée plein sud."
    →
    "toiture": "tuiles", "orientation": "sud"

    **Exemple 3**
    Transcription : "Je suis infirmière, mon mari est retraité."
    →
    "activite_madame": "cdi santé", "activite_monsieur": "retraité"

    **Exemple 4**
    Transcription : "Je suis artisan depuis 5 ans, ma femme est auto-entrepreneuse depuis deux ans."
    →
    "activite_monsieur": "indépendant (>3 ans)", "activite_madame": "indépendant (<=3 ans)"

    **Exemple 5**
    Transcription : "On gagne environ 2500 euros à deux."
    →
    "revenu": 2500

    ---

    Analyse maintenant la transcription suivante :

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

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        data = {"error": "Réponse LLM non valide", "raw": content}

    return data
