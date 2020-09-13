import os
import tidalapi


def main():
    tidal_url = input('Enter TIDAL playlist URL: ')
    while not(tidal_url.startswith('https://tidal.com/browse/playlist/')):
        print('Invalid TIDAL playlist URL.')
        tidal_url = input('Enter TIDAL playlist URL: ')


if __name__ == '__main__':
    main()
