import requests
from dotenv import load_dotenv
import os
import json
import time

# Load environment variables from .env file
load_dotenv()

# Retrieve client ID and client secret from environment variables
client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

# Define file path for token storage
token_file = 'token.json'

def get_access_token():
    # Check if token exists and is valid
    if os.path.exists(token_file):
        with open(token_file, 'r') as f:
            token_data = json.load(f)
            # If token has expired, refresh it
            if time.time() > token_data['expires_at']:
                return refresh_access_token()
            else:
                return token_data['access_token']
    else:
        return refresh_access_token()

def refresh_access_token():
    url = "https://accounts.spotify.com/api/token"
    data = {
        'grant_type': 'client_credentials',
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

# Usage example
token = get_access_token()
