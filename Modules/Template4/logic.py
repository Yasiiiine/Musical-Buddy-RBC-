import pygame
import os
import random

# logic.py

# Ce fichier est prêt à accueillir de la logique plus tard.
class DummyLogic:
    def __init__(self, dossier_audio):
        self.dossier_audio = dossier_audio
        # Vérification que le dossier existe
        if not os.path.exists(self.dossier_audio):
            raise ValueError(f"Le dossier {self.dossier_audio} n'existe pas.")
        pygame.mixer.init()
        self.musique_en_cours = None
        self.en_pause = False
        self.last_pause_time = 0 

    def play_audio():
        # Lister tous les fichiers audio dans le dossier
        fichiers_audio = [f for f in os.listdir(self.dossier_audio) 
                          if f.endswith(('.mp3', '.wav', '.ogg', '.flac'))]
        
        if not fichiers_audio:
            print(f"Aucun fichier audio trouvé dans {self.dossier_audio}.")
            return
        
        # Sélectionner un fichier audio aléatoirement dans la liste
        fichier_audio = random.choice(fichiers_audio)
        chemin_audio = os.path.join(self.dossier_audio, fichier_audio)
        
        # Charger et jouer le fichier audio
        pygame.mixer.music.load(chemin_audio)
        pygame.mixer.music.play()

        print(f"Lecture de {fichier_audio}...")

        # Attendre la fin de la lecture
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10) 

    def stop_audio(self):
        """Mettre la musique en pause avec un délai pour éviter l'abus."""
        current_time = time.time()
        if current_time - self.last_pause_time < 2:
            print("Veuillez attendre quelques secondes avant de mettre la musique en pause à nouveau.")
            return
        

        """Mettre la musique en pause."""
        if pygame.mixer.music.get_busy():
            pygame.mixer.music.pause()
            self.en_pause = True
            print("Musique en pause.")
        else:
            print("Aucune musique en cours pour mettre en pause.")

    def replay_audio(self):
        """Relancer la musique si elle est en pause, avec un délai pour éviter l'abus."""
        current_time = time.time()
        if current_time - self.last_pause_time < 2:
            print("Veuillez attendre quelques secondes avant de relancer la musique.")
            return
        
        
        """Relancer la lecture si la musique est en pause."""
        if self.en_pause:
            pygame.mixer.music.unpause()
            self.en_pause = False
            print("Relance de la musique...")
        else:
            print("La musique n'est pas en pause.")
