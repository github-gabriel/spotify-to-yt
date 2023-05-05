<img src="https://user-images.githubusercontent.com/92476790/236544077-4332d50e-0a8c-4476-a40e-ba33993c9037.png" width="720px">

# Spotify To YT

Ich möchte oft die Musikvideos zu den Liedern in meiner Spotify Playlist sehen, daher habe ich mich entschieden ein Script
zu erstellen, welches alle Lieder einer Spotify Playlist auf YouTube sucht und den Top Vorschlag dann zu einer Playlist hinzufügt, sodass die Spotify Playlist am Ende 1:1 auf YouTube kopiert wird. Das Script ist auch für größere Playlists
ausgelegt, da es aufpasst wieviel Lieder es schon hinzgefügt hat und später ab dem Punkt dann einfach weitermachen kann.

## Setup

Um das Python Script aufzusetzen, installiere alle Module mit
```
pip install -r requirements.txt
```

Außerdem müssen folgende Variablen deklariert werden: 
```python
self.client_id_spotify = 'YOUR_SPOTIFY_CLIENT_ID'
self.client_secret_spotify = 'YOUR_SPOTIFY_CLIENT_SECRET'
self.spotify_scope = "playlist-read-private"
self.spotify_username = "YOUR_SPOTIFY_USERNAME"
```
### Spotify
Für die Spotify Client ID und Client Secret wird eine Spotify App benötigt, die im [Spotify Dashboard](https://developer.spotify.com/dashboard) erstellt werden kann.

<img src="https://user-images.githubusercontent.com/92476790/236543304-c24863a1-9b28-4434-b3ae-75b2f9524fc1.png" width="1280px">

### YouTube
Für den YouTube Teil des ganzen, wird ein YouTube API Key benötigt und ein OAuth Zustimmungsbildschirm.

<img src="https://user-images.githubusercontent.com/92476790/236543768-ebb9fb43-be40-4a62-ab60-603a33fa3d1c.png" width="1280px">

<img src="https://user-images.githubusercontent.com/92476790/236543760-62c18a11-4124-4b6f-8a1f-681a774ecc7d.png" width="1280px">

Am Ende kann man die "Daten" des OAuth Clients herunterladen. Diese werden als ```client_secrets.json``` im selben Verzeichnis wie
das Script benötigt. 

Das Aufsetzen des YouTube Teils ist etwas aufwendiger, deshalb möchte ich hier auf Tutorials von [Corey Schafer](https://www.youtube.com/@coreyms) verweisen, die mir sehr geholfen haben: 
- https://www.youtube.com/watch?v=vQQEaSnQ_bs&ab_channel=CoreySchafer
- https://www.youtube.com/watch?v=th5_9woFJmk&ab_channel=CoreySchafer

## Demo

Hier ein Video zur Demonstration des Scriptes:

https://user-images.githubusercontent.com/92476790/236546110-6f06f25b-f0f8-4f18-a584-751c9415e373.mp4

## ⚠️Mögliche Fehler⚠️

Ich hatte beim Ausprobieren des Scripts den Fehler, dass ich mich über OAuth anmelde, das Script dann aber nicht funktioniert. Wenn ```token.pickle``` (Zugangsdaten) erfolgreich erstellt wurde kann man das Programm einfach beenden und dann neustarten. Das hat in meinem Fall geholfen, bei weiteren Problemen einfach ein Issue öffnen.
