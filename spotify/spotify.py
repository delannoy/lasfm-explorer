#!/usr/bin/env python3

from __future__ import annotations
import dataclasses
import datetime
import base64
import json
import logging
import os
import urllib
import typing

import awkward
import rich.logging
import rich.prompt

'''[Spotify Web API](https://developer.spotify.com/documentation/web-api/reference/)'''

rich_handler = rich.logging.RichHandler(rich_tracebacks=True, log_time_format="[%Y-%m-%d %H:%M:%S]") # [rich.logging](https://rich.readthedocs.io/en/stable/reference/logging.html)
logging.basicConfig(level=logging.DEBUG, format='%(message)s', handlers=[rich_handler])

def csv(values: list[str], sep: str = ',') -> str:
    if values is not None:
        return str.join(sep, values)

SCOPE = {
        'image': {'ugc-image-upload': True},
        'spotify_connect': {'user-read-playback-state': True, 'user-modify-playback-state': True, 'user-read-currently-playing': True},
        'playback': {'app-remote-control': False, 'streaming': False},
        'playlists': {'playlist-read-private': True, 'playlist-read-collaborative': True, 'playlist-modify-private': True, 'playlist-modify-public': True},
        'follow': {'user-follow-modify': True, 'user-follow-read': True},
        'listening_history': {'user-read-playback-position': True, 'user-top-read': True, 'user-read-recently-played': True},
        'library': {'user-library-modify': True, 'user-library-read': True},
        'users': {'user-read-email': True, 'user-read-private': True},
        'open_access': {'user-soa-link': False, 'user-soa-unlink': False, 'user-manage-entitlements': False, 'user-manage-partner': False, 'user-create-partner': False}
        }
SCOPE = [scope for category, scopes in SCOPE.items() for scope, granted in scopes.items() if granted]


@dataclasses.dataclass
class Auth:
    client_id: str = os.getenv('SPOTIFY_CLIENT_ID')
    client_secret: str = os.getenv('SPOTIFY_CLIENT_SECRET')
    refresh_token: str = os.getenv('SPOTIFY_REFRESH_TOKEN')
    access_token_validity: float = 0.0
    redirect_uri: str = 'https://localhost:8888/callback'

    def __post_init__(self):
        '''Verify that `SPOTIFY_CLIENT_ID` and `SPOTIFY_CLIENT_SECRET` enviroment variables are set.'''
        assert (self.client_id and self.client_secret), '\nPlease create an application:\nhttps://developer.spotify.com/dashboard/applications\n\nand set the following environment variables:\nSPOTIFY_CLIENT_ID\nSPOTIFY_CLIENT_SECRET'

    def __getattribute__(self, attr):
        '''Intercept attribute lookup for `self.access_token`: request user auth and create access_token+refresh_token if `self.refresh_token` is not defined & request a new access_token if it has expired.'''
        now = datetime.datetime.now(tz=datetime.timezone.utc).timestamp()
        if (attr == 'access_token') and (not self.refresh_token):
            code = self.userAuth()
            self.requestAccessToken(code=code)
        if (attr == 'access_token') and (now > self.access_token_validity):
            self.refreshAccessToken()
            return self.access_token
        return super().__getattribute__(attr)

    def clientAuth(self) -> dict[str, str]:
        '''Encode `self.client_id` and `self.client_secret` as base 64 strings.'''
        # [How to use urllib with username/password authentication in python 3?](https://stackoverflow.com/a/24648149)
        s = f'{self.client_id}:{self.client_secret}'.encode('utf-8')
        auth = base64.b64encode(s=s).decode('utf-8')
        return {'Authorization': f'Basic {auth}'}

    def token(self) -> str:
        '''[Client Credentials Flow | Request authorization](https://developer.spotify.com/documentation/web-api/tutorials/client-credentials-flow#request-authorization)'''
        url = 'https://accounts.spotify.com/api/token'
        data = urllib.parse.urlencode(query={'grant_type': 'client_credentials'}).encode('utf-8')
        request = urllib.request.Request(method='POST', url=url, data=data, headers=self.clientAuth())
        with urllib.request.urlopen(url=request) as response:
            logging.debug(f'{request.method} | {response.status} | {request.full_url} | {dict(urllib.parse.parse_qsl(request.data.decode()))}')
            return json.loads(response.read().decode('utf-8')).get('access_token')

    def userAuth(self):
        '''[Authorization Code Flow | Request User Authorization](https://developer.spotify.com/documentation/web-api/tutorials/code-flow#request-user-authorization)'''
        # https://python.plainenglish.io/bored-of-libraries-heres-how-to-connect-to-the-spotify-api-using-pure-python-bd31e9e3d88a
        logging.warning(f'\nPlease make sure "{self.redirect_uri}" is whitelisted:\nhttps://developer.spotify.com/dashboard/{self.client_id}/settings\n')
        params = urllib.parse.urlencode(dict(client_id=self.client_id, response_type='code', redirect_uri=self.redirect_uri, scope=csv(SCOPE, sep=' ')))
        request = urllib.request.Request(method='GET', url=f'https://accounts.spotify.com/authorize?{params}')
        return input(f"Please log in and authorize the application through your browser:\n{request.full_url}\n\nand paste the 'code' parameter from the redirected url:\n")

    def accessToken(self, data: dict[str, str]):
        '''[Authorization Code Flow | Request Access Token](https://developer.spotify.com/documentation/web-api/tutorials/code-flow#request-access-token)'''
        data = urllib.parse.urlencode(query=data).encode('utf-8')
        headers = {**self.clientAuth(), 'Content-Type': 'application/x-www-form-urlencoded'}
        request = urllib.request.Request(method='POST', url='https://accounts.spotify.com/api/token', data=data, headers=headers)
        with urllib.request.urlopen(url=request) as response:
            logging.debug(f'{request.method} | {response.status} | {request.full_url} | {dict(urllib.parse.parse_qsl(request.data.decode()))}')
            return json.loads(response.read().decode('utf-8'))

    def requestAccessToken(self, code: str):
        '''[Authorization Code Flow | Request Access Token](https://developer.spotify.com/documentation/web-api/tutorials/code-flow#request-access-token)'''
        data = dict(grant_type='authorization_code', code=code, redirect_uri=self.redirect_uri)
        response = self.accessToken(data=data)
        logging.warning(f'\nStore your `refresh_token` somewhere safe:\n{response["refresh_token"]}\n\nand set it as the following environment variable:\nSPOTIFY_REFRESH_TOKEN')
        self.access_token, self.refresh_token = response.get('access_token'), response.get('refresh_token')
        self.access_token_validity = datetime.datetime.now(tz=datetime.timezone.utc).timestamp() + float(response.get('expires_in'))

    def refreshAccessToken(self):
        '''[Authorization Code Flow | Request a refreshed Access Token](https://developer.spotify.com/documentation/web-api/tutorials/code-flow#request-a-refreshed-access-token)'''
        data = dict(grant_type='refresh_token', refresh_token=self.refresh_token)
        response = self.accessToken(data=data)
        self.access_token = response.get('access_token')
        self.access_token_validity = datetime.datetime.now(tz=datetime.timezone.utc).timestamp() + float(response.get('expires_in'))


@dataclasses.dataclass
class Spotify:
    endpoint: str
    token: str
    url: str = 'https://api.spotify.com/v1'

    def __post_init__(self):
        self.url = f'{self.url}{self.endpoint}'

    @staticmethod
    def handleResponse(request: urllib.request.Request):
        '''Read and parse response to `request`.'''
        with urllib.request.urlopen(url=request) as response:
            msg = f'{request.method} | {response.status} | {request.full_url}'
            logging.info(f'{msg} | {request.data.decode()}') if request.data else logging.info(msg)
            response = response.read().decode('utf-8')
            return awkward.from_json(source=response) if response else response

    @staticmethod
    def handleHTTPError(http_error: urllib.error.HTTPError):
        '''Read and parse `http_error`.'''
        logging.error(f'{http_error.status} | {http_error.reason} | {http_error.url}')
        if 'json' in http_error.headers.get('Content-Type', ''):
            logging.error(json.loads(http_error.read().decode('utf-8')).get('error'))

    @classmethod
    def getResponse(cls, request: urllib.request.Request):
        '''Read and parse response for `request`.'''
        try:
            return cls.handleResponse(request=request)
        except urllib.error.HTTPError as http_error:
            return cls.handleHTTPError(http_error=http_error)

    def request(self, method: str, params: dict[str, typing.Any] = {}, data: dict[str, typing.Any] = {}):
        '''Instantiate an HTTP request of a given `method` with corresponding query `params` in the url'''
        params = {k: v for k, v in params.items() if v is not None}
        url = urllib.parse.urlparse(url=f'{self.url}?{urllib.parse.urlencode(query=params)}')
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': f'Bearer {self.token}'}
        if data:
            data = {k: v for k, v in data.items() if v is not None}
            data = json.dumps(data).encode('utf-8') # ["Error parsing JSON" when using Spotify API](https://stackoverflow.com/a/30100530) [Problem sending post requests to spotify api in python](https://stackoverflow.com/a/70234391)
            request = urllib.request.Request(method=method, url=urllib.parse.urlunparse(url), data=data, headers=headers)
        else:
            request = urllib.request.Request(method=method, url=urllib.parse.urlunparse(url), headers=headers)
        return self.getResponse(request=request)

    def delete(self, params: dict[str, typing.Any] = {}, data: dict[str, typing.Any] = {}):
        '''Instantiate an HTTP DELETE request'''
        return self.request(method='DELETE', params=params, data=data)

    def get(self, **kwargs):
        '''Instantiate an HTTP GET request'''
        return self.request(method='GET', params=kwargs)

    def post(self, params: dict[str, typing.Any] = {}, data: dict[str, typing.Any] = {}):
        '''Instantiate an HTTP POST request'''
        return self.request(method='POST', params=params, data=data)

    def put(self, params: dict[str, typing.Any] = {}, data: dict[str, typing.Any] = {}):
        '''Instantiate an HTTP PUT request'''
        return self.request(method='PUT', params=params, data=data)


@dataclasses.dataclass
class Album:
    auth: Auth

    def __post_init__(self):
        self.unsave = self.remove

    def infoSingle(self, id: str, market: str = None):
        '''[Get Album](https://developer.spotify.com/documentation/web-api/reference/get-an-album)'''
        return Spotify(endpoint=f'/albums/{id}', token=self.auth.token()).get(market=market)

    def info(self, ids: list[str], market: str = None):
        '''[Get Several Albums](https://developer.spotify.com/documentation/web-api/reference/get-multiple-albums)'''
        return Spotify(endpoint='/albums', token=self.auth.token()).get(ids=csv(ids), market=market)

    def tracks(self, id: str, limit: int = 20, offset: int = 0, market: str = None):
        '''[Get Album Tracks](https://developer.spotify.com/documentation/web-api/reference/get-an-albums-tracks)'''
        return Spotify(endpoint=f'/albums/{id}/tracks', token=self.auth.token()).get(id=id, limit=limit, offset=offset, market=market)

    def saved(self, limit: int = 20, offset: int = 0, market: str = None):
        '''[Get User's Saved Albums](https://developer.spotify.com/documentation/web-api/reference/get-users-saved-albums)'''
        return Spotify(endpoint='/me/albums', token=self.auth.access_token).get(limit=limit, offset=offset, market=market)

    def save(self, ids: list[str]):
        '''[Save Albums for Current User](https://developer.spotify.com/documentation/web-api/reference/save-albums-user)'''
        return Spotify(endpoint='/me/albums', token=self.auth.access_token).put(data=dict(ids=ids))

    def remove(self, ids: list[str]):
        '''[Remove Users' Saved Albums](https://developer.spotify.com/documentation/web-api/reference/remove-albums-user)'''
        return Spotify(endpoint='/me/albums', token=self.auth.access_token).delete(data=dict(ids=ids))

    def isSaved(self, ids: list[str]):
        '''[Check User's Saved Albums](https://developer.spotify.com/documentation/web-api/reference/check-users-saved-albums)'''
        return Spotify(endpoint='/me/albums/contains', token=self.auth.access_token).get(ids=csv(ids))

    def newReleases(self, country: str = None, limit: int = 20, offset: int = 0):
        '''[Get New Releases](https://developer.spotify.com/documentation/web-api/reference/get-new-releases)'''
        return Spotify(endpoint='/browse/new-releases', token=self.auth.token()).get(country=country, limit=limit, offset=offset)


@dataclasses.dataclass
class Artist:
    auth: Auth

    def infoSingle(self, id: str):
        '''[Get Artist](https://developer.spotify.com/documentation/web-api/reference/get-an-artist)'''
        return Spotify(endpoint=f'/artists/{id}', token=self.auth.token()).get()

    def info(self, ids: list[str]):
        '''[Get Several Artists](https://developer.spotify.com/documentation/web-api/reference/get-multiple-artists)'''
        return Spotify(endpoint='/artists', token=self.auth.token()).get(ids=csv(ids))

    def albums(self, id: str, include_groups: list[str] = None, limit: int = 20, offset: int = 0, market: str = None):
        '''[Get Artist's Albums](https://developer.spotify.com/documentation/web-api/reference/get-an-artists-albums)'''
        if include_groups:
            assert all(entity in ('album', 'single', 'appears_on', 'compilation') for entity in include_groups)
        return Spotify(endpoint=f'/artists/{id}/albums', token=self.auth.token()).get(id=id, include_groups=csv(include_groups), limit=limit, offset=offset, market=market)

    def topTracks(self, id: str, market: str):
        '''[Get Artist's Top Tracks](https://developer.spotify.com/documentation/web-api/reference/get-an-artists-top-tracks)'''
        # [Cannot retrieve an artist's top tracks](https://github.com/spotify/web-api/issues/650)
        return Spotify(endpoint=f'/artists/{id}/top-tracks', token=self.auth.token()).get(market=market)

    def related(self, id: str):
        '''[Get Artist's Related Artists](https://developer.spotify.com/documentation/web-api/reference/get-an-artists-related-artists)'''
        return Spotify(endpoint=f'/artists/{id}/related-artists', token=self.auth.token()).get()


@dataclasses.dataclass
class Audiobook:
    auth: Auth

    def __post_init__(self):
        self.unsave = self.remove

    def infoSingle(self, id: str, market: str = None):
        '''[Get an Audiobook](https://developer.spotify.com/documentation/web-api/reference/get-an-audiobook)'''
        return Spotify(endpoint=f'/audiobooks/{id}', token=self.auth.token()).get(market=market)

    def info(self, ids: list[str], market: str = None):
        '''[Get Several Audiobooks](https://developer.spotify.com/documentation/web-api/reference/get-multiple-audiobooks)'''
        return Spotify(endpoint='/audiobooks', token=self.auth.token()).get(ids=csv(ids), market=market)

    def chapters(self, id: str, limit: int = 20, offset: int = 0, market: str = None):
        '''[Get Audiobook Chapters](https://developer.spotify.com/documentation/web-api/reference/get-audiobook-chapters)'''
        return Spotify(endpoint=f'/audiobooks/{id}/chapters', token=self.auth.token()).get(limit=limit, offset=offset, market=market)

    def saved(self, limit: int = 20, offset: int = 0):
        '''[Get User's Saved Audiobooks](https://developer.spotify.com/documentation/web-api/reference/get-users-saved-audiobooks)'''
        return Spotify(endpoint='/me/audiobooks', token=self.auth.access_token).get(limit=limit, offset=offset)

    def save(self, ids: list[str]):
        '''[Save Audiobooks for Current User](https://developer.spotify.com/documentation/web-api/reference/save-audiobooks-user)'''
        return Spotify(endpoint='/me/audiobooks', token=self.auth.access_token).put(data=dict(ids=ids))

    def remove(self, ids: list[str]):
        '''[Remove User's Saved Audiobooks](https://developer.spotify.com/documentation/web-api/reference/remove-audiobooks-user)'''
        return Spotify(endpoint='/me/audiobooks', token=self.auth.access_token).delete(data=dict(ids=ids))

    def isSaved(self, ids: list[str]):
        '''[Check User's Saved Audiobooks](https://developer.spotify.com/documentation/web-api/reference/check-users-saved-audiobooks)'''
        return Spotify(endpoint='/me/audiobooks/contains', token=self.auth.access_token).get(ids=csv(ids))


@dataclasses.dataclass
class Category:
    auth: Auth

    def browse(self, country: str = None, locale: str = None, limit: int = 20, offset: int = 0):
        '''[Get Several Browse Categories](https://developer.spotify.com/documentation/web-api/reference/get-categories)'''
        return Spotify(endpoint='/browse/categories', token=self.auth.token()).get(country=country, locale=locale, limit=limit, offset=offset)

    def info(self, category_id: str, country: str = None, locale: str = None):
        '''[Get Single Browse Category](https://developer.spotify.com/documentation/web-api/reference/get-a-category)'''
        return Spotify(endpoint=f'/browse/categories/{category_id}', token=self.auth.token()).get(country=country, locale=locale)


@dataclasses.dataclass
class Chapter:
    auth: Auth

    def infoSingle(self, id: str, market: str = None):
        '''[Get a Chapter](https://developer.spotify.com/documentation/web-api/reference/get-a-chapter)'''
        return Spotify(endpoint=f'/chapters/{id}', token=self.auth.token()).get(market=market)

    def info(self, ids: list[str], market: str = None):
        '''[Get Several Chapters](https://developer.spotify.com/documentation/web-api/reference/get-several-chapters)'''
        return Spotify(endpoint='/chapters', token=self.auth.token()).get(ids=csv(ids), market=market)


@dataclasses.dataclass
class Episode:
    auth: Auth

    def __post_init__(self):
        self.unsave = self.remove

    def infoSingle(self, id: str, market: str = None):
        '''[Get Episode](https://developer.spotify.com/documentation/web-api/reference/get-an-episode)'''
        return Spotify(endpoint=f'/episodes/{id}', token=self.auth.access_token).get(market=market)

    def info(self, ids: list[str], market: str = None):
        '''[Get Several Episodes](https://developer.spotify.com/documentation/web-api/reference/get-multiple-episodes)'''
        return Spotify(endpoint='/episodes', token=self.auth.access_token).get(ids=csv(ids), market=market)

    def saved(self, limit: int = 20, offset: int = 0, market: str = None):
        '''[Get User's Saved Episodes](https://developer.spotify.com/documentation/web-api/reference/get-users-saved-episodes)'''
        return Spotify(endpoint='/me/episodes', token=self.auth.access_token).get(limit=limit, offset=offset, market=market)

    def save(self, ids: list[str]):
        '''[Save Episodes for Current User](https://developer.spotify.com/documentation/web-api/reference/save-episodes-user)'''
        return Spotify(endpoint='/me/episodes', token=self.auth.access_token).put(data=dict(ids=ids))

    def remove(self, ids: list[str]):
        '''[Remove User's Saved Episodes](https://developer.spotify.com/documentation/web-api/reference/remove-episodes-user)'''
        return Spotify(endpoint='/me/episodes', token=self.auth.access_token).delete(data=dict(ids=ids))

    def isSaved(self, ids: list[str]):
        '''[Check User's Saved Episodes](https://developer.spotify.com/documentation/web-api/reference/check-users-saved-episodes)'''
        return Spotify(endpoint='/me/episodes/contains', token=self.auth.access_token).get(ids=csv(ids))


@dataclasses.dataclass
class Genre:
    auth: Auth

    def seeds(self):
        '''[Get Available Genre Seeds](https://developer.spotify.com/documentation/web-api/reference/get-recommendation-genres)'''
        return Spotify(endpoint='/recommendations/available-genre-seeds', token=self.auth.token()).get()


@dataclasses.dataclass
class Market:
    auth: Auth

    def info(self):
        '''[Get Available Markets](https://developer.spotify.com/documentation/web-api/reference/get-available-markets)'''
        return Spotify(endpoint='/markets', token=self.auth.token()).get()


@dataclasses.dataclass
class Player:
    auth: Auth

    def __post_init__(self):
        self.currentlyPlaying = self.nowPlaying

    def playbackState(self, additional_types: list[str] = None, market: str = None):
        '''[Get Playback State](https://developer.spotify.com/documentation/web-api/reference/get-information-about-the-users-current-playback)'''
        if additional_types:
            assert additional_types in ('track', 'episode')
            additional_types = csv(additional_types)
        return Spotify(endpoint='/me/player', token=self.auth.access_token).get(additional_types=additional_types, market=market)

    def transferPlayback(self, device_ids: list[str], play: bool = None):
        '''[Transfer Playback](https://developer.spotify.com/documentation/web-api/reference/transfer-a-users-playback)'''
        return Spotify(endpoint='/me/player', token=self.auth.access_token).put(data=dict(device_ids=device_ids, play=play))

    def availableDevices(self):
        '''[Get Available Devices](https://developer.spotify.com/documentation/web-api/reference/get-a-users-available-devices)'''
        return Spotify(endpoint='/me/player/devices', token=self.auth.access_token).get()

    def nowPlaying(self, additional_types: list[str]= None, market: str = None):
        '''[Get Currently Playing Track](https://developer.spotify.com/documentation/web-api/reference/get-the-users-currently-playing-track)'''
        if additional_types:
            assert additional_types in ('track', 'episode')
            additional_types = csv(additional_types)
        return Spotify(endpoint='/me/player/currently-playing', token=self.auth.access_token).get(additional_types=additional_types, market=market)

    def play(self, device_id: str = None, context_uri: str = None, uris: list[str] = None, offset: dict[str, typing.Any] = None, position_ms: int = None):
        '''[Start/Resume Playback](https://developer.spotify.com/documentation/web-api/reference/start-a-users-playback)'''
        return Spotify(endpoint='/me/player/play', token=self.auth.access_token).put(params=dict(device_id=device_id), data=dict(context_uri=context_uri, uris=uris, offset=offset, position_ms=position_ms))

    def pause(self, device_id: str = None):
        '''[Pause Playback](https://developer.spotify.com/documentation/web-api/reference/pause-a-users-playback)'''
        return Spotify(endpoint='/me/player/pause', token=self.auth.access_token).put(params=dict(device_id=device_id))

    def next(self, device_id: str = None):
        '''[Skip To Next](https://developer.spotify.com/documentation/web-api/reference/skip-users-playback-to-next-track)'''
        return Spotify(endpoint='/me/player/next', token=self.auth.access_token).post(params=dict(device_id=device_id))

    def previous(self, device_id: str = None):
        '''[Skip To Previous](https://developer.spotify.com/documentation/web-api/reference/skip-users-playback-to-previous-track)'''
        return Spotify(endpoint='/me/player/previous', token=self.auth.access_token).post(params=dict(device_id=device_id))

    def seek(self, position_ms: int, device_id: str = None):
        '''[Seek To Position](https://developer.spotify.com/documentation/web-api/reference/seek-to-position-in-currently-playing-track)'''
        return Spotify(endpoint='/me/player/seek', token=self.auth.access_token).put(params=dict(position_ms=position_ms, device_id=device_id))

    def repeat(self, state: str, device_id: str = None):
        '''[Set Repeat Mode](https://developer.spotify.com/documentation/web-api/reference/set-repeat-mode-on-users-playback)'''
        assert state in ('track', 'context', 'off')
        return Spotify(endpoint='/me/player/repeat', token=self.auth.access_token).put(params=dict(state=state, device_id=device_id))

    def volume(self, volume_percent: int, device_id: str = None):
        '''[Set Playback Volume](https://developer.spotify.com/documentation/web-api/reference/set-volume-for-users-playback)'''
        return Spotify(endpoint='/me/player/volume', token=self.auth.access_token).put(params=dict(volume_percent=volume_percent, device_id=device_id))

    def shuffle(self, state: bool, device_id: str = None):
        '''[Toggle Playback Shuffle](https://developer.spotify.com/documentation/web-api/reference/toggle-shuffle-for-users-playback)'''
        return Spotify(endpoint='/me/player/shuffle', token=self.auth.access_token).put(params=dict(state=state, device_id=device_id))

    def recent(self, limit: int = 20, after: int = None, before: int = None):
        '''[Get Recently Played Tracks](https://developer.spotify.com/documentation/web-api/reference/get-recently-played)'''
        if after:
            assert before is None
        if before:
            assert after is None
        return Spotify(endpoint='/me/player/recently-played', token=self.auth.access_token).get(limit=limit, after=after, before=before)

    def queue(self):
        '''[Get the User's Queue](https://developer.spotify.com/documentation/web-api/reference/get-queue)'''
        return Spotify(endpoint='/me/player/queue', token=self.auth.access_token).get()

    def add(self, uri: str, device_id: str = None):
        '''[Add Item to Playback Queue](https://developer.spotify.com/documentation/web-api/reference/add-to-queue)'''
        return Spotify(endpoint='/me/player/queue', token=self.auth.access_token).post(params=dict(uri=uri, device_id=device_id))


@dataclasses.dataclass
class Playlist:
    auth: Auth

    def __post_init__(self):
        self.deleteTracks = self.removeTracks
        self.overwrite = self.replace

    def info(self, playlist_id: str, fields: list[str] = None, additional_types: list[str] = None, market: str = None):
        if additional_types:
            assert additional_types in ('track', 'episode')
            additional_types = csv(additional_types)
        '''[Get Playlist](https://developer.spotify.com/documentation/web-api/reference/get-playlist)'''
        return Spotify(endpoint=f'/playlists/{playlist_id}', token=self.auth.token()).get(fields=csv(fields), additional_types=additional_types, market=market)

    def modify(self, playlist_id: str, name: str = None, public: bool = None, collaborative: bool = None, description: str = None):
        '''[Change Playlist Details](https://developer.spotify.com/documentation/web-api/reference/change-playlist-details)'''
        return Spotify(endpoint=f'/playlists/{playlist_id}', token=self.auth.access_token).put(data=dict(name=name, public=public, collaborative=collaborative, description=description))

    def getTracks(self, playlist_id: str, fields: str = None, additional_types: str = None, limit: int = 20, offset: int = 0, market: str = None):
        '''[Get Playlist Items](https://developer.spotify.com/documentation/web-api/reference/get-playlists-tracks)'''
        if additional_types:
            assert additional_types in ('track', 'episode')
            additional_types = csv(additional_types)
        return Spotify(endpoint=f'/playlists/{playlist_id}/tracks', token=self.auth.access_token).get(fields=fields, additional_types=additional_types, limit=limit, offset=offset, market=market)

    def update(self, playlist_id: str, uris: list[str] = None, range_start: int = None, insert_before: int = None, range_length: int = None, snapshot_id: str = None):
        '''[Update Playlist Items](https://developer.spotify.com/documentation/web-api/reference/reorder-or-replace-playlists-tracks)'''
        if uris:
            assert not any([range_start, insert_before, range_length, snapshot_id])
        if any([range_start, insert_before, range_length, snapshot_id]):
            assert uris is None
        data = dict(uris=uris, range_start=range_start, insert_before=insert_before, range_length=range_length, snapshot_id=snapshot_id)
        return Spotify(endpoint=f'/playlists/{playlist_id}/tracks', token=self.auth.access_token).put(data=data)

    def reorder(self, playlist_id: str, range_start: int = None, insert_before: int = None, range_length: int = 1, snapshot_id: str = None):
        '''[Update Playlist Items](https://developer.spotify.com/documentation/web-api/reference/reorder-or-replace-playlists-tracks)'''
        return Spotify(endpoint=f'/playlists/{playlist_id}/tracks', token=self.auth.access_token).put(data=dict(range_start=range_start, insert_before=insert_before, range_length=range_length, snapshot_id=snapshot_id))

    def replace(self, playlist_id: str, uris: list[str] = None):
        '''[Update Playlist Items](https://developer.spotify.com/documentation/web-api/reference/reorder-or-replace-playlists-tracks)'''
        return Spotify(endpoint=f'/playlists/{playlist_id}/tracks', token=self.auth.access_token).put(data=dict(uris=uris))

    def addTracks(self, playlist_id: str, uris: list[str], position: int = None):
        '''[Add Items to Playlist](https://developer.spotify.com/documentation/web-api/reference/add-tracks-to-playlist)'''
        return Spotify(endpoint=f'/playlists/{playlist_id}/tracks', token=self.auth.access_token).post(data=dict(uris=uris, position=position))

    def removeTracks(self, playlist_id: str, tracks: list[dict[str, str]], snapshot_id: int = None):
        '''[Remove Playlist Items](https://developer.spotify.com/documentation/web-api/reference/remove-tracks-playlist)'''
        return Spotify(endpoint=f'/playlists/{playlist_id}/tracks', token=self.auth.access_token).delete(data=dict(tracks=tracks, snapshot_id=snapshot_id))

    def mine(self, limit: int = 20, offset: int = 0):
        '''[Get Current User's Playlists](https://developer.spotify.com/documentation/web-api/reference/get-a-list-of-current-users-playlists)'''
        return Spotify(endpoint='/me/playlists', token=self.auth.access_token).get(limit=limit, offset=offset)

    def get(self, user_id: str, limit: int = 20, offset: int = 0):
        '''[Get User's Playlists](https://developer.spotify.com/documentation/web-api/reference/get-list-users-playlists)'''
        return Spotify(endpoint=f'/users/{user_id}/playlists', token=self.auth.access_token).get(limit=limit, offset=offset)

    def create(self, user_id: str, name: str, public: bool = None, collaborative: bool = None, description: str = None):
        '''[Create Playlist](https://developer.spotify.com/documentation/web-api/reference/create-playlist)'''
        assert not all([public, collaborative])
        return Spotify(endpoint=f'/users/{user_id}/playlists', token=self.auth.access_token).post(data=dict(name=name, public=public, collaborative=collaborative, description=description))

    def featured(self, country: str = None, locale: str = None, timestamp: str = None, limit: int = 20, offset: int = 0):
        '''[Get Featured Playlists](https://developer.spotify.com/documentation/web-api/reference/get-featured-playlists)'''
        return Spotify(endpoint='/browse/featured-playlists', token=self.auth.token()).get(country=country, locale=locale, timestamp=timestamp, limit=limit, offset=offset)

    def category(self, category_id: str, country: str = None, limit: int = 20, offset: int = 0):
        '''[Get Category's Playlists](https://developer.spotify.com/documentation/web-api/reference/get-a-categories-playlists)'''
        return Spotify(endpoint=f'/browse/categories/{category_id}/playlists', token=self.auth.token()).get(category_id=category_id, country=country, limit=limit, offset=offset)

    def cover(self, playlist_id: str):
        '''[Get Playlist Cover Image](https://developer.spotify.com/documentation/web-api/reference/get-playlist-cover)'''
        return Spotify(endpoint=f'/playlists/{playlist_id}/images', token=self.auth.token()).get()

    def uploadCover(self, playlist_id: str, image: bytes):
        '''[Add Custom Playlist Cover Image](https://developer.spotify.com/documentation/web-api/reference/upload-custom-playlist-cover)'''
        url = f'https://api.spotify.com/v1/playlists/{playlist_id}/images'
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': f'Bearer {self.auth.access_token}'}
        request = urllib.request.Request(method='PUT', url=url, data=image, headers=headers)
        return Spotify.getResponse(request=request)


@dataclasses.dataclass
class Search:
    auth: Auth
    filter_album: tuple[str] = ('album', 'artist', 'tag:hipster,' 'tag:new', 'upc', 'year')
    filter_artist: tuple[str] = ('artist', 'genre', 'year')
    filter_track: tuple[str] = ('album', 'artist', 'genre', 'isrc', 'track', 'year')

    def item(self, q: str, type: list[str], include_external: str = None, limit: int = 20, offset: int = 0, market: str = None):
        '''[Search for Item](https://developer.spotify.com/documentation/web-api/reference/search)'''
        assert all(entity in ('album', 'artist', 'playlist', 'track', 'show', 'episode', 'audiobook') for entity in type)
        if include_external:
            assert include_external == 'audio'
        return Spotify(endpoint='/search', token=self.auth.token()).get(q=q, type=csv(type), include_external=include_external, limit=limit, offset=offset, market=market)


@dataclasses.dataclass
class Show:
    auth: Auth

    def __post_init__(self):
        self.unsave = self.remove

    def infoSingle(self, id: str, market: str = None):
        '''[Get Show](https://developer.spotify.com/documentation/web-api/reference/get-a-show)'''
        return Spotify(endpoint=f'/shows/{id}', token=self.auth.access_token).get(market=market)

    def info(self, ids: list[str], market: str = None):
        '''[Get Several Shows](https://developer.spotify.com/documentation/web-api/reference/get-multiple-shows)'''
        return Spotify(endpoint='/shows', token=self.auth.token()).get(ids=csv(ids), market=market)

    def episodes(self, id: str, limit: int = 20, offset: int = 0, market: str = None):
        '''[Get Show Episodes](https://developer.spotify.com/documentation/web-api/reference/get-a-shows-episodes)'''
        return Spotify(endpoint=f'/shows/{id}/episodes', token=self.auth.access_token).get(limit=limit, offset=offset, market=market)

    def saved(self, limit: int = 20, offset: int = 0):
        '''[Get User's Saved Shows](https://developer.spotify.com/documentation/web-api/reference/get-users-saved-shows)'''
        return Spotify(endpoint='/me/shows', token=self.auth.access_token).get(limit=limit, offset=offset)

    def save(self, ids: list[str]):
        '''[Save Shows for Current User](https://developer.spotify.com/documentation/web-api/reference/save-shows-user)'''
        return Spotify(endpoint='/me/shows', token=self.auth.access_token).put(data=dict(ids=ids))

    def remove(self, ids: list[str], market: str = None):
        '''[Remove User's Saved Shows](https://developer.spotify.com/documentation/web-api/reference/remove-shows-user)'''
        return Spotify(endpoint='/me/shows', token=self.auth.access_token).delete(data=dict(ids=ids, market=market))

    def isSaved(self, ids: list[str]):
        '''[Check User's Saved Shows](https://developer.spotify.com/documentation/web-api/reference/check-users-saved-shows)'''
        return Spotify(endpoint='/me/shows/contains', token=self.auth.access_token).get(ids=csv(ids))


@dataclasses.dataclass
class Track:
    auth: Auth

    def __post_init__(self):
        self.unsave = self.remove

    def infoSingle(self, id: str, market: str = None):
        '''[Get Track](https://developer.spotify.com/documentation/web-api/reference/get-track)'''
        return Spotify(endpoint=f'/tracks/{id}', token=self.auth.token()).get(market=market)

    def info(self, ids: list[str], market: str = None):
        '''[Get Several Tracks](https://developer.spotify.com/documentation/web-api/reference/get-several-tracks)'''
        return Spotify(endpoint='/tracks', token=self.auth.token()).get(ids=csv(ids), market=market)

    def saved(self, limit: int = 20, offset: int = 0, market: str = None):
        '''[Get User's Saved Tracks](https://developer.spotify.com/documentation/web-api/reference/get-users-saved-tracks)'''
        return Spotify(endpoint='/me/tracks', token=self.auth.access_token).get(limit=limit, offset=offset, market=market)

    def save(self, ids: list[str]):
        '''[Save Tracks for Current User](https://developer.spotify.com/documentation/web-api/reference/save-tracks-user)'''
        return Spotify(endpoint='/me/tracks', token=self.auth.access_token).put(data=dict(ids=ids))

    def remove(self, ids: list[str]):
        '''[Remove User's Saved Tracks](https://developer.spotify.com/documentation/web-api/reference/remove-tracks-user)'''
        return Spotify(endpoint='/me/tracks', token=self.auth.access_token).delete(data=dict(ids=ids))

    def isSaved(self, ids: list[str]):
        '''[Check User's Saved Tracks](https://developer.spotify.com/documentation/web-api/reference/check-users-saved-tracks)'''
        return Spotify(endpoint='/me/tracks/contains', token=self.auth.access_token).get(ids=csv(ids))

    def audioFeatures(self, ids: list[str]):
        '''[Get Tracks' Audio Features](https://developer.spotify.com/documentation/web-api/reference/get-several-audio-features)'''
        return Spotify(endpoint='/audio-features', token=self.auth.token()).get(ids=csv(ids))

    def audioFeaturesSingle(self, id: str):
        '''[Get Track's Audio Features](https://developer.spotify.com/documentation/web-api/reference/get-audio-features)'''
        return Spotify(endpoint=f'/audio-features/{id}', token=self.auth.token()).get(id=id)

    def audioAnalysis(self, id: str):
        ''''[Get Track's Audio Analysis](https://developer.spotify.com/documentation/web-api/reference/get-audio-analysis)'''
        return Spotify(endpoint=f'/audio-analysis/{id}', token=self.auth.token()).get(id=id)

    def recommendations(self, seed_artists: list[str], seed_genres: list[str], seed_tracks: list[str],
            min_acousticness: float = None, max_acousticness: float = None, target_acousticness: float = None,
            min_danceability: float = None, max_danceability: float = None, target_danceability: float = None,
            min_duration_ms: int = None, max_duration_ms: int = None, target_duration_ms: int = None,
            min_energy: float = None, max_energy: float = None, target_energy: float = None,
            min_instrumentalness: float = None, max_instrumentalness: float = None, target_instrumentalness: float = None,
            min_key: float = None, max_key: float = None, target_key: float = None,
            min_liveness: float = None, max_liveness: float = None, target_liveness: float = None,
            min_loudness: float = None, max_loudness: float = None, target_loudness: float = None,
            min_mode: float = None, max_mode: float = None, target_mode: float = None,
            min_popularity: float = None, max_popularity: float = None, target_popularity: float = None,
            min_speechiness: float = None, max_speechiness: float = None, target_speechiness: float = None,
            min_tempo: float = None, max_tempo: float = None, target_tempo: float = None,
            min_time_signature: float = None, max_time_signature: float = None, target_time_signature: float = None,
            min_valence: float = None, max_valence: float = None, target_valence: float = None,
            limit: int = 20, market: str = None):
        '''[Get Recommendations](https://developer.spotify.com/documentation/web-api/reference/get-recommendations)'''
        return Spotify(endpoint='/recommendations', token=self.auth.token()).get(seed_artists=csv(seed_artists), seed_genres=csv(seed_genres), seed_tracks=csv(seed_tracks),
                min_acousticness=min_acousticness, max_acousticness=max_acousticness, target_acousticness=target_acousticness,
                min_danceability=min_danceability, max_danceability=max_danceability, target_danceability=target_danceability,
                min_duration_ms=min_duration_ms, max_duration_ms=max_duration_ms, target_duration_ms=target_duration_ms,
                min_energy=min_energy, max_energy=max_energy, target_energy=target_energy,
                min_instrumentalness=min_instrumentalness, max_instrumentalness=max_instrumentalness, target_instrumentalness=target_instrumentalness,
                min_key=min_key, max_key=max_key, target_key=target_key,
                min_liveness=min_liveness, max_liveness=max_liveness, target_liveness=target_liveness,
                min_loudness=min_loudness, max_loudness=max_loudness, target_loudness=target_loudness,
                min_mode=min_mode, max_mode=max_mode, target_mode=target_mode,
                min_popularity=min_popularity, max_popularity=max_popularity, target_popularity=target_popularity,
                min_speechiness=min_speechiness, max_speechiness=max_speechiness, target_speechiness=target_speechiness,
                min_tempo=min_tempo, max_tempo=max_tempo, target_tempo=target_tempo,
                min_time_signature=min_time_signature, max_time_signature=max_time_signature, target_time_signature=target_time_signature,
                min_valence=min_valence, max_valence=max_valence, target_valence=target_valence,
                limit=limit, market=market)


@dataclasses.dataclass
class User:
    auth: Auth

    def me(self):
        '''[Get Current User's Profile](https://developer.spotify.com/documentation/web-api/reference/get-current-users-profile)'''
        return Spotify(endpoint='/me', token=self.auth.access_token).get()

    def topItems(self, type: str, time_range: str = 'medium_term', limit: int = 20, offset: int = 0):
        '''[Get User's Top Items](https://developer.spotify.com/documentation/web-api/reference/get-users-top-artists-and-tracks)'''
        assert time_range in ('short_term', 'medium_term', 'long_term')
        return Spotify(endpoint=f'/me/top/{type}', token=self.auth.access_token).get(time_range=time_range, limit=limit, offset=offset)

    def profile(self, user_id: str):
        '''[Get User's Profile](https://developer.spotify.com/documentation/web-api/reference/get-users-profile)'''
        return Spotify(endpoint=f'/users/{user_id}', token=self.auth.token()).get()

    def followPlaylist(self, playlist_id: str, public: bool = True):
        '''[Follow Playlist](https://developer.spotify.com/documentation/web-api/reference/follow-playlist)'''
        return Spotify(endpoint=f'/playlists/{playlist_id}/followers', token=self.auth.access_token).put(data=dict(public=public))

    def unfollowPlaylist(self, playlist_id: str):
        '''[Follow Playlist](https://developer.spotify.com/documentation/web-api/reference/follow-playlist)'''
        return Spotify(endpoint=f'/playlists/{playlist_id}/followers', token=self.auth.access_token).delete()

    def followedArtists(self, type: str = 'artist', after: str = None, limit: int = 20):
        '''[Get Followed Artists](https://developer.spotify.com/documentation/web-api/reference/get-followed)'''
        assert type in ('artist')
        return Spotify(endpoint='/me/following', token=self.auth.access_token).get(type=type, after=after, limit=limit)

    def follow(self, type: str, ids: list[str]):
        '''[Follow Artists or Users](https://developer.spotify.com/documentation/web-api/reference/follow-artists-users)'''
        assert type in ('artist', 'user')
        return Spotify(endpoint='/me/following', token=self.auth.access_token).put(params=dict(type=type), data=dict(ids=ids))

    def unfollow(self, type: str, ids: list[str]):
        '''[Unfollow Artists or Users](https://developer.spotify.com/documentation/web-api/reference/unfollow-artists-users)'''
        assert type in ('artist', 'user')
        return Spotify(endpoint='/me/following', token=self.auth.access_token).delete(params=dict(type=type), data=dict(ids=ids))

    def isFollowing(self, type: str, ids: list[str]):
        '''[Check If User Follows Artists or Users](https://developer.spotify.com/documentation/web-api/reference/check-current-user-follows)'''
        assert type in ('artist', 'user')
        return Spotify(endpoint='/me/following', token=self.auth.access_token).get(type=type, ids=csv(ids))

    def areFollowingPlaylist(self, playlist_id: str, ids: list[str]):
        '''[Check if Users Follow Playlist](https://developer.spotify.com/documentation/web-api/reference/check-if-user-follows-playlist)'''
        return Spotify(endpoint=f'/playlists/{playlist_id}/followers/contains', token=self.auth.token()).get(ids=csv(ids))
