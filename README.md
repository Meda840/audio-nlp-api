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

📂 audio-nlp-api/
├── main.py # Point d'entrée FastAPI
├── service/
│ ├── download.py # Téléchargement des fichiers audio
│ ├── convert.py # Conversion audio MP3 a WAV (non utilisé car WAV disponible)
│ ├── transcribe.py # Transcription locale (plus lent)
│ ├── transcribeAssembly.py # Transcription via AssemblyAI (rapide)
│ ├── extract_infos.py # Extraction d'informations via OpenAI API
├── utils/
│ ├── silence_trimmer.py # Suppression des silences audio
│ └── file_cleanup.py # Executé via cron pour la Suppression automatique des fichiers audio 
├── logs/ # Logs des tâches automatiques cron
├── .env # Clés API et URL backend PHP
├── requirements.txt # Dépendances Python
└── README.md 

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

pip install -r requirements.txt

### 4. Créer le fichier .env

ASSEMBLYAI_API_KEY=cle_assemblyai
OPENAI_API_KEY=cle_openai
php_api_url=http://serveur-php.com/endpoint.php/fiche_ai_data_post.php

### ▶️ Lancer le serveur FastAPI

uvicorn main:app --host 0.0.0.0 --port 8000

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

flowchart TD
    A[📥 Requête POST /process] --> B[⬇️ Télécharger audio (download_audio)]
    B --> C[🔊 Nettoyage silence (trim_silence)]
    C --> D{💻 Transcription}
    D -->|Rapide| E[📝 AssemblyAI (transcribe_with_assemblyai)]
    D -->|Local| F[📝 faster-whisper (transcribe_audio)]
    E --> G[📄 Lecture transcription]
    F --> G
    G --> H[🤖 Extraction infos OpenAI (extract_infos_from_text)]
    H --> I[📡 Envoi données au serveur PHP (send_ai_data_to_php)]
    I --> J[✅ Terminé, logs console]
    
    subgraph Background
        B
        C
        D
        E
        F
        G
        H
        I
    end

    style Background fill:#f9f,stroke:#333,stroke-width:1px,fill-opacity:0.05


flowchart TD
    style A fill:#FFD700,stroke:#333,stroke-width:1px
    style B fill:#87CEFA,stroke:#333,stroke-width:1px
    style C fill:#98FB98,stroke:#333,stroke-width:1px
    style D fill:#FFB6C1,stroke:#333,stroke-width:1px
    style E fill:#FF6347,stroke:#333,stroke-width:1px
    style F fill:#8A2BE2,stroke:#333,stroke-width:1px

    A[📥 **POST /process**<br>Requête client] --> B[⬇️ **Téléchargement audio**<br>download_audio]
    B --> C[🔊 **Nettoyage silences**<br>trim_silence]
    C --> D{💻 **Transcription**}
    D -->|🌐 Rapide| E[📝 **AssemblyAI**<br>transcribe_with_assemblyai]
    D -->|💻 Local| F[📝 **faster-whisper**<br>transcribe_audio]
    E --> G[📄 **Lecture transcription**]
    F --> G
    G --> H[🤖 **Extraction infos**<br>extract_infos_from_text]
    H --> I[📡 **Envoi au PHP**<br>send_ai_data_to_php]
    I --> J[✅ **Terminé**<br>Logs et retour status]

    subgraph Background["⚡ BackgroundTasks"]
        B
        C
        D
        E
        F
        G
        H
        I
    end
