import re
import json
import os
from dotenv import load_dotenv
from openai import OpenAI

sales_script ="""
bonjour, Mr ou Mme Dupond Rémi? c'est Adnan/sara du service ENR( du bureau d'etude RGE) ----
( Rassurez vous il ne s'agit ni d'une démarche commerciale ni publicitaire, Pour cela vous êtes toujours propriétaire de votre maison individuelle dans le département X ) OU
( Je vous appel dans le cadre d'une étude à l'échelle national pour la sensibilisation aux énergies vertes, dans le département X, 
vous êtes toujours propirétaire de votre maison individuelle dans le départment X?) 
---- Trés bien alors suite aux augmentations qu'on subit vos factures d'énergies ces dernières années nous avons mis en place des études téléphonqiues gratuires
pour voir comment les réduire considérabelemnt (ou jusqu'a 90%). Pour cela un conseiller RGE( reconnu garant de l'environnement) va vous rappeler afin de vérifier
si le projet des panneaux photovoltaiques est realisable chez vous et surtout s'il peu etre autofinancer sans toucher à votre pouvoir d'achat 
(ou sans dépasser le montant de la facture que vous payez actuellement). Vous pourrez ainsi produire de l'electricité verte pour votre propre consommation
ce qui réduira vos factures et vous rendra autonome, un atout précieux face au conexte actuel de crise énérgétique mondiale;
--- 1. Quel est votre mode de chauffage? 2. Comme la majorité des foyers francais ont une facture qui dépasse les 100€ par mois est-ce-que c'est le cas pour vous?
3. Votre toiture est Orientée EST-OUEST ou plein SUD? Bien ensoleillé? 
4. Donc sur la partie ensoleillée de votre toiture, Vous pensez avoir 20 m2 dégagée sans Obstables ni de velux ni de chiens assis et sans ombrage? c'est lequivalent de 4 m sur 5 a vue d'oeil) 
5. d'apres votre jeune voix vous avez quel âge ? Et pour Mme/Mr si vous êtes en couple? 5.1 : Situation familiale : 
6. Et vous êtes dans quel domaine d'activité? (Mr et Mme) 7. Sans me communiquer un chiffre exact est ce que vous avez un revenu égal ou supérieur à ?
8. Alors on a fini, je vous remercie de votre partience, vous allez recevoir un sms avec un code confidentiel pour éviter tout démarchage téléphonique ou arnaque, 
notre conseiller vous communiquera ce code afin de s'identifier et il répondra à toutes vos questionns et verifiera si le projet peut s'autofinancer 
et nous comptons sur vous pour etre attentif/ve à ses explications. Pour cela vous serez bien d'accord de bénéficier d'une étude personnalisée de Notre Bureau d'étude Local RGE?
Nb: vérifier l'adresse exacte : (votre code postal en premier, et la commune et l'adresse exacte, vous êtes sur quel chemin, rue ou route etc... et le numéro de la maison) 
Alors c'est bien à cette adresse que vous êtes propritaire de votre maison individuelle ?  Verification du nom et prenom.
"""


# Charger le fichier .env
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
# Initialiser le client OpenAI
client = OpenAI(api_key=api_key)

def extract_infos_from_text(transcript: str) -> dict:
    prompt = f"""
    Tu es un assistant expert en qualification d'appels commerciaux pour des projets photovoltaïques.
    Tu connais parfaitement le script de vente suivant (conserve-le en mémoire et utilise-le comme contexte de référence) :
    \"\"\"
    {sales_script}
    \"\"\"

    Ta mission :
    - Lire la transcription ci-dessous
    - Inférer les réponses même implicites en t’appuyant sur le script et le contexte typique de ces appels
    - Réponds toujours en JSON valide **sans markdown, sans texte explicatif**, avec les clés en snake_case.
    - Remplir les champs demandés ci-dessous avec les valeurs attendues

     ## Règles pour le commentaire_suggestion_ia :
    - Toujours suivre cet ordre et séparateur " / " :
      script ok / verrouillage ok / proprietaire oui/non / facture (montant ou estimation) / superficie (m²) / toit (type) / orientation / espace_20m2 / age_mr / age_mme / activite_mr / activite_mme / revenu / Q_interet / adresse / note / observation
    - Si une information est absente → mettre "-"
    - Ne rien inventer, se baser uniquement sur la transcription
    - Reformuler les fautes ou termes approximatifs pour avoir un texte clair
    - Indiquer si l'appel semble intéressant, moyennement intéressant, ou non intéressant
    - Les observations peuvent inclure : obstacles sur le toit, informations manquantes, particularités du client, etc.
     ## Exemples de commentaire_suggestion_ia :
    1. script ok / verrouillage ok / proprietaire oui / facture 700£ / superficie 500M² / toit en ardoise / orientation plein sud / 20M² oui / mr 60 et mme 60 / mr et mme liberaux plus de 3 ans / revenu sup à 2000£ / Q d'interet mr dit oui / adresse 24 rue Belle Epine, 37700 Tours / note 10 / mr semble moyennement intéressé
    2. script ok / verrouillage ok / proprietaire oui / facture 120£ / superficie 130M² / toit plat / orientation bien ensoleillée / 20M² non / mr 40 et mme 34 / mr et mme en cdi / revenu estimé "-" / Q d'interet mr dit d'accord / adresse 1 Chemin Youri Gagarine, 49500 Segré-en-Anjou Bleu / note 1 / mr semble intéressé
    3. script ok / verrouillage ok / proprietaire oui / facture "-" / superficie 300 M² / toit en ardoise / orientation sud / 20M² oui / mr 72 et mme 52 / mr retraité et mme fonctionnaire / revenu sup à 1600£ / Q d'interet mr dit oui / adresse 32 Route de Castillon, 09200 Moulis / note 8 / mr semble intéressé

    ## Champs à extraire :
    - proprietaire : "oui" / "non"
    - situation_familiale : "celibataire" / "en couple" / "veuf" / "divorce" / "-"
    - age_monsieur : nombre / "<70" / ">70" / "-"
    - age_madame : nombre / "<70" / ">70" / "-"
    - superficie_maison : nombre (m²) ou "-"
    - mode_chauffage : texte exact Si la transcription contient une faute ou un mot proche d’un type valide, corrige-le vers le terme exact.
    - facture_electricite : montant en nombre si mentionné, sinon "plus_de_100","entre 80 et 100" "moins_de_80" ou "-"
    - type_facturation : 
        - "mensuelle" si le montant < 300 €,
        - "annuelle" si le montant ≥ 300 €,
        - "-" sinon
    - toiture : texte exact ("tuiles", "ardoises", "terrasse", "bac acier", "inconnu", etc.)
    - orientation :
        - "sud", "est", "ouest", "est-ouest", "nord", "bien ensoleillée", ou "-"
        - Si la personne ne sait pas, répondre "-"
    - espace_toit_20m2 :
        - "20m" si la toiture semble dégagée
        - "moins de 20m" s’il y a des obstacles et le client mentionne que c'est moins de 20m
        - "-" si aucune info claire
    - adresse : texte complet si mentionné
    - code_postal : nombre de xxxxx ou "-"
    - ville : nom si identifiable
    - adresse_modifiee :
        Retourner 1 si dans la transcription le client dit ou laisse comprendre que :
        * l’adresse annoncée par le commercial n’est pas correcte
        * il a déménagé ou habite ailleurs maintenant
        * le numéro de rue, la rue ou la ville ne correspondent pas
        Retourner 0 si aucune contradiction ou changement n’est mentionné
        Retourner 0 si aucune information claire sur l’adresse
    - activite_monsieur : voir règles dans le script.Si salarié repondre CDI, Si "libéral" ou "indépendant", inclure ancienneté : 
        - Si le client mentionne "libéral" ou "indépendant", vérifier si le transcript indique depuis combien de temps.
        - Si 3 ans ou plus → renvoyer "indépendant (plus de 3 ans)"
        - Si moins de 3 ans → renvoyer "indépendant (moins de 3 ans)"
        - Si aucune info sur la durée → renvoyer "indépendant"
    - activite_madame : même logique
    - revenu : montant mensuel si mentionné, sinon "-"
    - tel2 : autre numéro mentionné, sinon "-"
    - creneau_rappel : si le client donne une préférence (matin, après-midi…)
    - heure_rappel : si une heure précise est mentionnée
    - commentaire_suggestion_ia : suivre Règles pour le commentaire_suggestion_ia et les exemples donnés
     Astuce pour toi :
    - Le script sert de repère : si une information est implicite (ex: montant de facture typique), infère-la.
    - Si orientation ou surface du toit ne sont pas claires → "inconnu" proprement, ne pas inventer.
    - Pour facture : applique strictement la règle mensuelle/annuelle selon montant.
    - Si conjoint est mentionnée comme propriétaire (ex : “c’est madame”), considérer `proprietaire = "oui"`.
    - Si le locuteur mentionne “madame”, “mon mari”, “ma femme” → `situation_familiale = "en couple"`.
    - Si le client dit explicitement “ce n’est pas mon adresse”, “j’ai déménagé”, “c’est l’ancienne adresse”, ou corrige une rue, un numéro ou une ville → `adresse_modifiee = 1`.
    - Si le client confirme l’adresse telle que dite → `adresse_modifiee = 0`.
    - Répondre en JSON valide uniquement.

    Transcription à analyser :
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
    print(f"------------------- reponse of gpt {content} ...")

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        data = {"error": "Réponse LLM non valide", "raw": content}

    return data
