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


# get_playlist_details("3cDHCxYclYnKR0kgi2l9Cz")
# https://open.spotify.com/track/3Dw9lMKAtrorXeW0wec1dr?si=b4b785e2131743c3

import requests

def add_track_to_playlist(track_url, playlist_id):
    access_token = load_access_token()  # Assuming you load the access token here

    if not access_token:
        print("Error: Access token not available.")
        return

    # Extract the track ID from the URL
    track_id = track_url.split("/")[-1].split("?")[0]  # Extract the last part of the URL as track ID

    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = {
        'Authorization': f'Bearer {access_token}',  # Include Bearer token for authentication
        'Content-Type': 'application/json'  # Set content type to JSON
    }

    data = {
        "uris": [f"spotify:track:{track_id}"],  # Add the track URI to the list
        "position": 0  # Position where the track should be added (optional)
    }

    response = requests.post(url, headers=headers, json=data)  # Make the POST request

    if response.status_code == 201:
        print(f"Track {track_id} successfully added to playlist {playlist_id}.")
    else:
        print(f"Error: {response.status_code}, {response.text}")
        # Handle token expiration or other errors here if necessary

# Example usage
track_url = "https://open.spotify.com/track/3Dw9lMKAtrorXeW0wec1dr?si=b4b785e2131743c3"
playlist_id = "3cDHCxYclYnKR0kgi2l9Cz"  # Replace with your playlist ID
add_track_to_playlist(track_url, playlist_id)
