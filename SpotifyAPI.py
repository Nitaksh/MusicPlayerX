import base64
import requests
import os 


client_id = "5ff0d8b57f3f46dfa59d9f8211c94e7b"
client_secret = "dc3cf25db6ed416291ecaf87c64688e7"


def get_access_token(client_id, client_secret):
    auth_str = f"{client_id}:{client_secret}"
    b64_auth_str = base64.urlsafe_b64encode(auth_str.encode()).decode()

    headers = {
        "Authorization": f"Basic {b64_auth_str}",
    }

    data = {
        "grant_type": "client_credentials",
    }

    response = requests.post("https://accounts.spotify.com/api/token", headers=headers, data=data)
    response_data = response.json()

    return response_data["access_token"]

def search_song(access_token, song_name):
    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    params = {
        "q": song_name,
        "type": "track",
        "limit": 1,
    }

    response = requests.get("https://api.spotify.com/v1/search", headers=headers, params=params)
    response_data = response.json()

    # Extract details of the first result
    if response_data["tracks"]["items"]:
        first_result = response_data["tracks"]["items"][0]
        song_details = {
            "name": first_result["name"],
            "artists": [artist["name"] for artist in first_result["artists"]],
            "album": first_result["album"]["name"],
            "release_date": first_result["album"]["release_date"],
            "popularity": first_result["popularity"],
            "track_id": first_result["id"],  # Adding the track ID to the song_details
        }
        return song_details
    else:
        return None

def get_audio_features(access_token, track_id):
    headers = {
        "Authorization": f"Bearer {access_token}",
    }

    response = requests.get(f"https://api.spotify.com/v1/audio-features/{track_id}", headers=headers)
    features_data = response.json()

    return features_data

def get_metadata(song_name):
    access_token = get_access_token(client_id, client_secret)
    song_details = search_song(access_token, song_name)
    
    if song_details:
        track_id = song_details["track_id"]
        audio_features = get_audio_features(access_token, track_id)
        
        song_details["audio_features"] = audio_features  # Adding audio features to song_details
        return song_details
    
    return None
'''
song_name = "Maroon 5 animals"
song_details = get_metadata(song_name)

if song_details:
    print("Song Name:", song_details["name"])
    print("Artists:", ", ".join(song_details["artists"]))
    print("Album:", song_details["album"])
    print("Release Date:", song_details["release_date"])
    print("Audio Features:", song_details["audio_features"])
'''