import yt_dlp
import vlc
from PyQt5.QtCore import QTimer

class MusicPlayer:
    def __init__(self):
        self.player = None
        self.timer = QTimer()  # Timer pour surveiller l'état du lecteur
        self.timer.timeout.connect(self.check_playing)

    def play(self, song_name):
        print(f"Playing song: {song_name}")  # Debugging line
        ydl_opts = {
            'format': 'bestaudio/best',
            'noplaylist': True,
            'default_search': 'ytsearch1:',
            'quiet': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(song_name, download=False)
            if 'entries' in info:
                video = info['entries'][0]
            else:
                video = info
            
            if video is not None and 'formats' in video:
                for fmt in video['formats']:
                    if fmt.get('acodec') != 'none':
                        audio_url = fmt['url']
                        print(f"Audio URL: {audio_url}")  # Debugging line
                        break
                else:
                    print("Aucun format audio valide trouvé.")
                    return
            
            self.player = vlc.MediaPlayer(audio_url)
            self.player.play()
            print("Player started")  # Debugging line

            # Démarrer le timer pour surveiller la lecture
            self.timer.start(1000)  # Vérifie toutes les secondes

    def stop(self):
        if self.player is not None and self.player.is_playing():
            self.player.stop()
            print("Player stopped")  # Debugging line
        self.timer.stop()

    def is_playing(self):
        return self.player.is_playing() if self.player else False

    def check_playing(self):
        if not self.is_playing():
            print("Lecture terminée.")
            self.timer.stop()