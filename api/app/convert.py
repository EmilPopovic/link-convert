import logging
import requests
import re
from difflib import SequenceMatcher
import base64
import time

from secret_manager import get_secret


LOG_FORMAT = (
    '%(asctime)s | %(levelname)-8s | %(name)s | %(filename)s:%(lineno)d | '
    '%(funcName)s() | %(threadName)s | %(message)s'
)


logging.basicConfig(
    level=logging.INFO,
    format=LOG_FORMAT,
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger(__name__)

SPOTIFY_CLIENT_ID = get_secret('SPOTIFY_CLIENT_ID')
SPOTIFY_CLIENT_SECRET = get_secret('SPOTIFY_CLIENT_SECRET')
YOUTUBE_API_KEY = get_secret('YOUTUBE_API_KEY')

logger.info('Loaded configuration: '
           f'SPOTIFY_CLIENT_ID={SPOTIFY_CLIENT_ID is not None}, '
           f'SPOTIFY_CLIENT_SECRET={SPOTIFY_CLIENT_SECRET is not None}, '
           f'YOUTUBE_API_KEY={YOUTUBE_API_KEY is not None}')


_spotify_token = None
_spotify_token_expiry = 0


def get_spotify_token():
    global _spotify_token, _spotify_token_expiry

    if _spotify_token and time.time() < _spotify_token_expiry:
        return _spotify_token

    logger.info('Refreshing Spotify token...')

    token_url = 'https://accounts.spotify.com/api/token'
    auth_header = base64.b64encode(f'{SPOTIFY_CLIENT_ID}:{SPOTIFY_CLIENT_SECRET}'.encode()).decode()
    headers = {
        'Authorization': f'Basic {auth_header}',
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    data = {
        'grant_type': 'client_credentials'
    }

    response = requests.post(token_url, headers=headers, data=data)
    if response.status_code != 200:
        raise Exception(f'Failed to get Spotify token: {response.text}')

    token_info = response.json()
    _spotify_token = token_info['access_token']
    _spotify_token_expiry = time.time() + token_info['expires_in'] - 30  # renew 30 seconds early

    return _spotify_token


def extract_spotify_track_id(url: str) -> str | None:
    match = re.search(r'track/([a-zA-Z0-9_-]+)', url)
    return match.group(1) if match else None


def extract_youtube_video_id(url: str) -> str | None:
    match = re.search(r'v=([a-zA-Z0-9_-]+)', url)
    return match.group(1) if match else None


def get_spotify_track_info(track_id: str) -> dict:
    token = get_spotify_token()
    headers = {
        'Authorization': f'Bearer {token}'
    }
    response = requests.get(
        f'https://api.spotify.com/v1/tracks/{track_id}',
        headers=headers
    )
    if response.status_code != 200:
        raise Exception('Spotify track not found')
    data = response.json()
    return {
        'title': data['name'],
        'artist': data['artists'][0]['name'],
        'album': data['album']['name'],
        'duration_ms': data['duration_ms']
    }


def search_youtube_music(query: str) -> tuple[str | None, float]:
    url = 'https://www.googleapis.com/youtube/v3/search'
    params = {
        'part': 'snippet',
        'q': query,
        'type': 'video',
        'videoCategoryId': '10',
        'key': YOUTUBE_API_KEY,
    }
    response = requests.get(url, params=params)
    if response.status_code != 200:
        raise Exception('YouTube search failed')
    items = response.json().get('items', [])
    if not items:
        return None, 0.0
    best = items[0]
    confidence = SequenceMatcher(None, query.lower(), best['snippet']['title'].lower()).ratio()
    return f'https://music.youtube.com/watch?v={best['id']['videoId']}', confidence


def get_youtube_track_info(video_id: str) -> dict | None:
    url = 'https://www.googleapis.com/youtube/v3/videos'
    params = {
        'part': 'snippet,contentDetails',
        'id': video_id,
        'key': YOUTUBE_API_KEY
    }
    response = requests.get(url,params=params)
    if response.status_code != 200:
        raise Exception('YouTube video not found')
    items = response.json().get('items', [])
    if not items:
        return None
    snippet = items[0]['snippet']
    return {
        'title': snippet['title'],
        'artist': snippet.get('channelTitle'),
        'album': None,
        'duration_ms': None
    }


def search_spotify_track(title, artist) -> tuple[str | None, float]:
    token = get_spotify_token()
    headers = {
        'Authorization': f'Bearer {token}'
    }
    query = f'{title} {artist}'
    params = {
        'q': query,
        'type': 'track',
        'limit': 1
    }
    response = requests.get('https://api.spotify.com/v1/search', headers=headers, params=params)
    if response.status_code != 200:
        raise Exception('Spotify search failed.')
    items = response.json().get('tracks', {}).get('items', [])
    if not items:
        return None, 0.0
    track = items[0]
    match_query = f'{title} {artist}'
    found_title = f'{track['name']} {track['artists'][0]['name']}'
    confidence = SequenceMatcher(None, match_query.lower(), found_title.lower()).ratio()
    return f'https://open.spotify.com/track/{track['id']}', confidence


def convert_spotify_to_youtube(spotify_url):
    track_id = extract_spotify_track_id(spotify_url)
    if track_id is None:
        raise Exception('Invalid Spotify URL.')
    track_info = get_spotify_track_info(track_id)
    youtube_url, confidence = search_youtube_music(f'{track_info['title']} {track_info['artist']}')
    return {
        'youtube_music_url': youtube_url,
        'match_confidence': confidence,
        'track_info': track_info
    }

def convert_youtube_to_spotify(youtube_url):
    video_id = extract_youtube_video_id(youtube_url)
    if video_id is None:
        raise Exception('Invalid YouTube URL.')
    track_info = get_youtube_track_info(video_id)
    if not track_info:
        raise Exception('Could not extract YouTube track info.')
    spotify_url, confidence = search_spotify_track(track_info['title'], track_info['artist'])
    return {
        'spotify_url': spotify_url,
        'match_confidence': confidence,
        'track_info': track_info
    }
