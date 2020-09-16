import os
import time
import webbrowser
from urllib.parse import urlparse, parse_qs

import requests
import tidalapi
from dotenv import load_dotenv, find_dotenv, set_key, unset_key

# Loads environment variables defined in .env
load_dotenv()

TIDAL_EMAIL = os.getenv('TIDAL_EMAIL')
TIDAL_PASS = os.getenv('TIDAL_PASS')
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
REDIRECT_URI = os.getenv('REDIRECT_URI')
STATE = os.getenv('STATE')
REFRESH_TOKEN = os.getenv('REFRESH_TOKEN')

access_token = ''


def print_hdiv():
    print('-----------------------------------')


def refresh_token():
    # Refresh access token
    token = requests.post('https://accounts.spotify.com/api/token',
                          data={'grant_type': 'refresh_token',
                                'refresh_token': REFRESH_TOKEN,
                                'client_id': CLIENT_ID,
                                'client_secret': CLIENT_SECRET}).json()
    return token


def request_token():
    # Request user authentication
    code_response = requests.get('https://accounts.spotify.com/authorize',
                                 params={'client_id': CLIENT_ID,
                                         'response_type': 'code',
                                         'redirect_uri': REDIRECT_URI,
                                         'state': STATE,
                                         'scope': 'playlist-modify-public playlist-modify-private'
                                         })

    # Print next step information for user
    print_hdiv()
    print('You will be redirected to a web page in 5 seconds to grant us access to your Spotify user data...\n'
          '\n'
          'This information is necessary for us to be able to create Spotify playlists on your account for you.\n'
          'Please be ready to copy and paste the URL of the web page you are redirected to after you grant us access.')
    print_hdiv()
    time.sleep(5)

    # Get authorization code that can be exchanged for an access token
    webbrowser.open(code_response.url)
    redirect_url = input('Please copy and paste the URL of the website you were redirected to: ')
    url_object = urlparse(redirect_url)
    qs = parse_qs(url_object.query)

    # Error if user does not grant access to Spotify user data
    if qs.get('error'):
        print('Oh no! Our request to access your user data was denied!')
    else:
        print('Exchanging authorization code for access token...')

    # Exchange authorization code for access token
    token = requests.post('https://accounts.spotify.com/api/token',
                          data={'grant_type': 'authorization_code',
                                'code': qs.get('code'),
                                'redirect_uri': REDIRECT_URI,
                                'client_id': CLIENT_ID,
                                'client_secret': CLIENT_SECRET}).json()
    return token


def auth_spotify():
    # If REFRESH_TOKEN exists, user wanted to be remembered from last session, so refresh access token
    print('Recognizing Spotify user...')
    if REFRESH_TOKEN:
        print('User is recognized. Refreshing Spotify access token...')
        token = refresh_token()
    else:
        print('User is unrecognized. Requesting Spotify authorization code...')
        token = request_token()

    global access_token
    access_token = token['access_token']

    # Ask user if they would like to be remembered for next session
    print_hdiv()
    while True:
        remember_me = input('Would you like your Spotify access information to be remembered next session (y/n)? ')
        # If yes, save the refresh token to environment variables
        if remember_me.lower() == 'y':
            try:
                print("We'll remember you next time! ;)")
                set_key(find_dotenv(), 'REFRESH_TOKEN', token['refresh_token'])
            except KeyError:
                pass
            break
        # If no, make sure refresh token is unset in environment variables
        elif remember_me.lower() == 'n':
            print('Erasing you from memory...bye! :(')
            unset_key(find_dotenv(), 'REFRESH_TOKEN')
            break
        else:
            pass
    print_hdiv()

    user_object = requests.get('https://api.spotify.com/v1/me',
                               headers={'Authorization': 'Bearer ' + access_token}).json()
    print(f"Successfully logged into Spotify as {user_object['id']}")


def main():
    # Initialize TIDAL session using credentials defined in .env
    print('Logging into TIDAL session...')
    session = tidalapi.Session()
    session.login(TIDAL_EMAIL, TIDAL_PASS)
    if session.check_login():
        print(f'Successfully logged into TIDAL as {TIDAL_EMAIL}')

    # Authenticate Spotify and get access token
    auth_spotify()

    # Queries user for valid TIDAL playlist URL
    print_hdiv()
    while True:
        tidal_url = input('Enter TIDAL playlist URL: ')
        tidal_playlist_id = tidal_url[34:]
        try:
            tidal_playlist = session.get_playlist(tidal_playlist_id)
            break
        except requests.exceptions.HTTPError:
            print('Invalid TIDAL playlist URL.')
    print_hdiv()


if __name__ == '__main__':
    main()
