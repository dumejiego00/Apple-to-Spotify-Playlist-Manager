import requests
import json
import time
import os

token_file = 'token.json'

def load_access_token():
    if os.path.exists(token_file):
        with open(token_file, 'r') as f:
            token_data = json.load(f)
            if time.time() > token_data['expires_at']:
                print("Token expired. Refreshing...")
                return refresh_access_token()
            else:
                print("Using existing access token.")
                return token_data['access_token']
    else:
        return refresh_access_token()

def refresh_access_token():
    client_id = 'your-client-id'  # Replace with your actual client ID
    client_secret = 'your-client-secret'  # Replace with your actual client secret
    
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
        expires_in = response_data['expires_in']

        with open(token_file, 'w') as f:
            json.dump({
                'access_token': access_token,
                'expires_at': time.time() + expires_in
            }, f)

        print(f"New Access Token: {access_token}")
        return access_token
    else:
        print(f"Error: {response.status_code}, {response.text}")
        return None
