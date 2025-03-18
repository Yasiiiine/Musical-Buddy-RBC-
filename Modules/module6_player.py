import yt_dlp
import vlc
import time

class MusicPlayer:
    def __init__(self):
        self.player = None

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
            time.sleep(2)  # Wait for the player to start
            print("Player started")  # Debugging line

    def stop(self):
        if self.player is not None and self.player.is_playing():
            self.player.stop()
            print("Player stopped")  # Debugging line

    def is_playing(self):
        return self.player.is_playing() if self.player else False