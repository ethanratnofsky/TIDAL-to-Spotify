import os
import time
import webbrowser
from urllib.parse import urlparse, parse_qs

import requests
import tidalapi
from dotenv import load_dotenv

# Loads environment variables defined in .env
load_dotenv()

TIDAL_EMAIL = os.getenv('TIDAL_EMAIL')
TIDAL_PASS = os.getenv('TIDAL_PASS')
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
STATE = os.getenv('STATE')


def print_hdiv():
    print('----------')


def request_spotify_auth():
    # Request user authentication
    print('Connecting to Spotify...')
    params = {'client_id': CLIENT_ID,
              'response_type': 'code',
              'redirect_uri': 'https://example.com/callback',
              'state': STATE,
              'scope': 'playlist-modify-public playlist-modify-private'
              }
    response = requests.get('https://accounts.spotify.com/authorize', params)

    # Print next step information for user
    print_hdiv()
    print('You will be redirected to a web page in 5 seconds to grant us access to your Spotify user data...\n'
          '\n'
          'This information is necessary for us to be able to create Spotify playlists on your account for you.\n'
          'Please be ready to copy and paste the URL of the web page you are redirected to after you grant us access.')
    print_hdiv()
    time.sleep(5)

    # Get authorization code that can be exchanged for an access token
    webbrowser.open(response.url)
    redirect_url = input('Please copy and paste the URL of the website you were redirected to: ')
    url_object = urlparse(redirect_url)
    qs = parse_qs(url_object.query)

    # Error if user does not grant access to Spotify user data
    if qs.get('error'):
        print('Oh no! Our request to access your user data was denied!')
    else:
        print('We\'re in!')


def main():
    # Initialize TIDAL session using credentials defined in .env
    print('Logging into TIDAL session...')
    session = tidalapi.Session()
    session.login(TIDAL_EMAIL, TIDAL_PASS)
    if session.check_login():
        print(f'Successfully logged in as {TIDAL_EMAIL}')

    # Authenticate Spotify
    request_spotify_auth()

    print_hdiv()
    print('Ready to do work!')
    exit()

    # Queries user for valid TIDAL playlist URL
    while True:
        tidal_url = input('Enter TIDAL playlist URL: ')
        tidal_playlist_id = tidal_url[34:]
        try:
            tidal_playlist = session.get_playlist(tidal_playlist_id)
            print_hdiv()
            break
        except requests.exceptions.HTTPError:
            print('Invalid TIDAL playlist URL.')


if __name__ == '__main__':
    main()
