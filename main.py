import os
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
    tidal_url = input('Enter TIDAL playlist URL: ')
    while not(tidal_url.startswith('https://tidal.com/browse/playlist/')):
        print('Invalid TIDAL playlist URL.')
        tidal_url = input('Enter TIDAL playlist URL: ')
    print_hdiv()


if __name__ == '__main__':
    main()
