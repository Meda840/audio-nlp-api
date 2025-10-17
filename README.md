# 🧠 AI Audio Processing API

Ce projet est une API Python développée avec **FastAPI** qui permet de :
- Télécharger un fichier audio,
- Le nettoyer (suppression des silences),
- Le transcrire automatiquement (AssemblyAI),
- Extraire des informations structurées (OpenAI),
- Puis envoyer les résultats au backend PHP.

---

## 🚀 Fonctionnalités principales

- ✅ Téléchargement automatique de fichiers audio depuis une URL
- 🔊 Nettoyage des silences pour améliorer la transcription
- 📝 Transcription vocale → texte avec AssemblyAI
- 🤖 Extraction intelligente d’informations via OpenAI
- 🔁 Envoi automatique des données extraites vers un serveur PHP
- 🧰 Traitement en **BackgroundTasks** pour ne pas bloquer l’API

---

## 🏗️ Architecture du projet

<pre> ```
📂 audio-nlp-api/
├── main.py                     # Point d'entrée FastAPI
├── service/
│   ├── download.py             # Téléchargement des fichiers audio
│   ├── convert.py              # Conversion audio MP3 a WAV (non utilisé car WAV disponible)
│   ├── transcribe.py           # Transcription locale (plus lent)
│   ├── transcribeAssembly.py   # Transcription via AssemblyAI (rapide)
│   └── extract_infos.py        # Extraction d'informations via OpenAI API
├── utils/
│   ├── silence_trimmer.py      # Suppression des silences audio
│   └── file_cleanup.py         # Cron pour suppression automatique des fichiers audio
├── logs/                       # Logs des tâches automatiques cron
├── .env                        # Clés API et URL backend PHP
├── requirements.txt            # Dépendances Python
└── README.md
``` </pre>

---

## ⚙️ Installation & Configuration
```bash
### 1. Cloner le projet

git clone https://github.com/Meda840/audio-nlp-api.git
cd audio-nlp-api

### 2. Créer et activer un environnement virtuel

python3 -m venv venv
source venv/bin/activate   # Linux
venv\Scripts\activate      # Windows

### 3. Installer les dépendances

apt update
apt install -y build-essential python3-dev
pip install -r requirements.txt

### 4. Créer le fichier .env

ASSEMBLYAI_API_KEY=cle_assemblyai
OPENAI_API_KEY=cle_openai
php_api_url=http://serveur-php.com/fiche_ai_data_post.php

### ▶️ Lancer le serveur FastAPI

uvicorn main:app --host 0.0.0.0 --port 8000

```

## 🖥️ Déploiement & Service Systemd
Pour exécuter l'API en production et assurer qu'elle redémarre automatiquement en cas de crash, nous utilisons **systemd**.
### 1️⃣ Création du fichier de service

Créer un fichier `/etc/systemd/system/audio-nlp-api.service` :
```ini
[Unit]
Description=Audio NLP API - FastAPI/Uvicorn Service
After=network.target

[Service]
User=m.elgaouzi
Group=m.elgaouzi
#Project working directory
WorkingDirectory=/home/m.elgaouzi/audio-nlp-api
#Path to virtual environment & app start command
ExecStart=/home/m.elgaouzi/audio-nlp-api/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
#Restart on failure
Restart=always
RestartSec=5
#Environment variables
Environment="PYTHONUNBUFFERED=1"
EnvironmentFile=/home/m.elgaouzi/audio-nlp-api/.env

[Install]
WantedBy=multi-user.target
```

### 2️⃣ Commandes utiles systemd

``` bash
#Recharger les services après modification 
sudo systemctl daemon-reload

#Démarrer le service
sudo systemctl start audio-nlp-api

#Activer le service au démarrage du serveur
sudo systemctl enable audio-nlp-api

#Vérifier le statut du service
sudo systemctl status audio-nlp-api

#Arrêter le service
sudo systemctl stop audio-nlp-api
```
### 3️⃣ Notes

Le service tourne sous l'utilisateur m.elgaouzi pour plus de sécurité (éviter root en production).

Restart=always permet au serveur de redémarrer automatiquement en cas de crash.

Les logs peuvent être consultés via :
``` bash
journalctl -u audio-nlp-api -f 
```


### Requirements

- Python 3.11+
- Virtual environment (`venv`)
- Dependencies listed in `requirements.txt`


### Endpoints

## GET (`/health`)
Permet de vérifier si l’API fonctionne correctement.

---

Pour lancer le traitement audio et envoyer des données au serveur PHP
## POST  (`/process`)
    {
    "fiche_id": 12345,
    "audio_url": "https://exemple.com/audio/12345.wav"
    }

    📡 Réponse immédiate :
    {
    "status": "queued",
    "fiche_id": 12345,
    "message": "Processing started in background. Results will be sent to PHP when ready."
    }

⏳ Une fois le traitement terminé, les données sont envoyées automatiquement au backend PHP défini dans .env.


## 🧼 Nettoyage automatique des fichiers audio

Un script `utils/file_cleanup.py` est exécuté automatiquement chaque soir via une tâche **cron** pour supprimer les fichiers audio (par défaut > 2 heures) afin de libérer de l’espace disque.

📅 Exemple de cron job :
```bash
0 23 * * * /usr/bin/python3 /home/mohamed-amine/Desktop/audio-nlp-api/utils/file_cleanup.py >> /home/mohamed-amine/Desktop/audio-nlp-api/logs/cron_cleanup.log 2>&1

```


