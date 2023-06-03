import json
import sys
import time

import googleapiclient
import spotipy
import pickle
import google
import os
from spotipy.oauth2 import SpotifyOAuth
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

TITLE_STRING = r"""
   _____             __  _ ____         ______         __  __           ______      __       
  / ___/____  ____  / /_(_) __/_  __   /_  __/___      \ \/ /___  __  _/_  __/_  __/ /_  ___ 
  \__ \/ __ \/ __ \/ __/ / /_/ / / /    / / / __ \      \  / __ \/ / / // / / / / / __ \/ _ \
 ___/ / /_/ / /_/ / /_/ / __/ /_/ /    / / / /_/ /      / / /_/ / /_/ // / / /_/ / /_/ /  __/
/____/ .___/\____/\__/_/_/  \__, /    /_/  \____/      /_/\____/\__,_//_/  \__,_/_.___/\___/ 
    /_/                    /____/                                                                                                                                                                                                                                                                                                                     
    """

if sys.platform == "win32" or sys.platform == "win64":  # Windows
    from colorama import init
    from colorama import Fore

    init()
    INFO_PREFIX = Fore.GREEN + "[INFO] " + Fore.RESET
    WARNING_PREFIX = Fore.YELLOW + "[WARNING] " + Fore.RESET
    ERROR_PREFIX = Fore.RED + "[ERROR] " + Fore.RESET

    TITLE = Fore.GREEN + TITLE_STRING
else:
    from termcolor import colored

    INFO_PREFIX = colored("[INFO] ", "green")
    WARNING_PREFIX = colored("[WARNING] ", "yellow")
    ERROR_PREFIX = colored("[ERROR] ", "red")

    TITLE = colored(TITLE_STRING, "green")


def retry(func, max_retries):
    retries = 0
    while retries < max_retries:
        try:
            func()
            return 0
        except:
            retries += 1
            time.sleep(1)


def get_spotify_playlist_id(link):
    try:
        start = link.find("/playlist/") + len("/playlist/")
        end = link.find("?")
        return link[start:end]
    except Exception as id_exception:
        print(
            ERROR_PREFIX + f"Es gab einen Fehler beim Extrahieren der Playlist ID! Mehr Infos: {id_exception}")


class SpotifyToYouTube:
    def __init__(self, spotify_playlist_link_arg):
        self.client_id_spotify = 'YOUR_SPOTIFY_CLIENT_ID'
        self.client_secret_spotify = 'YOUR_SPOTIFY_CLIENT_SECRET'

        self.spotify_scope = "playlist-read-private"
        self.spotify_username = "YOUR_SPOTIFY_USERNAME"

        self.youtube_playlist_description = 'My Spotify Playlist as a YouTube Playlist'
        self.youtube_playlist_privacy_status = 'private'
        self.youtube_playlist_id = ""

        self.youtube = None

        self.song_titles_file_path = "song_titles.txt"
        self.song_titles_list = ""
        try:
            if os.path.exists(self.song_titles_file_path):
                self.song_titles = open(self.song_titles_file_path, "r")

                existing_playlist_link_id = ""
                spotify_playlist_link_id = ""
                existing_txt_item_content = ""

                try:
                    existing_txt_item_content = self.song_titles.read().splitlines()
                    existing_playlist_link = existing_txt_item_content[0].strip()
                    existing_playlist_link_id = get_spotify_playlist_id(existing_playlist_link)
                    spotify_playlist_link_id = get_spotify_playlist_id(spotify_playlist_link_arg)
                except IndexError:
                    existing_playlist_link = ""

                if existing_playlist_link_id != spotify_playlist_link_id or existing_playlist_link_id == "":
                    print(
                        WARNING_PREFIX + "Achtung! Du bist dabei eine neue Spotify Playlist zu einer YouTube Playlist umzuwandeln!\n"
                                         "Dabei wird dein alter Fortschritt beim Übertragen der Playlist überschrieben.\n"
                                         "Möchtest du wirklich eine neue Playlist auf YouTube übertragen? [yes/no]")
                    answer = input("> ")
                    match answer:
                        case "yes":
                            self.spotify_playlist_link = spotify_playlist_link_arg
                            self.song_titles.truncate(0)
                            self.song_titles.write(self.spotify_playlist_link + '\n')
                            self.song_titles_list = ""
                        case "no":
                            self.spotify_playlist_link = existing_playlist_link
                            self.song_titles_list = existing_txt_item_content
                        case _:
                            print(WARNING_PREFIX + "Bitte gib eine valide Antwort [yes/no] an!")
                            input("")
                            sys.exit()
                elif existing_playlist_link_id == spotify_playlist_link_id:
                    self.spotify_playlist_link = spotify_playlist_link_arg
                    self.song_titles_list = existing_txt_item_content
            else:
                self.song_titles = open(self.song_titles_file_path, "a+")
                self.spotify_playlist_link = spotify_playlist_link_arg
                self.song_titles.write(self.spotify_playlist_link + '\n')
                self.song_titles_list = self.get_song_titles()
        except Exception as file_exception:
            print(ERROR_PREFIX + f"Es gab einen Fehler beim Öffnen der Datei. Mehr Infos: {file_exception}")

        self.song_titles.close()

        self.spotify_playlist_id = get_spotify_playlist_id(self.spotify_playlist_link)

        self.credentials = None

        self.spotify_token = SpotifyOAuth(scope=self.spotify_scope, username=self.spotify_username,
                                          client_id=self.client_id_spotify,
                                          client_secret=self.client_secret_spotify,
                                          redirect_uri='http://localhost:5000/')

        self.spotify = spotipy.Spotify(auth_manager=self.spotify_token)

        self.spotify_playlist_name = self.get_spotify_playlist_name()

    def get_song_titles(self):
        playlist_tracks = self.get_playlist_tracks()
        return playlist_tracks

    def get_playlist_tracks(self):
        tracks = []

        offset = 0
        limit = 100

        while True:
            playlist_tracks = self.spotify.playlist_items(self.spotify_playlist_link, offset=offset,
                                                          limit=limit)
            tracks.extend(playlist_tracks["items"])
            if playlist_tracks["next"]:
                offset += limit
            else:
                break

        return tracks

    def login_oauth(self):
        flow = InstalledAppFlow.from_client_secrets_file('client_secrets.json',
                                                         [
                                                             'https://www.googleapis.com/auth/youtube'])
        flow.run_local_server(port=5000, prompt='consent', authorization_prompt_message='')
        self.credentials = flow.credentials

        with open('token.pickle', 'wb') as f:
            print(INFO_PREFIX + "Speichere Zugangsdaten in Datei...")

            pickle.dump(self.credentials, f)

    def login(self):
        if os.path.exists('token.pickle'):
            with open('token.pickle', 'rb') as token:
                print(INFO_PREFIX + "Lade Zugangsdaten von Datei...")

                self.credentials = pickle.load(token)

        # Credentials Code: https://www.youtube.com/watch?v=vQQEaSnQ_bs
        if not self.credentials or not self.credentials.valid:
            if self.credentials and self.credentials.expired and self.credentials.refresh_token:

                print(INFO_PREFIX + "Aktualisiere Zugangsdaten...")

                try:
                    self.credentials.refresh(Request())
                except google.auth.exceptions.RefreshError:
                    print(ERROR_PREFIX + "Zugangsdaten sind ungültig. Bitte neu einloggen.")
                    self.credentials = None
                    self.login_oauth()
            else:
                self.login_oauth()

        self.youtube = build('youtube', 'v3', credentials=self.credentials)

    def get_spotify_playlist_name(self):
        playlist = self.spotify.playlist(self.spotify_playlist_link)

        print(INFO_PREFIX + "Playlist gefunden: " + playlist['name'])

        return playlist["name"]

    def create_youtube_playlist(self):
        def create_playlist():
            create_playlist_request = self.youtube.playlists().insert(  # Erstelle Playlist
                part='snippet,status',
                body={
                    'snippet': {
                        'title': self.spotify_playlist_name,
                        'description': self.youtube_playlist_description
                    },
                    'status': {
                        'privacyStatus': self.youtube_playlist_privacy_status
                    }
                }
            )  # Cost 50
            create_playlist_response = create_playlist_request.execute()

            self.youtube_playlist_id = create_playlist_response['id']

            print(INFO_PREFIX + f"Die Playlist \"{create_playlist_response['snippet']['title']}\" wurde erstellt!")

        created = False

        playlists_request = self.youtube.playlists().list(  # Liste aller Playlists des Users
            part="id,snippet",
            mine=True,
            fields="items(id,snippet(title))"
        )  # Cost 1
        playlists_response = playlists_request.execute()

        self.song_titles = open(self.song_titles_file_path, "a")

        for playlist in playlists_response['items']:

            if playlist['snippet'][
                'title'].lower() == self.spotify_playlist_name.lower():  # Wenn Playlist bereits existiert

                print(INFO_PREFIX + f"Die Playlist \"{playlist['snippet']['title']}\" existiert bereits!")

                self.youtube_playlist_id = playlist['id']

                if os.path.getsize(self.song_titles_file_path) == 0:
                    nextPageToken = None
                    while True:
                        playlist_items_request = self.youtube.playlistItems().list(
                            part='snippet',
                            playlistId=self.youtube_playlist_id,
                            maxResults=50,
                            pageToken=nextPageToken
                        )  # Cost 1

                        playlist_items_response = playlist_items_request.execute()

                        for video in playlist_items_response['items']:
                            video_id = video['snippet']['resourceId']['videoId']
                            self.song_titles.write(video_id + "\n")

                        nextPageToken = playlist_items_response.get('nextPageToken')

                        if not nextPageToken:
                            break
                break
            elif not created:
                create_playlist()
                break

        else:
            create_playlist()

        self.song_titles.close()

    def add_spotify_songs_to_youtube_playlist(self):
        self.song_titles = open(self.song_titles_file_path, "a")

        def add_video():
            video_request = self.youtube.search().list(  # Nach YouTube Video für Song suchen
                part="id,snippet",
                type='video',
                q=track['name'] + ' - ' + track['artists'][0][
                    'name'],
                maxResults=1,
                fields="items(id(videoId),snippet(title))"
            )  # Cost 100
            video_response = video_request.execute()
            video_id = video_response['items'][0]['id'][
                'videoId']  # Video ID des ersten Videos aus der Suche
            video_title = video_response['items'][0]['snippet']['title']
            self.youtube.playlistItems().insert(
                part="snippet",
                body={
                    "snippet": {
                        "playlistId": self.youtube_playlist_id,
                        "position": 0,
                        "resourceId": {
                            "kind": "youtube#video",
                            "videoId": video_id
                        }
                    }
                }
            ).execute()  # Cost 50

            self.song_titles.write(song_title + "\n")

            return video_title

        i = 0

        for item in self.get_playlist_tracks():
            track = item['track']
            song_title = track['name'] + ' - ' + track['artists'][0]['name']
            if song_title not in self.song_titles_list:
                try:
                    video_title = add_video()
                    i += 1
                    print(INFO_PREFIX + f"Das Video \"{video_title}\" wurde zur Playlist hinzugefügt!")
                except googleapiclient.errors.HttpError as e:
                    if e.resp.status == 409 and 'SERVICE_UNAVAILABLE' in str(e):
                        print(ERROR_PREFIX + "YouTube API ist nicht verfügbar. Versuche es erneut...")
                        if retry(add_video, max_retries=3) == 0:
                            i += 1
        if i == 0:
            print(INFO_PREFIX + "Die YouTube Playlist enthält alle Spotify Playlist Lieder!")
        else:
            print(INFO_PREFIX + f"Es wurden {i} neue Lieder zur YouTube Playlist hinzugefügt!")

        self.song_titles.close()


def main(spotify_playlist_link_main):
    try:
        spotify_to_youtube = SpotifyToYouTube(spotify_playlist_link_main)
    except Exception as general_exception:
        print(
            ERROR_PREFIX + f"Es ist ein Fehler beim Erstellen des \'SpotifyToYouTube\' Objektes aufgetreten! Mehr Infos: {general_exception}")
        input("")
        sys.exit()
    spotify_to_youtube.login()
    try:
        spotify_to_youtube.create_youtube_playlist()
        spotify_to_youtube.add_spotify_songs_to_youtube_playlist()
    except Exception as e:
        if isinstance(e, googleapiclient.errors.HttpError):
            error = e.content
            error_json = json.loads(error)
            error_code = error_json['error']['code']
            error_message = error_json['error']['message']
            match error_code:
                case 403:
                    print(
                        ERROR_PREFIX + "Für heute wurden alle YouTube API Requests verbraucht. Versuche es morgen erneut.")
                case _:
                    print(
                        ERROR_PREFIX + f"Ein unbekannter Fehler ({error_code}, {error_message}) ist aufgetreten. Versuche es später erneut. Mehr Infos:\n" + e)
        else:
            print(ERROR_PREFIX + f"Ein unbekannter Fehler ist aufgetreten. {str(e)}")
    spotify_to_youtube.song_titles.close()
    print("\a")


if __name__ == '__main__':
    spotify_playlist_link = input("Was ist der Link zur Playlist? [Teilen > Link zu Playlist kopieren]\n> ")
    print(TITLE)
    main(spotify_playlist_link)
    input("")
