import json
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
          'Please be ready to copy and paste the URL of the web page you are redirected to after you grant us access.\n')
    time.sleep(5)

    # Get authorization code that can be exchanged for an access token
    webbrowser.open(code_response.url)
    redirect_url = input('Please copy and paste the URL of the website you were redirected to: ')
    # TODO: Error handling for pasted URL
    print_hdiv()
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
    return user_object['id']


def print_tidal_playlist(playlist, items):
    print('Playlist ID:', playlist.id)
    print('Title:', playlist.name)
    print('Description:', playlist.description)
    print('Date Created:', playlist.created)
    print('Creator:', playlist.creator)
    print('Duration:', playlist.duration)
    print('Public?:', playlist.is_public)
    print('Date Last Modified:', playlist.last_updated)
    print('Number of Tracks:', playlist.num_tracks)
    print('Contents:')
    for item in items:
        print('    ' + item.name + ' by ' + item.artist.name)


def get_users_spotify_playlists():
    spotify_playlists = requests.get('https://api.spotify.com/v1/me/playlists',
                                     headers={'Authorization': 'Bearer ' + access_token}).json()
    playlists = []
    for playlist in spotify_playlists['items']:
        playlists.append(playlist['name'])

    return playlists


def search_spotify(query):
    results = requests.get('https://api.spotify.com/v1/search',
                           headers={
                               'Authorization': 'Bearer ' + access_token
                           },
                           params={
                               # TODO: something is wrong with URL query encoding
                               'q': query,
                               'type': 'track',
                               'offset': 0,
                               'limit': 1
                           }).json()
    return results


def main():
    # Initialize TIDAL session using credentials defined in .env
    print('Logging into TIDAL session...')
    session = tidalapi.Session()
    session.login(TIDAL_EMAIL, TIDAL_PASS)
    if session.check_login():
        print(f'Successfully logged into TIDAL as {TIDAL_EMAIL}')
    else:
        print('Uh oh! Error logging in to TIDAL.')
        exit()

    # Authenticate Spotify and get access token
    spotify_user_id = auth_spotify()
    print(f"Successfully logged into Spotify as {spotify_user_id}")

    # Queries user for valid TIDAL playlist URL
    print_hdiv()
    while True:
        tidal_url = input('Enter TIDAL playlist URL: ')
        tidal_playlist_id = tidal_url[34:]
        try:
            tidal_playlist = session.get_playlist(tidal_playlist_id)
            tidal_playlist_items = session.get_playlist_items(tidal_playlist_id)
            break
        except requests.exceptions.HTTPError:
            print('Invalid TIDAL playlist URL.')

    print('TIDAL Playlist Information:')
    print_tidal_playlist(tidal_playlist, tidal_playlist_items)
    print_hdiv()

    # Ask user if they would like to create a Spotify playlist under the same name
    while True:
        same_name = input(
            f'Would you like create the Spotify playlist under the same TIDAL playlist name \'{tidal_playlist.name}\' (y/n)? ')
        if same_name.lower() == 'y':
            spotify_playlist_name = tidal_playlist.name
            break
        elif same_name.lower() == 'n':
            spotify_playlist_name = input('Enter your desired new Spotify playlist name: ')
            break

    # Check if user already has a Spotify playlist under the inputted playlist name
    spotify_playlists = get_users_spotify_playlists()
    i = 0
    while i < len(spotify_playlists):
        if spotify_playlist_name == spotify_playlists[i]:
            print(f'A Spotify playlist named \'{spotify_playlist_name}\' already exists under your user!')
            spotify_playlist_name = input('Please enter a playlist name that does not already exist: ')
            i = 0
        else:
            i += 1

    # Create new Spotify playlist as inputted name.
    print(f'Creating a new Spotify playlist named \'{spotify_playlist_name}\'...')
    payload = {
        'name': spotify_playlist_name,
        'public': True,
        'collaborative': False,
        'description': tidal_playlist.description
    }
    spotify_playlist = requests.post(f'https://api.spotify.com/v1/users/{spotify_user_id}/playlists',
                                     headers={
                                         'Authorization': 'Bearer ' + access_token,
                                         'Content-Type': 'application/json'
                                     },
                                     data=json.dumps(payload)).json()
    print(f'Successfully created Spotify playlist \'{spotify_playlist_name}\'')

    # Search Spotify for tracks in TIDAL playlist
    print('Adding tracks from TIDAL playlist to Spotify playlist...')
    spotify_uris = []
    tracks_not_added = []
    for item in tidal_playlist_items:
        try:
            # If Spotify track found, add Spotify URI to spotify_uris.
            results = search_spotify(item.name + ' ' + item.artist.name)
            spotify_uris.append(results['tracks']['items'][0]['uri'])
        except IndexError:
            # If not, add TIDAL track to tracks_not_added.
            tracks_not_added.append(item.name + ' by ' + item.artist.name)

    # Add Spotify tracks from spotify_uris to Spotify playlist
    requests.post(f"https://api.spotify.com/v1/playlists/{spotify_playlist['id']}/tracks",
                  headers=
                  {
                      'Authorization': 'Bearer ' + access_token,
                      'Content-Type': 'application/json'
                  },
                  data=json.dumps(spotify_uris))

    # Print completed status with number of tracks added and contents of tracks_not_added
    print(f'Successfully added {len(spotify_uris)} track(s) to Spotify playlist \'{spotify_playlist_name}\'.')
    print(f'{len(tracks_not_added)} track(s) could not be found on Spotify.')
    if len(tracks_not_added) > 0:
        print('TIDAL tracks not found on Spotify:')
        for track in tracks_not_added:
            print('    ' + track.name + ' by ' + track.artist.name)

    # Open Spotify playlist in web browser
    webbrowser.open(spotify_playlist['external_urls']['spotify'])


if __name__ == '__main__':
    main()
