import requests
import os

# Remplace ce token par une variable d'environnement pour plus de sécurité
AUDD_API_TOKEN = os.getenv('AUDD_API_TOKEN', 'ff6a831ba01ef35fdb0bd250eeeae537')
AUDD_API_URL = 'https://api.audd.io/'

def search_song(file_path):
    """Envoie un fichier mp3 à l'API AudD, affiche et sauvegarde les résultats."""
    with open(file_path, 'rb') as f:
        files = {'file': f}
        data = {
            'api_token': AUDD_API_TOKEN,
            'return': 'apple_music,spotify',  # Pour plus d'infos sur la chanson
        }
        response = requests.post(AUDD_API_URL, data=data, files=files)
    if response.status_code == 200:
        result = response.json()
        if result.get('result'):
            song = result['result']
            title = song.get('title')
            artist = song.get('artist')
            album = song.get('album')
            duration = song.get('duration')
            spotify_url = song.get('spotify', {}).get('external_urls', {}).get('spotify', 'N/A')
            apple_url = song.get('apple_music', {}).get('url', 'N/A')
            print(f"Titre : {title}")
            print(f"Artiste : {artist}")
            print(f"Album : {album}")
            print(f"Durée : {duration} secondes")
            print(f"Spotify : {spotify_url}")
            print(f"Apple Music : {apple_url}")
            # Sauvegarde des résultats dans un fichier JSON
            result_data = {
                "title": title,
                "artist": artist,
                "album": album,
                "duration": duration,
                "spotify_url": spotify_url,
                "apple_music_url": apple_url
            }
            with open("audd_result.json", "w", encoding="utf-8") as out:
                import json
                json.dump(result_data, out, ensure_ascii=False, indent=2)
                print("Résultat sauvegardé dans audd_result.json.")
        else:
            print("Aucun résultat trouvé.")
    else:
        print(f"Erreur lors de la requête : {response.status_code}")

def main():
    file_path = "tesDrmG.mp3"
    if not os.path.isfile(file_path):
        print("Fichier introuvable.")
        return
    search_song(file_path)

if __name__ == "__main__":
    main()
