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
    access_token = exchange_code_for_token(code)
    if access_token:
        return f"Authorization successful. Access token saved.", 200
    else:
        return "Failed to retrieve access token.", 400


def exchange_code_for_token(code):
    """
    Exchanges the authorization code for an access token.
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
        expires_in = response_data['expires_in']  # Expiration time in seconds

        # Store token data in file with correct expiration time
        with open(token_file, 'w') as f:
            json.dump({
                'access_token': access_token,
                'expires_at': time.time() + expires_in  # Set expiration time based on response
            }, f)

        print(f"New Access Token: {access_token}")
        return access_token
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
                return refresh_access_token()
            else:
                return token_data['access_token']
    else:
        return None


def refresh_access_token():
    """
    Refreshes the access token. (Placeholder: implement later if required)
    """
    print("Token refresh logic not implemented yet.")
    return None


if __name__ == "__main__":
    # Print the authorization URL for the user to visit
    print(f"Visit the following URL to authorize the app:\n{auth_url}")
    # Run the Flask server to handle the callback
    app.run(port=8888)
