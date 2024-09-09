#!/usr/bin/env python3

from __future__ import annotations
import dataclasses
import datetime
import enum
import hashlib
import json
import logging
import os
import pathlib
import typing
import urllib
import uuid
import xml.etree.ElementTree

import dateparser
import rich.logging
import pydantic

import models

try:
    API_KEY = uuid.UUID(os.environ['LASTFM_KEY']).hex # [Create API account](https://www.last.fm/api/account/create) [API Applications(https://www.last.fm/api/accounts)
except KeyError as error:
    logging.error('Please define your last.fm api_key as an environment variable:\nexport LASTFM_KEY=your_lastfm_api_key')
    raise SystemExit

logging.basicConfig(level=logging.DEBUG, format='%(message)s', handlers=[rich.logging.RichHandler(rich_tracebacks=True, log_time_format='[%Y-%m-%d %H:%M:%S]')])

HEADERS = {'User-Agent': 'delannoy/0.2 (a@delannoy.cc)'}
FORMAT = 'json'
JSON_TYPE = typing.Dict[str, typing.Any]
RESPONSE_TYPE = pydantic.BaseModel if (FORMAT == 'json') else xml.etree.ElementTree

def validate(check: bool, message: str) -> None:
    '''Raise `ValueError` with `message` if `check` is `False`.'''
    if not check:
        raise ValueError(message)

def deprecated_api_methods():
    '''Query methods deprecated from the Last.FM API.'''
    api = json.loads(urllib.request.urlopen('https://github.com/jkbrzt/lastfmclient/raw/master/api.json').read().decode('utf-8'))
    return {f"{package}.{method}({', '.join(api[package][method]['params'].keys())})" for package in api for method in api[package] if (not package.startswith('_')) and (not getattr(globals().get(package, None), method, None))}
    {f'{package}.{method}': Request.get(method=f'{package}.{method}', api_key=API_KEY) for package in api for method in api[package] if (not package.startswith('_')) and (not getattr(globals().get(package, None), method, None))}
    sorted(set(kwargs.lower() for method in [api[package][method].get('params', {}).keys() for package in api for method in api[package] if (not package.startswith('_'))] for kwargs in method))


class Errors(enum.IntEnum):
    '''https://www.last.fm/api/errorcodes''' # [Last.fm Error Codes](https://lastfm-docs.github.io/api-docs/codes/)

    def __new__(cls, value: int, doc: str = ''):
        '''override Enum.__new__ to take a doc argument''' # [How can I attach documentation to members of a python enum?](https://stackoverflow.com/a/50473952)
        self = int.__new__(cls, value)
        self._value_ = value
        self.__doc__ = doc
        return self

    INVALID_SERVICE = (2, "Invalid service - This service does not exist")
    INVALID_METHOD = (3, "Invalid Method - No method with that name in this package")
    AUTHENTICATION_FAILED = (4, "Authentication Failed - You do not have permissions to access the service")
    INVALID_FORMAT = (5, "Invalid format - This service doesn't exist in that format")
    INVALID_PARAMETERS = (6, "Invalid parameters - Your request is missing a required parameter")
    INVALID_RESOURCE = (7, "Invalid resource specified")
    OPERATION_FAILED = (8, "Operation failed - Something else went wrong")
    INVALID_SESSION_KEY = (9, "Invalid session key - Please re-authenticate")
    INVALID_API_KEY = (10, "Invalid API key - You must be granted a valid key by last.fm")
    SERVICE_OFFLINE = (11, "Service Offline - This service is temporarily offline. Try again later.")
    SUBSCRIBERS_ONLY = (12, "Subscribers Only - This station is only available to paid last.fm subscribers")
    INVALID_METHOD_SIGNATURE = (13, "Invalid method signature supplied")
    UNAUTHORIZED_TOKEN = (14, "Unauthorized Token - This token has not been authorized")
    EXPIRED_TOKEN = (15, "This item is not available for streaming.")
    TEMPORARY_ERROR = (16, "The service is temporarily unavailable, please try again.")
    LOGIN_REQUIRED = (17, "Login: User requires to be logged in")
    TRIAL_EXPIRED = (18, "Trial Expired - This user has no free radio plays left. Subscription required.")
    NOT_ENOUGH_CONTENT = (20, "Not Enough Content - There is not enough content to play this station")
    NOT_ENOUGH_MEMBERS = (21, "Not Enough Members - This group does not have enough members for radio")
    NOT_ENOUGH_FANS = (22, "Not Enough Fans - This artist does not have enough fans for for radio")
    NOT_ENOUGH_NEIGHBOURS = (23, "Not Enough Neighbours - There are not enough neighbours for radio")
    NO_PEAK_RADIO = (24, "No Peak Radio - This user is not allowed to listen to radio during peak usage")
    RADIO_NOT_FOUND = (25, "Radio Not Found - Radio station not found")
    SUSPENDED_API_KEY = (26, "API Key Suspended - This application is not allowed to make requests to the web services")
    DEPRECATED  = (27, "Deprecated - This type of request is no longer supported")
    RATE_LIMIT_EXCEEDED = (29, "Rate Limit Exceded - Your IP has made too many requests in a short period, exceeding our API guidelines")


class StrEnum(str, enum.Enum):
    @classmethod
    def list(cls):
        return sorted(enum.value for enum in cls)


class Message(StrEnum):
    ALBUM = '`artist` and `album` must be provided unless `mbid` is specified'
    ARTIST = '`artist` must be provided unless `mbid` is specified'
    TRACK = '`artist` and `track` must be provided unless `mbid` is specified'
    SK = '`session_key` is required; run `Auth.main()` to obtain one and define it as an environment variable:\nexport LASTFM_SESSION_KEY=your_lastfm_session_key'
    USER = '`user` is required unless a session key is provided as an environment variable:\nexport LASTFM_SESSION_KEY=your_lastfm_session_key'


class Period(StrEnum):
    OVERALL = 'overall'
    SEVEN_DAYS= '7day'
    ONE_WEEK = '7day'
    ONE_MONTH = '1month'
    THIRTY_DAYS = '1month'
    THREE_MONTHS = '3month'
    SIX_MONTHS = '6month'
    TWELVE_MONTHS = '12month'
    ONE_YEAR = '12month'


class TaggingType(StrEnum):
    ARTIST = 'artist'
    ALBUM = 'album'
    TRACK = 'track'


@dataclasses.dataclass
class Request:
    url: str = 'http://ws.audioscrobbler.com/2.0/'
    sleep: float = 0.2 # [Rate limit copied from pylast since it is not explicitly mentioned in the API Terms of Service](https://github.com/pylast/pylast/blob/master/src/pylast/__init__.py#L119)

    @staticmethod
    def parse_datetime(val: int|float|str|datetime.datetime) -> int:
        '''Parse `val` into UTC unix timestamp.'''
        if isinstance(val, (int, float)):
            return int(val)
        if isinstance(val, str):
            validate(check=dateparser.parse(val), message=f"Unable to parse '{val}' as a `datetime` object")
            val = dateparser.parse(val) if dateparser.parse(val).tzinfo else dateparser.parse(f'{val} UTC')
        return int(val.timestamp())

    @classmethod
    def validate_kwargs(cls, key: str, val: typing.Any) -> tuple[str, str|int]:
        '''Validate/parse `from` or `to` into UTC unix timestamp `int`, `lang` into ISO 639-1 `str`, `mbid` into `uuid.UUID` `str`, `tags` into comma-separated `str`, etc.'''
        key = key.lower()
        if key in ('autocorrect', 'extended', 'recenttracks'):
            validate(check=(int(val) in (0,1)), message=f'`{key}` must be either a boolean or an integer value (0 or 1)')
            val = int(val)
        if key in ('from', 'to'):
            val = cls.parse_datetime(val)
        if key == 'country':
            validate(check=(val in geo.countries()), message=f"'{key}' must be a valid ISO 3166-1 country name ('{val}' is not)")
        if key == 'lang':
            validate(check=(val in geo.languages()), message=f"'{key}' must be a valid 2-character ISO 639-1 country code ('{val}' is not)")
        if key == 'mbid':
            val = uuid.UUID(str(val))
        if key == 'period':
            validate(check=(val in Period.list()), message=f"'{key}' must be one of {Period.list()} ('{val}' is not)")
        if key == 'taggingtype':
            validate(check=(val in TaggingType.list()), message=f"'{key}' must be one of {TaggingType.list()} ('{val}' is not)")
        if key == 'tags' and isinstance(val, (list, tuple)):
            validate(check=(len(val) <= 10), message='A maximium of 10 `tags` are accepted')
            val = ','.join(str(item).replace(',', '') for item in val)
        return (key, f'{val}')

    @classmethod
    def request(cls, request_method: str, data: JSON_TYPE = None, **kwargs) -> urllib.request.Request:
        '''Instantiate a `urllib.request.Request` of given `request_method` with url parameters given by `kwargs` dictionary.'''
        kwargs = dict(cls.validate_kwargs(key, val) for key, val in kwargs.items() if val is not None)
        params = {**kwargs, 'format': FORMAT}
        logging.debug(params)
        url = urllib.parse.urlparse(url=f'{cls.url}?{urllib.parse.urlencode(query=params)}')
        data = urllib.parse.urlencode(params).encode('utf-8') if data else None
        return urllib.request.Request(method=request_method, url=urllib.parse.urlunparse(url), headers=HEADERS, data=data)

    @staticmethod
    def error(response: JSON_TYPE):
        logging.error(f"{response['message'] = }")
        if response.get('error') in {e.value for e in Errors}:
            error_enum = Errors(response.get('error'))
            logging.error(f"{error_enum.name}: {error_enum.__doc__}")

    @classmethod
    def urlopen(cls, request: urllib.request.Request) -> RESPONSE_TYPE:
        '''Fetch response for `request`.'''
        with urllib.request.urlopen(url=request) as response:
            logging.info(f'HTTP Request: {request.method} | {response.status} | {request.full_url}')
            if FORMAT != 'json':
                return response.read()
            response = json.loads(response.read().decode('utf-8'))
        if response.get('error'):
            cls.error(response)
        return response

    @classmethod
    def response(cls, request: urllib.request.Request) -> RESPONSE_TYPE:
        '''Fetch response for `request` and handle exceptions.'''
        try:
            return cls.urlopen(request=request)
        except json.JSONDecodeError as error:
            logging.error(f'json.JSONDecodeError: {error}')
        except urllib.error.HTTPError as http_error:
            logging.error(f'{http_error.status} | {http_error.reason} | {http_error.url} | {dict(http_error.headers)}')
            if 'json' in http_error.headers.get('Content-Type', ''):
                error = json.loads(http_error.read().decode('utf-8'))
                cls.error(error)
                return error

    @classmethod
    def get(cls, format: str = FORMAT, **kwargs) -> pydantic.BaseModel:
        '''Wrapper function for `urllib.request.urlopen` GET requests which accepts URL parameters from `kwargs`.'''
        request = cls.request(request_method='GET', **kwargs)
        response = cls.response(request=request)
        return cls.validate(response=response, method=kwargs.get('method'))

    @classmethod
    def post(cls, data: JSON_TYPE = None, **kwargs) -> pydantic.BaseModel:
        '''Wrapper function for `urllib.request.urlopen` POST requests which accepts URL parameters from `kwargs`.'''
        request = cls.request(request_method='POST', data=data, **kwargs)
        response = cls.response(request=request)
        return cls.validate(response=response, method=kwargs.get('method'))

    @staticmethod
    def validate(response: urllib.request.Request, method: str) -> pydantic.BaseModel:
        '''Determine the top level `entity` in the response and call the corresponding `pydantic` model to validate it.'''
        if (FORMAT != 'json') or (not response):
            return response
        if 'error' in response:
            return models.Error(**response)
        entity = next(iter(response))
        if method not in ('auth.getToken'):
            response = response.pop(entity)
        model = getattr(getattr(models, method.split('.')[0]), entity.capitalize())
        return model(**response)


@dataclasses.dataclass
class Auth:
    password: str = os.getenv('LASTFM_PASSWORD')
    secret: uuid.UUID = os.getenv('LASTFM_SECRET')
    session_key: str = os.getenv('LASTFM_SESSION_KEY')
    username: str = os.getenv('LASTFM_USER')

    @classmethod
    def calculate_api_sig(cls, params: JSON_TYPE) -> uuid.UUID:
        '''Calculates `api_sig` (sorts all method call `params`, merges them into a continous string of key & value pairs, and calculates md5).'''
        # [Authentication API](https://www.last.fm/api/authspec)
        # [Signature - Unofficial Last.fm API docs](https://lastfm-docs.github.io/api-docs/auth/signature/)
        # [Last.fm API invalid method signature but valid when getting session key](https://stackoverflow.com/a/45907546/13019084)
        validate(check=cls.secret, message='Please define your last.fm API secret as an environment variables:\nexport LASTFM_SECRET=your_lastfm_secret')
        params = {key: val for key, val in params.items() if val is not None}
        logging.debug(f"{dict(sorted(params.items()))} + '{cls.secret}'")
        sorted_params = [f'{key}{val}' for key, val in sorted(params.items()) if key not in ('api_sig', 'callback', 'format')]
        api_sig = str.join('', sorted_params) + uuid.UUID(cls.secret).hex
        logging.debug(f'{api_sig = }')
        api_sig = hashlib.md5(api_sig.encode('utf-8')).hexdigest()
        return uuid.UUID(api_sig).hex

    @classmethod
    def getMobileSession(cls, username: str = os.getenv('LASTFM_USER'), password: str = os.getenv('LASTFM_PASSWORD'), api_sig: uuid.UUID = None, api_key: uuid.UUID= API_KEY, method: str = 'auth.getMobileSession') -> RESPONSE_TYPE:
        '''Create a web service session for a user.'''
        validate(check=(username and password), message='Please define your last.fm username and password as environment variables:\nexport LASTFM_USER=your_lastfm_username\nexport LASTFM_PASSWORD=your_lastfm_password')
        api_sig = cls.calculate_api_sig(dict(username=username, password=password, method=method, api_key=api_key))
        return Request.post(**dict(username=username, password=password, method=method, api_key=api_key, api_sig=api_sig))

    @classmethod
    def getSession(cls, token: str, api_sig: uuid.UUID = None, api_key: uuid.UUID= API_KEY, method: str = 'auth.getSession') -> RESPONSE_TYPE:
        '''Fetch a session key for a user.'''
        api_sig = cls.calculate_api_sig(dict(token=token, method=method, api_key=api_key))
        return Request.get(**dict(token=token, method=method, api_key=api_key, api_sig=api_sig))

    @classmethod
    def getToken(cls, api_sig: uuid.UUID = None, api_key: uuid.UUID= API_KEY, method: str = 'auth.getToken') -> str:
        '''Fetch an unathorized request token for an API account.'''
        api_sig = cls.calculate_api_sig(dict(method=method, api_key=api_key))
        response = Request.get(**dict(method=method, api_key=api_key, api_sig=api_sig))
        return response.token

    @classmethod
    def main(cls):
        '''[Authentication: Desktop Application How-To](https://www.last.fm/api/desktopauth)'''
        token = cls.getToken()
        confirm = input(f'\nPlease authorize application access from browser:\nhttp://www.last.fm/api/auth/?api_key={API_KEY}&token={token}\nand press `y` to confirm: ')
        if not confirm.lower() in ('y', 'yes', 'yep'):
            return
        sk = cls.getSession(token=token)
        if sk:
            log.log.warning(f'Session key: {sk}\n(store it securely and set as `LASTFM_SESSION_KEY` environment variable)')

    @staticmethod
    def user(user: str = None, required: bool = True) -> str:
        if required:
            validate(check=(user or Auth.session_key), message=Message.USER.value)
        if (not user and Auth.session_key):
            return Auth.session_key

class album:

    def addTags(artist: str, album: str, tags: list[str], api_sig: uuid.UUID = None, sk: str = Auth.session_key, api_key: uuid.UUID = API_KEY, method: str = 'album.addTags') -> RESPONSE_TYPE:
        '''Tag an album using a list of user supplied tags.'''
        validate(check=sk, message=Message.SK.value)
        api_sig = Auth.calculate_api_sig(locals())
        return Request.get(**locals())

    def getInfo(artist: str = None, album: str = None, mbid: uuid.UUID = None, user: str = None, autocorrect: bool = None, lang: str = None, api_key: uuid.UUID = API_KEY, method: str = 'album.getInfo') -> RESPONSE_TYPE:
        '''Get the metadata and tracklist for an album on Last.fm using the album name or a musicbrainz id.'''
        validate(check=((artist and album) or mbid), message=Message.ALBUM.value)
        if (not user and Auth.session_key):
            logging.warning('`userplaycount` is not included for authenticated requests (providing `sk` and `api_sig`)! `user` must be provided explicitly instead.')
        if autocorrect:
            logging.warning('Note that `autocorrect` only affects `artist`, not `album`.')
        return Request.get(**locals())

    def getTags(artist: str = None, album: str = None, mbid: uuid.UUID = None, user: str = None, autocorrect: bool = None, api_key: uuid.UUID = API_KEY, method: str = 'album.getTags') -> RESPONSE_TYPE:
        '''Get the tags applied by an individual user to an album on Last.fm.'''
        validate(check=((artist and album) or mbid), message=Message.ALBUM.value)
        if autocorrect:
            logging.warning('Note that `autocorrect` only affects `artist`, not `album`.')
        sk = Auth.user(user=user, required=True)
        return Request.get(**locals())

    def getTopTags(artist: str = None, album: str = None, mbid: uuid.UUID = None, autocorrect: bool = None, api_key: uuid.UUID = API_KEY, method: str = 'album.getTopTags') -> RESPONSE_TYPE:
        '''Get the top tags for an album on Last.fm, ordered by popularity.'''
        validate(check=((artist and album) or mbid), message=Message.ALBUM.value)
        if autocorrect:
            logging.warning('Note that `autocorrect` only affects `artist`, not `album`.')
        return Request.get(**locals())

    def removeTag(artist: str, album: str, tag: str, api_sig: uuid.UUID = None, sk: str = Auth.session_key, api_key: uuid.UUID = API_KEY, method: str = 'album.removeTag') -> RESPONSE_TYPE:
        '''Remove a user's tag from an album.'''
        validate(check=sk, message=Message.SK.value)
        api_sig = Auth.calculate_api_sig(locals())
        return Request.get(**locals())

    def search(album: str, limit: int = 50, page: int = 1, api_key: uuid.UUID = API_KEY, method: str = 'album.search') -> RESPONSE_TYPE:
        '''Search for an album by name. Returns album matches sorted by relevance.'''
        return Request.get(**locals())


class artist:

    def addTags(artist: str, tags: list[str], api_sig: uuid.UUID = None, sk: str = Auth.session_key, api_key: uuid.UUID = API_KEY, method: str = 'artist.addTags') -> RESPONSE_TYPE:
        '''Tag an artist with one or more user supplied tags.'''
        validate(check=sk, message=Message.SK.value)
        api_sig = Auth.calculate_api_sig(locals())
        return Request.get(**locals())

    def getCorrection(artist: str, api_key: uuid.UUID = API_KEY, method: str = 'artist.getCorrection') -> RESPONSE_TYPE:
        '''Use the last.fm corrections data to check whether the supplied artist has a correction to a canonical artist.'''
        return Request.get(**locals())

    def getInfo(artist: str = None, mbid: uuid.UUID = None, user: str = None, autocorrect: bool = None, lang: str = None, api_key: uuid.UUID = API_KEY, method: str = 'artist.getInfo') -> RESPONSE_TYPE:
        '''Get the metadata for an artist. Includes biography, truncated at 300 characters.'''
        validate(check=(artist or mbid), message=Message.ARTIST.value)
        sk = Auth.user(user=user, required=False)
        return Request.get(**locals())

    def getSimilar(artist: str = None, mbid: uuid.UUID = None, autocorrect: bool = None, limit: int = 100, api_key: uuid.UUID = API_KEY, method: str = 'artist.getSimilar') -> RESPONSE_TYPE:
        '''Get all the artists similar to this artist.'''
        validate(check=(artist or mbid), message=Message.ARTIST.value)
        return Request.get(**locals())

    def getTags(artist: str = None, mbid: uuid.UUID = None, user: str = None, autocorrect: bool = None, api_key: uuid.UUID = API_KEY, method: str = 'artist.getTags') -> RESPONSE_TYPE:
        '''Get the tags applied by an individual user to an artist on Last.fm.'''
        validate(check=(artist or mbid), message=Message.ARTIST.value)
        sk = Auth.user(user=user, required=True)
        return Request.get(**locals())

    def getTopAlbums(artist: str = None, mbid: uuid.UUID = None, autocorrect: bool = None, limit: int = 50, page: int = 1, api_key: uuid.UUID = API_KEY, method: str = 'artist.getTopAlbums') -> RESPONSE_TYPE:
        '''Get the top albums for an artist on Last.fm, ordered by popularity.'''
        validate(check=(artist or mbid), message=Message.ARTIST.value)
        return Request.get(**locals())

    def getTopTags(artist: str = None, mbid: uuid.UUID = None, autocorrect: bool = None, api_key: uuid.UUID = API_KEY, method: str = 'artist.getTopTags') -> RESPONSE_TYPE:
        '''Get the top tags for an artist on Last.fm, ordered by popularity.'''
        validate(check=(artist or mbid), message=Message.ARTIST.value)
        return Request.get(**locals())

    def getTopTracks(artist: str = None, mbid: uuid.UUID = None, autocorrect: bool = None, limit: int = 50, page: int = 1, api_key: uuid.UUID = API_KEY, method: str = 'artist.getTopTracks') -> RESPONSE_TYPE:
        '''Get the top tracks by an artist on Last.fm, ordered by popularity.'''
        validate(check=(artist or mbid), message=Message.ARTIST.value)
        return Request.get(**locals())

    def removeTag(artist: str, tag: str, api_sig: typ.UUID = None, sk: str = Auth.session_key, api_key: uuid.UUID = API_KEY, method: str = 'artist.removeTag') -> RESPONSE_TYPE:
        '''Remove a user's tag from an artist.'''
        validate(check=sk, message=Message.SK.value)
        api_sig = Auth.calculate_api_sig(locals())
        return Request.get(**locals())

    def search(artist: str, limit: int = 30, page: int = 1, api_key: uuid.UUID = API_KEY, method: str = 'artist.search') -> RESPONSE_TYPE:
        '''Search for an artist by name. Returns artist matches sorted by relevance.'''
        return Request.get(**locals())


class chart:

    def getTopArtists(limit: int = 50, page: int = 1, api_key: uuid.UUID = API_KEY, method: str = 'chart.getTopArtists') -> RESPONSE_TYPE:
        '''Get the top artists chart.'''
        return Request.get(**locals())

    def getTopTags(limit: int = 50, page: int = 1, api_key: uuid.UUID = API_KEY, method: str = 'chart.getTopTags') -> RESPONSE_TYPE:
        '''Get the top artists chart.'''
        return Request.get(**locals())

    def getTopTracks(limit: int = 50, page: int = 1, api_key: uuid.UUID = API_KEY, method: str = 'chart.getTopTracks') -> RESPONSE_TYPE:
        '''Get the top tracks chart.'''
        return Request.get(**locals())


class geo:

    @staticmethod
    def isocodes(data: str) -> list[str]:
        '''[isocodes: A python library that provides you access to lists of various ISO standards](https://www.reddit.com/rf20kg/)'''
        file, field = dict(countries=(pathlib.Path('iso_3166-1.json'), 'name'), languages=(pathlib.Path('iso_639-2.json'), 'alpha_2'))[data]
        key = file.stem.split('_')[-1]
        if file.exists():
            return sorted(set(_[field].lower() for _ in json.load(file.open(mode='r'))[key] if _.get(field)))
        url = f'https://github.com/Atem18/isocodes/raw/main/isocodes/share/iso-codes/json/{file}'
        logging.debug(f'downloading {url}')
        response = urllib.request.urlopen(url).read().decode('utf-8')
        file.write_text(response)
        return sorted(set(_[field].lower() for _ in json.loads(response)[key] if _.get(field)))

    @classmethod
    def countries(cls) -> list[str]:
        '''Return list of ISO 3166-1 country names.'''
        return cls.isocodes('countries')

    @classmethod
    def languages(cls) -> list[str]:
        '''Return list of ISO 639-1 2-letter language codes.'''
        return cls.isocodes('languages')

    def getTopArtists(country: str, limit: int = 50, page: int = 1, api_key: uuid.UUID = API_KEY, method: str = 'geo.getTopArtists') -> RESPONSE_TYPE:
        '''Get the most popular artists on Last.fm by country.'''
        return Request.get(**locals())

    def getTopTracks(country: str, location: str = None, limit: int = 50, page: int = 1, api_key: uuid.UUID = API_KEY, method: str = 'geo.getTopTracks') -> RESPONSE_TYPE:
        '''Get the most popular tracks on Last.fm last week by country.'''
        return Request.get(**locals())


class library:

    def getArtists(user: str = None, limit: int = 50, page: int = 1, api_key: uuid.UUID = API_KEY, method: str = 'library.getArtists') -> RESPONSE_TYPE:
        '''A paginated list of all the artists in a user's library, with play counts and tag counts.'''
        validate(check=(user or Auth.session_key), message=Message.USER.value)
        sk = Auth.user(user=user, required=True)
        return Request.get(**locals())


class tag:

    def getInfo(tag: str, lang: str = None, api_key: uuid.UUID = API_KEY, method: str = 'tag.getInfo') -> RESPONSE_TYPE:
        '''Get the metadata for a tag.'''
        return Request.get(**locals())

    def getSimilar(tag: str, api_key: uuid.UUID = API_KEY, method: str = 'tag.getSimilar') -> RESPONSE_TYPE:
        '''Search for tags similar to this one. Returns tags ranked by similarity, based on listening data.'''
        logging.warning('The `tag.getSimilar` API endpoint currently broken and returns an empty array as a response.')
        return Request.get(**locals())

    def getTopAlbums(tag: str, limit: int = 50, page: int = 1, api_key: uuid.UUID = API_KEY, method: str = 'tag.getTopAlbums') -> RESPONSE_TYPE:
        '''Get the top albums tagged by this tag, ordered by tag count.'''
        return Request.get(**locals())

    def getTopArtists(tag: str, limit: int = 50, page: int = 1, api_key: uuid.UUID = API_KEY, method: str = 'tag.getTopArtists') -> RESPONSE_TYPE:
        '''Get the top artists tagged by this tag, ordered by tag count.'''
        return Request.get(**locals())

    def getTopTags(api_key: uuid.UUID = API_KEY, method: str = 'tag.getTopTags') -> RESPONSE_TYPE:
        '''Fetches the top global tags on Last.fm, sorted by popularity (number of times used).'''
        return Request.get(**locals())

    def getTopTracks(tag: str, limit: int = 50, page: int = 1, api_key: uuid.UUID = API_KEY, method: str = 'tag.getTopTracks') -> RESPONSE_TYPE:
        '''Get the top tracks tagged by this tag, ordered by tag count.'''
        return Request.get(**locals())

    def getWeeklyChartList(tag: str, api_key: uuid.UUID = API_KEY, method: str = 'tag.getWeeklyChartList') -> RESPONSE_TYPE:
        '''Get a list of available charts for this tag, expressed as date ranges which can be sent to the chart services.'''
        return Request.get(**locals())


class track:

    def addTags(artist: str, track: str, tags: list[str], api_sig: uuid.UUID = None, sk: str = Auth.session_key, api_key: uuid.UUID = API_KEY, method: str = 'track.addTags') -> RESPONSE_TYPE:
        '''Tag an album using a list of user supplied tags.'''
        validate(check=sk, message=Message.SK.value)
        api_sig = Auth.calculate_api_sig(locals())
        return Request.get(**locals())

    def getCorrection(artist: str, track: str, api_key: uuid.UUID = API_KEY, method: str = 'track.getCorrection') -> RESPONSE_TYPE:
        '''Use the last.fm corrections data to check whether the supplied track has a correction to a canonical track.'''
        return Request.get(**locals())

    def getInfo(artist: str = None, track: str = None, mbid: uuid.UUID = None, user: str = None, autocorrect: bool = None, lang: str = None, api_key: uuid.UUID = API_KEY, method: str = 'track.getInfo') -> RESPONSE_TYPE:
        '''Get the metadata for a track on Last.fm using the artist/track name or a musicbrainz id.'''
        validate(check=((artist and track) or mbid), message=Message.TRACK.value)
        sk = Auth.user(user=user, required=False)
        return Request.get(**locals())

    def getSimilar(artist: str = None, track: str = None, mbid: uuid.UUID = None, autocorrect: bool = None, limit: int = 100, api_key: uuid.UUID = API_KEY, method: str = 'track.getSimilar') -> RESPONSE_TYPE:
        '''Get the similar tracks for this track on Last.fm, based on listening data.'''
        validate(check=((artist and track) or mbid), message=Message.TRACK.value)
        return Request.get(**locals())

    def getTags(artist: str = None, track: str = None, mbid: uuid.UUID = None, user: str = None, autocorrect: bool = None, api_key: uuid.UUID = API_KEY, method: str = 'track.getTags') -> RESPONSE_TYPE:
        '''Get the tags applied by an individual user to a track on Last.fm.'''
        validate(check=((artist and track) or mbid), message=Message.TRACK.value)
        sk = Auth.user(user=user, required=True)
        return Request.get(**locals())

    def getTopTags(artist: str = None, track: str = None, mbid: uuid.UUID = None, autocorrect: bool = None, api_key: uuid.UUID = API_KEY, method: str = 'track.getTopTags') -> RESPONSE_TYPE:
        '''Get the top tags for this track on Last.fm, ordered by tag count. Supply either track & artist name or mbid.'''
        validate(check=((artist and track) or mbid), message=Message.TRACK.value)
        return Request.get(**locals())

    def love(artist: str, track: str, api_sig: typ.UUID = None, sk: str = Auth.session_key, api_key: uuid.UUID = API_KEY, method: str = 'track.love') -> RESPONSE_TYPE:
        '''Love a track for a user profile.'''
        validate(check=sk, message=Message.SK.value)
        api_sig = Auth.calculate_api_sig(locals())
        return Request.post(**locals())

    def removeTag(artist: str, track: str, tag: str, api_sig: uuid.UUID = None, sk: str = Auth.session_key, api_key: uuid.UUID = API_KEY, method: str = 'track.removeTag') -> RESPONSE_TYPE:
        '''Remove a user's tag from a track.'''
        validate(check=sk, message=Message.SK.value)
        api_sig = Auth.calculate_api_sig(locals())
        return Request.get(**locals())

    def scrobble(artist: list[str], track: list[str], timestamp: list[int], album: list[str] = (), mbid: list[uuid.UUID] = (), albumArtist: list[str] = (), trackNumber: list[int] = (), duration: list[int] = (), context: list[str] = (), streamId: list[str] = (), chosenByUser: list[bool] = (), api_sig: typ.UUID = None, sk: str = Auth.session_key, api_key: uuid.UUID = API_KEY, method: str = 'track.scrobble') -> RESPONSE_TYPE:
        '''Used to add a track-play to a user's profile.'''
        validate(check=sk, message=Message.SK.value)
        kwargs = locals()
        array_fields = ('artist', 'track', 'timestamp', 'album', 'mbid', 'trackNumber', 'albumArtist', 'duration', 'context', 'streamId', 'chosenByUser')
        validate(check=all((len(kwargs[array_field]) <= 50) for array_field in array_fields), message='a maximium of 50 tracks can be scrobbled in one submission')
        fields = dict(sorted({f'{array_field}[{idx}]': val for array_field in array_fields for idx, val in enumerate(kwargs.pop(array_field)) if (val is not None)}.items()))
        kwargs.update(fields)
        kwargs.update(dict(api_sig=Auth.calculate_api_sig(kwargs)))
        return Request.post(**kwargs)

    def search(track: str, artist: str = None, limit: int = 30, page: int = 1, api_key: uuid.UUID = API_KEY, method: str = 'track.search') -> RESPONSE_TYPE:
        '''Search for a track by track name. Returns track matches sorted by relevance.'''
        return Request.get(**locals())

    def unlove(artist: str, track: str, api_sig: typ.UUID = None, sk: str = Auth.session_key, api_key: uuid.UUID = API_KEY, method: str = 'track.unlove') -> RESPONSE_TYPE:
        '''Unlove a track for a user profile.'''
        validate(check=sk, message=Message.SK.value)
        api_sig = Auth.calculate_api_sig(locals())
        return Request.post(**locals())

    def updateNowPlaying(artist: str, track: str, album: str = None, mbid: typ.UUID = None, albumArtist: str = None, trackNumber: int = None, duration: int = None, context: str = None, api_sig: typ.UUID = None, sk: str = Auth.session_key, api_key: uuid.UUID = API_KEY, method: str = 'track.updateNowPlaying') -> RESPONSE_TYPE:
        '''Used to notify Last.fm that a user has started listening to a track.'''
        validate(check=sk, message=Message.SK.value)
        api_sig = Auth.calculate_api_sig(locals())
        logging.debug(api_sig)
        return Request.post(**locals())


class user:

    def getFriends(user: str = None, recenttracks: bool = False, limit: int = 50, page: int = 1, api_key: uuid.UUID = API_KEY, method: str = 'user.getFriends') -> RESPONSE_TYPE:
        '''Get a list of the user's friends on Last.fm.'''
        sk = Auth.user(user=user, required=True)
        return Request.get(**locals())

    def getInfo(user: str = None, api_key: uuid.UUID = API_KEY, method: str = 'user.getInfo') -> RESPONSE_TYPE:
        '''Get information about a user profile.'''
        sk = Auth.user(user=user, required=True)
        return Request.get(**locals())

    def getLovedTracks(user: str = None, limit: int = 50, page: int = 1, api_key: uuid.UUID = API_KEY, method: str = 'user.getLovedTracks') -> RESPONSE_TYPE:
        '''Get the last 50 tracks loved by a user.'''
        sk = Auth.user(user=user, required=True)
        return Request.get(**locals())

    def getPersonalTags(tag: str, taggingtype: TaggingType, user: str = None, limit: int = 50, page: int = 1, api_key: uuid.UUID = API_KEY, method: str = 'user.getPersonalTags') -> RESPONSE_TYPE:
        '''Get the user's personal tags.'''
        sk = Auth.user(user=user, required=True)
        return Request.get(**locals())

    def getRecentTracks(user: str = None, FROM: int = None, TO: int = None, extended: bool = None, limit: int = 50, page: int = 1, api_key: uuid.UUID = API_KEY, method: str = 'user.getRecentTracks') -> RESPONSE_TYPE:
        '''Get a list of the recent tracks listened to by this user. Also includes the currently playing track with the nowplaying="true" attribute if the user is currently listening. Artist mbid is missing with the `extended` argument.'''
        sk = Auth.user(user=user, required=True)
        return Request.get(**locals())

    def getTopAlbums(user: str = None, period: Period = None, limit: int = 50, page: int = 1, api_key: uuid.UUID = API_KEY, method: str = 'user.getTopAlbums') -> RESPONSE_TYPE:
        '''Get the top albums listened to by a user.'''
        sk = Auth.user(user=user, required=True)
        return Request.get(**locals())

    def getTopArtists(user: str = None, period: Period = None, limit: int = 50, page: int = 1, api_key: uuid.UUID = API_KEY, method: str = 'user.getTopArtists') -> RESPONSE_TYPE:
        '''Get the top artists listened to by a user.'''
        sk = Auth.user(user=user, required=True)
        return Request.get(**locals())

    def getTopTags(user: str = None, limit: int = 50, api_key: uuid.UUID = API_KEY, method: str = 'user.getTopTags') -> RESPONSE_TYPE:
        '''Get the top tags used by this user.'''
        sk = Auth.user(user=user, required=True)
        return Request.get(**locals())

    def getTopTracks(user: str = None, period: Period = None, limit: int = 50, page: int = 1, api_key: uuid.UUID = API_KEY, method: str = 'user.getTopTracks') -> RESPONSE_TYPE:
        '''Get the top tracks listened to by a user.'''
        sk = Auth.user(user=user, required=True)
        return Request.get(**locals())

    def getWeeklyAlbumChart(user: str = None, FROM: int = None, TO: int = None, api_key: uuid.UUID = API_KEY, method: str = 'user.getWeeklyAlbumChart') -> RESPONSE_TYPE:
        '''Get an album chart for a user profile for a given date range.'''
        sk = Auth.user(user=user, required=True)
        return Request.get(**locals())

    def getWeeklyArtistChart(user: str = None, FROM: int = None, TO: int = None, api_key: uuid.UUID = API_KEY, method: str = 'user.getWeeklyArtistChart') -> RESPONSE_TYPE:
        '''Get an artist chart for a user profile for a given date range.'''
        sk = Auth.user(user=user, required=True)
        return Request.get(**locals())

    def getWeeklyChartList(user: str = None, api_key: uuid.UUID = API_KEY, method: str = 'user.getWeeklyChartList') -> RESPONSE_TYPE:
        '''Get a list of available charts for this user expressed as date ranges which can be sent to the chart services.'''
        sk = Auth.user(user=user, required=True)
        return Request.get(**locals())

    def getWeeklyTrackChart(user: str = None, FROM: int = None, TO: int = None, api_key: uuid.UUID = API_KEY, method: str = 'user.getWeeklyTrackChart') -> RESPONSE_TYPE:
        '''Get a track chart for a user profile for a given date range.'''
        sk = Auth.user(user=user, required=True)
        return Request.get(**locals())

    def getTrackScrobbles(artist: str, track: str, user: str = None, FROM: int = None, TO: int = None, limit: int = 50, page: int = 1, api_key: uuid.UUID = API_KEY, method: str = 'user.getTrackScrobbles') -> RESPONSE_TYPE:
        '''[... there is a new method user.getTrackScrobbles which is just like user.getArtistTracks, except also takes a "track" parameter.](https://github.com/pylast/pylast/issues/298)'''
        sk = Auth.user(user=user, required=True)
        return Request.get(**locals())
