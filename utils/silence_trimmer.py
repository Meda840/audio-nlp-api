"""
===============================================================
 Fichier        : silence_trimmer.py
 Auteur         : Mohamed-Amine ELGAOUZI
 Description    : Supprime les silences dans les fichiers audio WAV 
                  pour améliorer la qualité de transcription. 
                  Utilise WebRTC VAD pour détecter la parole.
 Créé le        : 16/10/2025
 Dernière maj   : 16/10/2025
===============================================================
 Dépendances    :
 - os
 - wave
 - contextlib
 - webrtcvad
 - pydub

 Fonctionnalités clés :
 - Lecture d’un fichier WAV mono
 - Détection des parties parlées avec WebRTC VAD
 - Suppression des silences et reconstruction de l’audio
 - Sauvegarde du fichier traité dans 'data/audio/processed'
 - Affichage des durées originales et traitées pour logging

 Notes :
 - Ce module est utilisé dans le pipeline de traitement audio
   avant transcription via AssemblyAI ou Faster Whisper.
===============================================================
"""

import os
import wave
import contextlib
import webrtcvad
from pydub import AudioSegment

# Config
FRAME_DURATION_MS = 30  # duration per frame for VAD
VAD_MODE = 1            # 0-3, 3 is most aggressive
PROCESSED_DIR = "data/audio/processed"

def read_wave(path):
    """Lire un fichier WAV et retourner les données PCM et le taux d'échantillonnage"""
    with contextlib.closing(wave.open(path, 'rb')) as wf:
        num_channels = wf.getnchannels()
        if num_channels != 1:
            raise ValueError("webrtcvad only supports mono audio")
        sample_width = wf.getsampwidth()
        if sample_width != 2:
            raise ValueError("webrtcvad only supports 16-bit audio")
        sample_rate = wf.getframerate()
        if sample_rate not in (8000, 16000, 32000, 48000):
            raise ValueError("Unsupported sample rate: {}".format(sample_rate))
        pcm_data = wf.readframes(wf.getnframes())
        return pcm_data, sample_rate

def write_wave(path, audio, sample_rate):
    """Écrire des données PCM dans un fichier WAV"""
    with contextlib.closing(wave.open(path, 'wb')) as wf:
        wf.setnchannels(1)
        wf.setsampwidth(2)
        wf.setframerate(sample_rate)
        wf.writeframes(audio)

def frame_generator(frame_duration_ms, audio, sample_rate):
    """Générer des frames audio de frame_duration_ms"""
    n = int(sample_rate * (frame_duration_ms / 1000.0) * 2)  # 2 bytes per sample
    offset = 0
    while offset + n <= len(audio):
        yield audio[offset:offset + n]
        offset += n

def vad_collector(sample_rate, frame_duration_ms, padding_ms, vad, frames):
    """Filtrer les frames sans parole"""
    import collections
    num_padding_frames = int(padding_ms / frame_duration_ms)
    ring_buffer = collections.deque(maxlen=num_padding_frames)
    triggered = False
    voiced_frames = []

    for frame in frames:
        is_speech = vad.is_speech(frame, sample_rate)

        if not triggered:
            ring_buffer.append(frame)
            if sum(1 for f in ring_buffer if vad.is_speech(f, sample_rate)) > 0.9 * ring_buffer.maxlen:
                triggered = True
                voiced_frames.extend(ring_buffer)
                ring_buffer.clear()
        else:
            voiced_frames.append(frame)
            ring_buffer.append(frame)
            if sum(1 for f in ring_buffer if not vad.is_speech(f, sample_rate)) > 0.9 * ring_buffer.maxlen:
                triggered = False
                ring_buffer.clear()

    return b''.join(voiced_frames)

def trim_silence(input_path):
    """Supprimer les silences d'un fichier WAV et sauvegarder le fichier traité"""
    if not os.path.exists(PROCESSED_DIR):
        os.makedirs(PROCESSED_DIR)

    pcm_data, sample_rate = read_wave(input_path)
    vad = webrtcvad.Vad(VAD_MODE)
    frames = list(frame_generator(FRAME_DURATION_MS, pcm_data, sample_rate))
    trimmed_audio = vad_collector(sample_rate, FRAME_DURATION_MS, padding_ms=500, vad=vad, frames=frames)

    # Sauvegarder le fichier traité
    filename = os.path.basename(input_path)
    output_path = os.path.join(PROCESSED_DIR, filename)
    write_wave(output_path, trimmed_audio, sample_rate)

    # Logging durations
    original_audio = AudioSegment.from_file(input_path)
    trimmed_audio_seg = AudioSegment.from_file(output_path)
    print(f"[Trimmer] {filename} | Original: {len(original_audio)/1000:.2f}s | Trimmed: {len(trimmed_audio_seg)/1000:.2f}s")

    return output_path

