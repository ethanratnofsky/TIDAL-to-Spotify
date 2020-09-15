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


def print_hdiv():
    print('----------')


def request_spotify_auth():
    print('Connecting to Spotify...')
    response = requests.get('https://accounts.spotify.com/authorize',
                            params={
                                'client_id': CLIENT_ID,
                                'response_type': 'code',
                                'redirect_uri': 'https://example.com/callback',
                                'state': 'AUIdherfheh4ffDo8seFef4uwyIrq',
                                'scope': 'playlist-modify-public playlist-modify-private'
                            })
    print_hdiv()
    print('''You will be redirected to a web page in 5 seconds to grant us access to your Spotify user information.
    This information is necessary for us to be able to create Spotify playlists on your account for you. Please be
    ready to copy and paste the URL of the web page you are redirected to after you grant us access.''')
    print_hdiv()
    time.sleep(5)
    webbrowser.open(response.url)
    redirect_url = input('Please copy and paste the URL of the website you were redirected to: ')
    url_object = urlparse(redirect_url)
    qs = parse_qs(url_object.query)

    if qs.get('error'):
        print('Uh oh! Our request to access your user information was denied!')
    else:
        print('We\'re in!')


def main():
    # Initialize TIDAL session using credentials defined in .env
    print('Logging into TIDAL session...')
    session = tidalapi.Session()
    session.login(TIDAL_EMAIL, TIDAL_PASS)
    if session.check_login():
        print(f"Successfully logged in as {TIDAL_EMAIL}")

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
