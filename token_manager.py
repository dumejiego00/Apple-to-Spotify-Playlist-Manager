import requests
from dotenv import load_dotenv
import os
import json
import time
from flask import Flask, request

# Load environment variables from .env file
load_dotenv()

# Retrieve client ID and client secret from environment variables
client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

# Scopes and redirect URI
scopes = "playlist-modify-public playlist-modify-private"
redirect_uri = "http://127.0.0.1:8888/callback"
state = "34fFs29kd09"

# Authorization URL
auth_url = f"https://accounts.spotify.com/authorize?response_type=code&client_id={client_id}&redirect_uri={redirect_uri}&scope={scopes}&state={state}"

# Define file path for token storage
token_file = 'token.json'

app = Flask(__name__)

@app.route('/callback')
def callback():
    """
    Handles the redirect from Spotify and extracts the authorization code.
    """
    code = request.args.get('code')
    if not code:
        return "No code found in callback URL.", 400
    
    # Exchange the code for an access token
    token_data = exchange_code_for_token(code)
    if token_data:
        return "Authorization successful. Tokens saved.", 200
    else:
        return "Failed to retrieve access token.", 400


def exchange_code_for_token(code):
    """
    Exchanges the authorization code for an access token and refresh token.
    """
    url = "https://accounts.spotify.com/api/token"
    data = {
        'code': code,
        'redirect_uri': redirect_uri,
        'grant_type': 'authorization_code',
        'client_id': client_id,
        'client_secret': client_secret
    }

    response = requests.post(url, data=data)

    if response.status_code == 200:
        response_data = response.json()
        access_token = response_data['access_token']
        refresh_token = response_data['refresh_token']
        expires_in = response_data['expires_in']  # Expiration time in seconds

        # Store token data in file
        with open(token_file, 'w') as f:
            json.dump({
                'access_token': access_token,
                'refresh_token': refresh_token,
                'expires_at': time.time() + expires_in
            }, f)

        print(f"New Access Token: {access_token}")
        return response_data
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None


def load_access_token():
    """
    Loads the access token from the file or refreshes it if expired.
    """
    if os.path.exists(token_file):
        with open(token_file, 'r') as f:
            token_data = json.load(f)
            # If token has expired, refresh it
            if time.time() > token_data['expires_at']:
                return refresh_access_token(token_data['refresh_token'])
            else:
                return token_data['access_token']
    else:
        return None


def refresh_access_token(refresh_token):
    """
    Refreshes the access token using the refresh token.
    """
    url = "https://accounts.spotify.com/api/token"
    data = {
        'refresh_token': refresh_token,
        'grant_type': 'refresh_token',
        'client_id': client_id,
        'client_secret': client_secret
    }

    response = requests.post(url, data=data)

    if response.status_code == 200:
        response_data = response.json()
        access_token = response_data['access_token']
        expires_in = response_data['expires_in']

        # Update the token file with new access token and expiration time
        with open(token_file, 'r+') as f:
            token_data = json.load(f)
            token_data['access_token'] = access_token
            token_data['expires_at'] = time.time() + expires_in
            f.seek(0)
            json.dump(token_data, f)
            f.truncate()

        print(f"Refreshed Access Token: {access_token}")
        return access_token
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None


if __name__ == "__main__":
    # Print the authorization URL for the user to visit
    print(f"Visit the following URL to authorize the app:\n{auth_url}")
    # Run the Flask server to handle the callback
    app.run(port=8888)
