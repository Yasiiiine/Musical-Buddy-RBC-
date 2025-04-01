import tkinter as tk
from tkinter import filedialog
import pygame
import os

# logic.py

# Ce fichier est prêt à accueillir de la logique plus tard.
class DummyLogic:
    def __init__(self):
        pass  # Placeholder pour logique future




    def play_audio():
        # Dossier où se trouvent les fichiers audio
        dossier_audio = "recordings"
    
        # Vérifier si le dossier existe
        if not os.path.exists(dossier_audio):
            print(f"Le dossier {dossier_audio} n'existe pas.")
            return

        # Initialisation de pygame mixer
        pygame.mixer.init()
    
        # Fenêtre Tkinter pour choisir un fichier
        root = tk.Tk()
        root.withdraw()  # Masquer la fenêtre principale

        # Ouvrir la boîte de dialogue pour choisir un fichier audio dans le dossier recordings
        fichier_audio = filedialog.askopenfilename(
            initialdir=dossier_audio,  # Définir le répertoire initial sur recordings
            title="Sélectionner un fichier audio", 
            filetypes=[("Fichiers audio", "*.mp3 *.wav *.ogg *.flac")]
        )
    
        if fichier_audio:  # Si un fichier a été sélectionné
            # Charger et jouer le fichier audio
            pygame.mixer.music.load(fichier_audio)
            pygame.mixer.music.play()

            print(f"Lecture de {fichier_audio}...")

            # Attendre la fin de la lecture
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)  # Vérifie toutes les 100ms si la musique est toujours en lecture

        else:
            print("Aucun fichier sélectionné.")
