import os
import requests
import tidalapi
import webbrowser

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
    response = requests.get('https://accounts.spotify.com/authorize',
                            params={
                                'client_id': CLIENT_ID,
                                'response_type': 'code',
                                'redirect_uri': 'https://example.com/callback',
                                'state': 'AUIdherfheh4ffDo8seFef4uwyIrq',
                                'scope': 'playlist-modify-public playlist-modify-private'
                            })
    webbrowser.open(response.url)
    print(response.text)


def main():
    # Initialize TIDAL session using credentials defined in .env
    print('Logging into TIDAL session...')
    session = tidalapi.Session()
    session.login(TIDAL_EMAIL, TIDAL_PASS)
    if session.check_login():
        print(f"Successfully logged in as {TIDAL_EMAIL}")
        print_hdiv()

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

    request_spotify_auth()


if __name__ == '__main__':
    request_spotify_auth()
