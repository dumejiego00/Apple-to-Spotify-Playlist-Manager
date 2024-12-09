import requests
from token_manager import load_access_token

def get_playlist_details(playlist_id):
    access_token = load_access_token()

    if access_token:
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
        headers = {
            'Authorization': f'Bearer {access_token}'  # Bearer token
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            playlist = response.json()
            print(f"Playlist Name: {playlist['name']}")
            print(f"Description: {playlist['description']}")
            print(f"Number of Tracks: {playlist['tracks']['total']}")
            print(f"Spotify URL: {playlist['external_urls']['spotify']}")
        else:
            print(f"Error: {response.status_code}, {response.text}")


get_playlist_details("3cDHCxYclYnKR0kgi2l9Cz")