# logic.py
import os
import requests
import json
from pydub import AudioSegment
import tempfile

def get_audd_token():
    config_path = os.path.join(os.path.dirname(__file__), 'audd_config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('AUDD_API_TOKEN')
    except Exception:
        return None

AUDD_API_URL = 'https://api.audd.io/'

# Nouvelle fonction pour extraire un extrait court (20s max)
def get_audio_excerpt(file_path, duration_ms=20000):
    try:
        audio = AudioSegment.from_file(file_path)
        excerpt = audio[:duration_ms]
        temp = tempfile.NamedTemporaryFile(delete=False, suffix='.wav')
        excerpt.export(temp.name, format='wav')
        return temp.name
    except Exception as e:
        print(f"Erreur lors de l'extraction audio: {e}")
        return None

def identify_song(file_path):
    """Envoie un extrait court à l'API AudD ou le fichier complet en cas d'échec."""
    AUDD_API_TOKEN = get_audd_token()
    if not AUDD_API_TOKEN:
        return {'error': 'Token API AudD manquant ou fichier audd_config.json absent.'}
    try:
        # D'abord, essayer avec un extrait court pour éviter l'erreur 413
        use_full_file = False
        excerpt_path = None
        
        try:
            excerpt_path = get_audio_excerpt(file_path)
            if not excerpt_path:
                use_full_file = True
                print("Échec du découpage audio, on utilise le fichier complet")
        except Exception:
            use_full_file = True
            print("Exception lors du découpage, on utilise le fichier complet")
        
        # Préparation des données pour l'API
        data = {
            'api_token': AUDD_API_TOKEN,
            'return': 'apple_music,spotify',
        }
        
        if use_full_file:
            # Méthode directe comme dans audd_search.py
            with open(file_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(AUDD_API_URL, data=data, files=files)
        else:
            # Méthode avec extrait audio
            with open(excerpt_path, 'rb') as f:
                files = {'file': f}
                response = requests.post(AUDD_API_URL, data=data, files=files)
            # Nettoyage du fichier temporaire
            if excerpt_path and os.path.exists(excerpt_path):
                os.remove(excerpt_path)
                
        if response.status_code == 200:
            result = response.json()
            if result.get('result'):
                song = result['result']
                return {
                    'title': song.get('title'),
                    'artist': song.get('artist'),
                    'album': song.get('album'),
                    'duration': song.get('duration'),
                    'spotify_url': song.get('spotify', {}).get('external_urls', {}).get('spotify', 'N/A'),
                    'apple_music_url': song.get('apple_music', {}).get('url', 'N/A')
                }
            else:
                return {'error': 'Aucun résultat trouvé.'}
        else:
            return {'error': f'Erreur HTTP {response.status_code}'}
    except Exception as e:
        return {'error': str(e)}
