import os
import requests
import tidalapi

from dotenv import load_dotenv


def print_hdiv():
    print('----------')


def main():
    # Loads environment variables defined in .env
    load_dotenv()

    # Initialize TIDAL session using credentials defined in .env
    print('Logging into TIDAL session...')
    session = tidalapi.Session()
    session.login(os.getenv('TIDAL_EMAIL'), os.getenv('TIDAL_PASS'))
    if session.check_login():
        print(f"Successfully logged in as {os.getenv('TIDAL_EMAIL')}")
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


if __name__ == '__main__':
    main()
