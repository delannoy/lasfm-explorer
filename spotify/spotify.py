#!/usr/bin/env python3

from __future__ import annotations
import dataclasses
import datetime
import base64
import json
import os
import urllib
import typing

import awkward

'''[Spotify Web API](https://developer.spotify.com/documentation/web-api/reference/)'''

ARTIST_ID = '3grvcGPaLhfrD5CYsecr4j'
ALBUM_ID = '5hbxMCegyQPhpycfjtlW6I'
TRACK_ID = '5dux3AkWPrlKFVcHDUqor2'
PLAYLIST_ID = '65PdVn8FEJiiAIbUekw4a1'

def csv(values: list[str], sep: str = ',') -> str:
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
            print(f'{request.method} | {response.status} | {request.full_url} | {dict(urllib.parse.parse_qsl(request.data.decode()))}')
            return json.loads(response.read().decode('utf-8')).get('access_token')

    def userAuth(self):
        '''[Authorization Code Flow | Request User Authorization](https://developer.spotify.com/documentation/web-api/tutorials/code-flow#request-user-authorization)'''
        # https://python.plainenglish.io/bored-of-libraries-heres-how-to-connect-to-the-spotify-api-using-pure-python-bd31e9e3d88a
        print(f'\nPlease make sure "{self.redirect_uri}" is whitelisted:\nhttps://developer.spotify.com/dashboard/{self.client_id}/settings\n')
        params = urllib.parse.urlencode(dict(client_id=self.client_id, response_type='code', redirect_uri=self.redirect_uri, scope=csv(SCOPE, sep=' ')))
        request = urllib.request.Request(method='GET', url=f'https://accounts.spotify.com/authorize?{params}')
        return input(f'Please log in and authorize the application through your browser:\n{request.full_url}\n\nand paste the "code" parameter in the redirect url:\n')

    def accessToken(self, data: dict[str, str]):
        '''[Authorization Code Flow | Request Access Token](https://developer.spotify.com/documentation/web-api/tutorials/code-flow#request-access-token)'''
        data = urllib.parse.urlencode(query=data).encode('utf-8')
        headers = {**self.clientAuth(), 'Content-Type': 'application/x-www-form-urlencoded'}
        request = urllib.request.Request(method='POST', url='https://accounts.spotify.com/api/token', data=data, headers=headers)
        with urllib.request.urlopen(url=request) as response:
            print(f'{request.method} | {response.status} | {request.full_url} | {dict(urllib.parse.parse_qsl(request.data.decode()))}')
            return json.loads(response.read().decode('utf-8'))

    def requestAccessToken(self, code: str):
        '''[Authorization Code Flow | Request Access Token](https://developer.spotify.com/documentation/web-api/tutorials/code-flow#request-access-token)'''
        data = dict(grant_type='authorization_code', code=code, redirect_uri=self.redirect_uri)
        response = self.accessToken(data=data)
        print(f'\nStore your `refresh_token` somewhere safe:\n{response["refresh_token"]}\n\nand set it as the following environment variable:\nSPOTIFY_REFRESH_TOKEN')
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

    @staticmethod
    def handleResponse(request: urllib.request.Request):
        with urllib.request.urlopen(url=request) as response:
            msg = f'{request.method} | {response.status} | {request.full_url}'
            print(f'{msg} | {request.data.decode()}') if request.data else print(msg)
            response = response.read().decode('utf-8')
            return awkward.from_json(source=response) if response else response

    @staticmethod
    def handleHTTPError(http_error: urllib.error.HTTPError):
        print(f'{http_error.status} | {http_error.reason} | {http_error.url}')
        if 'json' in http_error.headers.get('Content-Type', ''):
            print(json.loads(http_error.read().decode('utf-8')).get('error'))

    @classmethod
    def getResponse(cls, request: urllib.request.Request):
        try:
            return cls.handleResponse(request=request)
        except urllib.error.HTTPError as http_error:
            return cls.handleHTTPError(http_error=http_error)

    @classmethod
    def request(cls, method: str, endpoint: str, token: str, params: dict[str, typing.Any] = {}, data: dict[str, typing.Any] = {}):
        params = {k: v for k, v in params.items() if v}
        url = urllib.parse.urlparse(url=f'https://api.spotify.com/v1{endpoint}?{urllib.parse.urlencode(query=params)}')
        headers = {'Accept': 'application/json', 'Content-Type': 'application/json', 'Authorization': f'Bearer {token}'}
        if data:
            data = json.dumps(data).encode('utf-8') # ["Error parsing JSON" when using Spotify API](https://stackoverflow.com/a/30100530) [Problem sending post requests to spotify api in python](https://stackoverflow.com/a/70234391)
            request = urllib.request.Request(method=method, url=urllib.parse.urlunparse(url), data=data, headers=headers)
        else:
            request = urllib.request.Request(method=method, url=urllib.parse.urlunparse(url), headers=headers)
        return cls.getResponse(request=request)

    @classmethod
    def delete(cls, endpoint: str, token: str, params: dict[str, typing.Any] = {}, data: dict[str, typing.Any] = {}):
        return cls.request(method='DELETE', endpoint=endpoint, token=token, params=params, data=data)

    @classmethod
    def get(cls, endpoint: str, token: str, **kwargs):
        return cls.request(method='GET', endpoint=endpoint, token=token, params=kwargs)

    @classmethod
    def post(cls, endpoint: str, token: str, params: dict[str, typing.Any] = {}, data: dict[str, typing.Any] = {}):
        return cls.request(method='POST', endpoint=endpoint, token=token, params=params, data=data)

    @classmethod
    def put(cls, endpoint: str, token: str, params: dict[str, typing.Any] = {}, data: dict[str, typing.Any] = {}):
        return cls.request(method='PUT', endpoint=endpoint, token=token, params=params, data=data)


@dataclasses.dataclass
class Album:
    auth: Auth

    def __post_init__(self):
        self.unsave = self.remove

    def get(self, id: str, market: str = ''):
        '''[Get Album](https://developer.spotify.com/documentation/web-api/reference/get-an-album)'''
        return Spotify.get(endpoint=f'/albums/{id}', token=self.auth.token(), market=market)

    def info(self, ids: list[str], market: str = ''):
        '''[Get Several Albums](https://developer.spotify.com/documentation/web-api/reference/get-multiple-albums)'''
        return Spotify.get(endpoint=f'/albums', token=self.auth.token(), ids=csv(ids), market=market)

    def tracks(self, id: str, market: str = '', limit: int = 20, offset: int = 0):
        '''[Get Album Tracks](https://developer.spotify.com/documentation/web-api/reference/get-an-albums-tracks)'''
        return Spotify.get(endpoint=f'/albums/{id}/tracks', token=self.auth.token(), id=id, market=market, limit=limit, offset=offset)

    def saved(self, limit: int = 20, offset: int = 0, market: str = ''):
        '''[Get User's Saved Albums](https://developer.spotify.com/documentation/web-api/reference/get-users-saved-albums)'''
        return Spotify.get(endpoint='/me/albums', token=self.auth.access_token, limit=limit, offset=offset, market=market)

    def save(self, ids: list[str]):
        '''[Save Albums for Current User](https://developer.spotify.com/documentation/web-api/reference/save-albums-user)'''
        return Spotify.put(endpoint='/me/albums', token=self.auth.access_token, data={'ids': ids})
        # return Spotify.put(endpoint='/me/albums', token=self.auth.access_token, params={'ids': csv(ids)})

    def remove(self, ids: list[str]):
        '''[Remove Users' Saved Albums](https://developer.spotify.com/documentation/web-api/reference/remove-albums-user)'''
        return Spotify.delete(endpoint='/me/albums', token=self.auth.access_token, data={'ids': ids})
        # return Spotify.delete(endpoint='/me/albums', token=self.auth.access_token, params={'ids': csv(ids)})

    def isSaved(self, ids: list[str]):
        '''[Check User's Saved Albums](https://developer.spotify.com/documentation/web-api/reference/check-users-saved-albums)'''
        return Spotify.get(endpoint='/me/albums/contains', token=self.auth.access_token, ids=csv(ids))

    def newReleases(self, country: str = '', limit: int = 20, offset: int = 0):
        '''[Get New Releases](https://developer.spotify.com/documentation/web-api/reference/get-new-releases)'''
        return Spotify.get(endpoint='/browse/new-releases', token=self.auth.token(), country=country, limit=limit, offset=offset)


@dataclasses.dataclass
class Artist:
    auth: Auth

    def get(self, id: str):
        '''[Get Artist](https://developer.spotify.com/documentation/web-api/reference/get-an-artist)'''
        return Spotify.get(endpoint=f'/artists/{id}', token=self.auth.token())

    def info(self, ids: list[str]):
        '''[Get Several Artists](https://developer.spotify.com/documentation/web-api/reference/get-multiple-artists)'''
        return Spotify.get(endpoint=f'/artists', token=self.auth.token(), ids=csv(ids))

    def albums(self, id: str, include_groups: list[str] = [], market: str = '', limit: int = 20, offset: int = 0):
        '''[Get Artist's Albums](https://developer.spotify.com/documentation/web-api/reference/get-an-artists-albums)'''
        if include_groups:
            assert all(entity in ('album', 'single', 'appears_on', 'compilation') for entity in include_groups)
        return Spotify.get(endpoint=f'/artists/{id}/albums', token=self.auth.token(), id=id, include_groups=csv(include_groups), market=market, limit=limit, offset=offset)

    def topTracks(self, id: str, market: str):
        '''[Get Artist's Top Tracks](https://developer.spotify.com/documentation/web-api/reference/get-an-artists-top-tracks)'''
        # [Cannot retrieve an artist's top tracks](https://github.com/spotify/web-api/issues/650)
        return Spotify.get(endpoint=f'/artists/{id}/top-tracks', token=self.auth.token(), market=market)

    def related(self, id: str):
        '''[Get Artist's Related Artists](https://developer.spotify.com/documentation/web-api/reference/get-an-artists-related-artists)'''
        return Spotify.get(endpoint=f'/artists/{id}/related-artists', token=self.auth.token())


@dataclasses.dataclass
class Audiobook:
    auth: Auth


@dataclasses.dataclass
class Categories:
    auth: Auth


@dataclasses.dataclass
class Chapter:
    auth: Auth


@dataclasses.dataclass
class Genre:
    auth: Auth


@dataclasses.dataclass
class Market:
    auth: Auth


@dataclasses.dataclass
class Player:
    auth: Auth


@dataclasses.dataclass
class Playlist:
    auth: Auth


@dataclasses.dataclass
class Search:
    auth: Auth


@dataclasses.dataclass
class Show:
    auth: Auth


@dataclasses.dataclass
class Track:
    auth: Auth


@dataclasses.dataclass
class User:
    auth: Auth

    def me(self):
        '''[Get Current User's Profile](https://developer.spotify.com/documentation/web-api/reference/get-current-users-profile)'''
        return Spotify.get(endpoint='/mex', token=self.auth.access_token)

    def topItems(self, type: str, time_range: str = 'medium_term', limit: int = 20, offset: int = 0):
        '''[Get User's Top Items](https://developer.spotify.com/documentation/web-api/reference/get-users-top-artists-and-tracks)'''
        assert time_range in ('short_term', 'medium_term', 'long_term')
        return Spotify.get(endpoint=f'/me/top/{type}', token=self.auth.access_token, time_range=time_range, limit=limit, offset=offset)

    def profile(self, user_id: str):
        '''[Get User's Profile](https://developer.spotify.com/documentation/web-api/reference/get-users-profile)'''
        return Spotify.get(endpoint=f'/users/{user_id}', token=self.auth.token())

    def followPlaylist(self, playlist_id: str, public: bool = True):
        '''[Follow Playlist](https://developer.spotify.com/documentation/web-api/reference/follow-playlist)'''
        return Spotify.put(endpoint=f'/playlists/{playlist_id}/followers', token=self.auth.access_token, data={'public': public})

    def unfollowPlaylist(self, playlist_id: str):
        '''[Follow Playlist](https://developer.spotify.com/documentation/web-api/reference/follow-playlist)'''
        return Spotify.delete(endpoint=f'/playlists/{playlist_id}/followers', token=self.auth.access_token)

    def followedArtists(self, type: str = 'artist', after: str = '', limit: int = 20):
        '''[Get Followed Artists](https://developer.spotify.com/documentation/web-api/reference/get-followed)'''
        assert type in ('artist')
        return Spotify.get(endpoint='/me/following', token=self.auth.access_token, type=type, after=after, limit=limit)

    def follow(self, type: str, ids: list[str]):
        '''[Follow Artists or Users](https://developer.spotify.com/documentation/web-api/reference/follow-artists-users)'''
        assert type in ('artist', 'user')
        return Spotify.put(endpoint='/me/following', token=self.auth.access_token, params={'type': type}, data={'ids': ids})
        # return Spotify.put(endpoint='/me/following', token=self.auth.access_token, params={'type': type, 'ids': csv(ids)})

    def unfollow(self, type: str, ids: list[str]):
        '''[Unfollow Artists or Users](https://developer.spotify.com/documentation/web-api/reference/unfollow-artists-users)'''
        assert type in ('artist', 'user')
        return Spotify.delete(endpoint='/me/following', token=self.auth.access_token, params={'type': type}, data={'ids': ids})
        # return Spotify.delete(endpoint='/me/following', token=self.auth.access_token, params={'type': type, 'ids': csv(ids)})

    def isFollowing(self, type: str, ids: list[str]):
        '''[Check If User Follows Artists or Users](https://developer.spotify.com/documentation/web-api/reference/check-current-user-follows)'''
        assert type in ('artist', 'user')
        return Spotify.get(endpoint='/me/following', token=self.auth.access_token, type=type, ids=csv(ids))

    def areFollowingPlaylist(self, playlist_id: str, ids: list[str]):
        '''[Check if Users Follow Playlist](https://developer.spotify.com/documentation/web-api/reference/check-if-user-follows-playlist)'''
        return Spotify.get(endpoint=f'/playlists/{playlist_id}/followers/contains', token=self.auth.token(), ids=csv(ids))
