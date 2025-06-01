# logic.py
import os
import requests
import json

def get_audd_token():
    config_path = os.path.join(os.path.dirname(__file__), 'audd_config.json')
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            return data.get('AUDD_API_TOKEN')
    except Exception:
        return None

AUDD_API_URL = 'https://api.audd.io/'

def identify_song(file_path):
    """Envoie un fichier audio à l'API AudD et retourne les infos de la chanson ou None."""
    AUDD_API_TOKEN = get_audd_token()
    if not AUDD_API_TOKEN:
        return {'error': 'Token API AudD manquant ou fichier audd_config.json absent.'}
    try:
        with open(file_path, 'rb') as f:
            files = {'file': f}
            data = {
                'api_token': AUDD_API_TOKEN,
                'return': 'apple_music,spotify',
            }
            response = requests.post(AUDD_API_URL, data=data, files=files)
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
