import requests
from token_manager import load_access_token
import pandas as pd

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

# # Example usage
# track_url = "https://open.spotify.com/track/3Dw9lMKAtrorXeW0wec1dr?si=b4b785e2131743c3" 
# playlist_id = "3cDHCxYclYnKR0kgi2l9Cz"  # Replace with your playlist ID
# add_track_to_playlist(track_url, playlist_id)

def search_track(song_name, artist_name):
    """
    Searches for a track on Spotify using its name and optionally the album name.
    
    Args:
        song_name (str): Name of the song to search for.
        album_name (str): Name of the album (optional).
        
    Returns:
        str: The URI of the track if found, else None.
    """
    access_token = load_access_token()  # Ensure you have a valid access token

    if not access_token:
        print("Access token is missing or invalid.")
        return None

    # Base URL for Spotify search
    url = "https://api.spotify.com/v1/search"

    # Build the search query
    query = f"track:{song_name}"
    query += f" artist:{artist_name}"

    # Request parameters
    params = {
        'q': query,
        'type': 'track',
        'limit': 1  # Get the top result only
    }

    # Headers with authorization
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    # Make the request
    response = requests.get(url, headers=headers, params=params)

    if response.status_code == 200:
        results = response.json()
        tracks = results.get('tracks', {}).get('items', [])
        if tracks:
            # Extract and return the track URI
            track_uri = tracks[0]['uri']
            print(f"Track found: {tracks[0]['name']} (URI: {track_uri})")
            return track_uri
        else:
            print("No tracks found.")
            return None
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

# # Example usage
# if __name__ == "__main__":
#     song_name = "#RICHAXXHAITIAN"
#     artist_name = "Mach-Hommy & KAYTRANADA" 
#     track_uri = search_track(song_name, artist_name)
#     if track_uri:
#         print(f"Track URI: {track_uri}")

CLEANED_CSV_FILE_PATH = 'cleaned_file.csv'
MISSING_URI_FILE_PATH = 'missing_uri_file.csv'
FOUND_URI_FILE_PATH = 'found_uri_file.csv'

# Function to load CSV, search songs, and update Spotify URI
import os

def update_csv_with_spotify_uris(csv_file_path, found_uris_file_path, missing_uris_file_path):
    # Ensure the directories for the output files exist
    for file_path in [found_uris_file_path, missing_uris_file_path]:
        output_dir = os.path.dirname(file_path)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Directory '{output_dir}' created for output files.")

    # Load the CSV file
    df = pd.read_csv(csv_file_path)
    
    # Lists to store rows for songs with and without URIs
    found_uris_rows = []
    missing_uris_rows = []

    # Iterate through each row and search for Spotify URI
    for index, row in df.iterrows():
        song_name = row['Name']
        artist = row['Artist']
        
        if pd.notna(song_name) and pd.notna(artist):  # Ensure fields are not NaN
            spotify_uri = search_track(song_name, artist)  # Call your search function
            
            if spotify_uri:
                row_copy = row.copy()
                row_copy['Spotify URI'] = spotify_uri  # Add URI to row copy
                found_uris_rows.append(row_copy)  # Add to found list
            else:
                missing_uris_rows.append(row)  # Add to missing list
        else:
            print(f"Skipping row at index {index} due to missing data.")
            missing_uris_rows.append(row)  # Add to missing list

    # Save the rows with found URIs to a separate file
    if found_uris_rows:
        found_uris_df = pd.DataFrame(found_uris_rows)
        found_uris_df.to_csv(found_uris_file_path, index=False)
        print(f"Songs with URIs saved to '{found_uris_file_path}'.")
    else:
        print("No songs with URIs found.")

    # Save the rows without URIs to another file
    if missing_uris_rows:
        missing_uris_df = pd.DataFrame(missing_uris_rows)
        missing_uris_df.to_csv(missing_uris_file_path, index=False)
        print(f"Songs without URIs saved to '{missing_uris_file_path}'.")
    else:
        print("No songs without URIs.")

import requests

def search_track_uri(track_uri):
    """
    Retrieves information for a track on Spotify using its URI.

    Args:
        track_uri (str): The Spotify URI of the track.

    Returns:
        dict: A dictionary containing track information if found, else None.
    """
    access_token = load_access_token()  # Ensure you have a valid access token

    if not access_token:
        print("Access token is missing or invalid.")
        return None

    # Extract track ID from the URI
    track_id = track_uri.split(":")[-1]

    # Base URL for Spotify track details
    url = f"https://api.spotify.com/v1/tracks/{track_id}"

    # Headers with authorization
    headers = {
        'Authorization': f'Bearer {access_token}'
    }

    # Make the request
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # Return the track information as a dictionary
        track_info = response.json()
        print(f"Track information retrieved: {track_info['name']} by {', '.join(artist['name'] for artist in track_info['artists'])}")
        return track_info
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None

# Example usage
# track_uri = "spotify:track:3n3Ppam7vgaVa1iaRUc9Lp"
# track_info = search_track_uri(track_uri)
# print(track_info)


# Run the update function
if __name__ == "__main__":
    update_csv_with_spotify_uris(CLEANED_CSV_FILE_PATH, FOUND_URI_FILE_PATH,MISSING_URI_FILE_PATH)
    # search_track("(Sittin' On) the Dock of the Bay", "Otis Redding")
    # search_track_uri("4OssqCixV2Xsxd43wMIQyS")

