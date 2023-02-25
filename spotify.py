"""
Spotify api
"""
import doctest
import json
import os
import base64
from dotenv import load_dotenv
import requests
import pycountry

load_dotenv()

client_id = os.getenv("CLIENT_ID")
client_secret = os.getenv("CLIENT_SECRET")

def get_auth_header(token):
    """
    Returns auth header with provided token
    >>> get_auth_header("token")
    {'Authorization': 'Bearer token'}
    """
    return {'Authorization': 'Bearer ' + token}


def get_token():
    """
    Returns access token
    """
    auth_string = client_id + ":" + client_secret
    auth_bytes = auth_string.encode("UTF-8")
    auth_base64 = str(base64.b64encode(auth_bytes), "UTF-8")

    url = "https://accounts.spotify.com/api/token"

    headers = {
        'Authorization': 'Basic ' + auth_base64,
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {'grant_type': 'client_credentials'}
    results  = requests.post(url, headers = headers, data = data)
    json_result = json.loads(results.content)
    token = json_result["access_token"]

    return token

def search_artist(token, artist_name):
    """
    Finds artist from given artist_name and valid access token.
    Returns in json format.
    >>> token = get_token()
    >>> search_artist(token, "kalush")["artists"]["items"][0]["name"]
    'KALUSH'
    >>> search_artist(token, "RHCP")["artists"]["items"][0]["name"]
    'Red Hot Chili Peppers'
    >>> search_artist(token, "Антитіла")["artists"]["items"][0]["name"]
    'Antytila'
    """
    url = 	f"https://api.spotify.com/v1/search?q={artist_name}&type=artist&limit=1"
    results = requests.get(url, headers=get_auth_header(token))
    json_result = json.loads(results.content)
    return json_result

def get_markets(song_id, token):
    """
    Finds available markets for given song_id and valid access token.
    Returns in json format.
    >>> token = get_token()
    >>> 'ET' in get_markets("2vHzOWRKYPLu8umRPIFuOq",token)
    True
    >>> "PL" in get_markets("44FopWyaddRoiuNrD8hlUw", token)
    True
    >>> "AO" in get_markets("7exHT4swWOKL5addPeqkLP", token)
    True
    """
    url = f"https://api.spotify.com/v1/tracks/{song_id}"
    results = requests.get(url, headers=get_auth_header(token), params={"country":"US"})
    available_markets = json.loads(results.content)["available_markets"]
    return available_markets

def top_track(artist_id, token):
    """
    Finds top tracks for artist with artist_id using valid access token.
    Returns in json format.
    >>> token = get_token()
    >>> top_track("46rVVJwHWNS7C7MaWXd842", token)[0]["name"]
    'Stefania (Kalush Orchestra)'
    >>> top_track("5sc9td6C7xxPa3mOmmvXPu", token)[0]["name"]
    'Фортеця Бахмут'
    >>> top_track("5lLVx3mMyUvZ9QKzM09CZa", token)[0]["name"]
    'Тримай'
    """
    url = f"https://api.spotify.com/v1/artists/{artist_id}/top-tracks?country=US"
    results = requests.get(url, headers=get_auth_header(token))
    json_result = json.loads(results.content)["tracks"]
    return json_result

def main():
    """
    Main start function
    """
    token = get_token()
    artist_name = input("Write artist name: ")
    artist = search_artist(token, artist_name)["artists"]["items"][0]
    tracks = None
    print(f"_____ Information found about {artist['name']} _____")
    print(
    """
    Write:

    'id' - get id of the artist
    'top_track' - to get top track/s
    'genres' - to get genres of artist
    'markets' - to get available markets of the most popular song
    'exit' - to exit app
    """)
    while True:
        request = input(">>> ")
        if request == "id":
            print(artist["id"])
        elif request == "top_track":
            if tracks is None:
                tracks = top_track(artist["id"], token)
            request = print("""
    Write:
    
    one - to get one most popular song
    set - to get set of most popular songs
    back - to go back to choices
    """)
            choice = input(">>> ")
            if choice == "set":
                for id, track in enumerate(tracks):
                    print(f'{id + 1}) {track["name"]}')
            elif choice == "one":
                print(f'{tracks[0]["name"]}')
            else:
                pass
        elif request == "markets":
            if tracks is None:
                tracks = top_track(artist["id"], token)
            top_track_id = tracks[0]["id"]
            for code in get_markets(top_track_id, token):
                # print(code)
                try:
                    print(pycountry.countries.get(alpha_2=code).name)
                except AttributeError:
                    continue
        elif request == "genres":
            print("\n".join([genre.capitalize() for genre in artist["genres"]]))
        elif request == "exit":
            break

if __name__ == "__main__":
    # doctest.testmod()
    main()
