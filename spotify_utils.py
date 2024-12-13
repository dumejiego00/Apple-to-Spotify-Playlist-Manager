from token_manager import load_access_token
import pandas as pd
import os
import requests

CLEANED_CSV_FILE_PATH = 'cleaned_file.csv'
MISSING_URI_FILE_PATH = 'missing_uri_file.csv'
FOUND_URI_FILE_PATH = 'found_uri_file.csv'

def get_playlist_details(playlist_id):
    access_token = load_access_token()

    if access_token:
        url = f"https://api.spotify.com/v1/playlists/{playlist_id}"
        headers = {
            'Authorization': f'Bearer {access_token}' 
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

def add_track_to_playlist(track_url, playlist_id):
    access_token = load_access_token() 

    if not access_token:
        print("Error: Access token not available.")
        return

    track_id = track_url.split("/")[-1].split("?")[0]  
    url = f"https://api.spotify.com/v1/playlists/{playlist_id}/tracks"
    headers = {
        'Authorization': f'Bearer {access_token}',  
        'Content-Type': 'application/json' 
    }

    data = {
        "uris": [f"spotify:track:{track_id}"],  
        "position": 0  
    }

    response = requests.post(url, headers=headers, json=data) 

    if response.status_code == 201:
        print(f"Track {track_id} successfully added to playlist {playlist_id}.")
    else:
        print(f"Error: {response.status_code}, {response.text}")

def search_track(song_name, artist_name):
    """
    Searches for a track on Spotify using its name and optionally the album name.
    
    Args:
        song_name (str): Name of the song to search for.
        album_name (str): Name of the album (optional).
        
    Returns:
        str: The URI of the track if found, else None.
    """
    access_token = load_access_token() 

    if not access_token:
        print("Access token is missing or invalid.")
        return None

    url = "https://api.spotify.com/v1/search"

    query = f"track:{song_name}"
    query += f" artist:{artist_name}"

    params = {
        'q': query,
        'type': 'track',
        'limit': 1  
    }

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        results = response.json()
        tracks = results.get('tracks', {}).get('items', [])
        if tracks:
            track_uri = tracks[0]['uri']
            print(f"Track found: {tracks[0]['name']} (URI: {track_uri})")
            return track_uri
        else:
            print("No tracks found.")
            return None
    else:
        print(f"Error: {response.status_code}, {response.text}")

        # print(f"Retry after{response.headers['retry-after']}")
        return None

def update_csv_with_spotify_uris(csv_file_path, found_uris_file_path, missing_uris_file_path):
    for file_path in [found_uris_file_path, missing_uris_file_path]:
        output_dir = os.path.dirname(file_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Directory '{output_dir}' created for output files.")

    df = pd.read_csv(csv_file_path)
    
    found_uris_rows = []
    missing_uris_rows = []

    for index, row in df.iterrows():
        song_name = row['Name']
        artist = row['Artist']
        
        if pd.notna(song_name) and pd.notna(artist):  
            spotify_uri = search_track(song_name, artist)  
            
            if spotify_uri:
                row_copy = row.copy()
                row_copy['Spotify URI'] = spotify_uri 
                found_uris_rows.append(row_copy) 
            else:
                missing_uris_rows.append(row) 
        else:
            print(f"Skipping row at index {index} due to missing data.")
            missing_uris_rows.append(row) 

    if found_uris_rows:
        found_uris_df = pd.DataFrame(found_uris_rows)
        found_uris_df.to_csv(found_uris_file_path, index=False)
        print(f"Songs with URIs saved to '{found_uris_file_path}'.")
    else:
        print("No songs with URIs found.")

    if missing_uris_rows:
        missing_uris_df = pd.DataFrame(missing_uris_rows)
        if 'Spotify Uri' in missing_uris_df.columns:
            missing_uris_df = missing_uris_df.drop(columns=['Spotify URI'])
        missing_uris_df.to_csv(missing_uris_file_path, index=False)
        print(f"Songs without URIs saved to '{missing_uris_file_path}'.")
    else:
        print("No songs without URIs.")

def search_track_uri(track_uri):
    """
    Retrieves information for a track on Spotify using its URI.

    Args:
        track_uri (str): The Spotify URI of the track.

    Returns:
        dict: A dictionary containing track information if found, else None.
    """
    access_token = load_access_token()  

    if not access_token:
        print("Access token is missing or invalid.")
        return None

    track_id = track_uri.split(":")[-1]

    url = f"https://api.spotify.com/v1/tracks/{track_id}"

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        track_info = response.json()
        print(f"Track information retrieved: {track_info['name']} by {', '.join(artist['name'] for artist in track_info['artists'])}")
        return track_info
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

def get_user_playlist():
    access_token = load_access_token()

    if not access_token:
        print("Access token is missing or invalid")
        return None

    url = 'https://api.spotify.com/v1/me/playlists'

    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        playlists = response.json()["items"]
        print("Playlists retrieved successfully:")
        for index, playlist in enumerate(playlists):
            print(f"{index + 1}: {playlist['name']} (ID: {playlist['id']})")
        
        # Allow user to pick a playlist
        choice = int(input("\nEnter the number of the playlist to select: ")) - 1
        if 0 <= choice < len(playlists):
            selected_playlist = playlists[choice]
            print(f"\nYou selected: {selected_playlist['name']} (ID: {selected_playlist['id']})")
            return selected_playlist["id"]
        else:
            print("Invalid selection.")
            return None
    else:
        print(f"Error: {response.status_code}, {response.json()}")
        return None
    
if __name__ == "__main__":
    # update_csv_with_spotify_uris(CLEANED_CSV_FILE_PATH, FOUND_URI_FILE_PATH,MISSING_URI_FILE_PATH)
    # search_track("(Sittin' On) the Dock of the Bay", "Otis Redding")
    # search_track_uri("4OssqCixV2Xsxd43wMIQyS")
    get_user_playlist()
