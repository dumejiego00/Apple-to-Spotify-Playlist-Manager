import requests
from dotenv import load_dotenv
import os

# Load environment variables from .env file
load_dotenv()

# Retrieve client ID and client secret from environment variables
client_id = os.getenv('SPOTIFY_CLIENT_ID')
client_secret = os.getenv('SPOTIFY_CLIENT_SECRET')

# Define the URL and data for the POST request
url = "https://accounts.spotify.com/api/token"
data = {
    'grant_type': 'client_credentials',
    'client_id': client_id,
    'client_secret': client_secret
}

# Make the POST request to get the token
response = requests.post(url, data=data)

# Check if the request was successful
if response.status_code == 200:
    # Parse the response JSON to get the access token
    access_token = response.json()['access_token']
    print(f"Access Token: {access_token}")
else:
    print(f"Error: {response.status_code}, {response.text}")
