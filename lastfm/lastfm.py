#!/usr/bin/env python3

from __future__ import annotations
import dataclasses
import datetime
import enum
import hashlib
import html.parser
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
import typing_extensions

import models

try:
    API_KEY = uuid.UUID(os.environ['LASTFM_KEY']).hex # [Create API account](https://www.last.fm/api/account/create) [API Applications(https://www.last.fm/api/accounts)
except KeyError as error:
    logging.error('Please define your last.fm api_key as an environment variable:\nexport LASTFM_KEY=your_lastfm_api_key')
    raise SystemExit

logging.basicConfig(level=logging.DEBUG, format='%(message)s', handlers=[rich.logging.RichHandler(rich_tracebacks=True, log_time_format='[%Y-%m-%d %H:%M:%S]')])

HEADERS = {'User-Agent': 'delannoy/0.2 (a@delannoy.cc)'}
FORMAT = 'json'
VALIDATE_RESPONSE = True if (FORMAT == 'json') else False


class MethodParser(html.parser.HTMLParser):
    '''[How can I use the python HTMLParser library to extract data from a specific div tag?](https://stackoverflow.com/a/3276119)'''
    def __init__(self):
        html.parser.HTMLParser.__init__(self)
        self.section = 0
        self.subsection = False
        self.capture = False
        self.data = tuple()

    def handle_starttag(self, tag: str, attrs: tuple):
        if (tag == 'section') and (dict(attrs).get('class') == 'sidebar-group depth-0'):
            self.section += 1
        if (tag == 'section') and (dict(attrs).get('class') == 'sidebar-group is-sub-group depth-1'):
            self.subsection = True
        if (tag == 'a'):
            self.capture = True

    def handle_endtag(self, tag: str):
        if (tag == 'section'):
            self.subsection = False
        if (tag == 'a'):
            self.capture = False

    def handle_data(self, data: str):
        if (self.section >= 2) and self.subsection and self.capture:
            self.data += (data,)


def methods():
    '''Scrape Last.FM API methods from the documentation website.'''
    response = urllib.request.urlopen('https://www.last.fm/api').read().decode('utf-8')
    method_parser = MethodParser()
    method_parser.feed(response)
    return method_parser.data
    import lxml.html
    etree = etree = lxml.html.fromstring(response)
    return [a.text for a in etree.xpath('//section[@class="sidebar-group depth-0"]')[1].xpath('.//a')]
    return [a.text for a in etree.cssselect('section[class="sidebar-group depth-0"]')[1].cssselect('a')]

def _deprecated_api_methods():
    '''Deprecated methods from the Last.FM API.'''
    api = json.loads(urllib.request.urlopen('https://github.com/jkbrzt/lastfmclient/raw/master/api.json').read().decode('utf-8'))
    return {f"{package}.{method}({', '.join(api[package][method]['params'].keys())})" for package in api for method in api[package] if (not package.startswith('_')) and (not getattr(globals().get(package, None), method, None))}
    {f'{package}.{method}': Request.get(method=f'{package}.{method}', api_key=API_KEY) for package in api for method in api[package] if (not package.startswith('_')) and (not getattr(globals().get(package, None), method, None))}
    [f"{package}.{method}{tuple(api[package][method].get('params', {}).keys())}" for package in api for method in api[package] if (not package.startswith('_')) and (getattr(globals().get(package, None), method, None))]
    sorted(set(kwargs.lower() for method in [api[package][method].get('params', {}).keys() for package in api for method in api[package] if (not package.startswith('_'))] for kwargs in method))


@dataclasses.dataclass
class Validate:
    album: str = '`artist` and `album` must be provided unless `mbid` is specified'
    artist: str = '`artist` must be provided unless `mbid` is specified'
    track: str = '`artist` and `track` must be provided unless `mbid` is specified'
    sk: str = '`session_key` is required; run `Auth.main()` to obtain one and define it as an environment variable:\nexport LASTFM_SESSION_KEY=your_lastfm_session_key'

    @staticmethod
    def kwargs(check: bool, message: str) -> None:
        '''Raise `ValueError` with `message` if `check` is `False`.'''
        if not check:
            raise ValueError(message)

    @classmethod
    def num_results(cls, response: Type.json, limit: int):
        '''Navigate nested keys in `response` until reaching a list of results, and compare its length to `limit`.'''
        entity = list(response.keys() - {'@attr', 'opensearch:startIndex', 'opensearch:totalResults', 'opensearch:itemsPerPage', 'opensearch:Query'})
        if (len(entity) != 1):
            return logging.warning(f'cannot identify unique key containing results: {entity}')
        entity = entity.pop(0)
        if isinstance(response[entity], dict):
            cls.num_results(response=response[entity], limit=limit)
        if isinstance(response[entity], list) and (len(response[entity]) != limit):
            logging.warning(f'a different numnber of results were returned ({len(response[entity])}) than requested ({limit})')

    @classmethod
    def response(cls, response: Type.json, method: str, limit: int = None) -> pydantic.BaseModel:
        '''Determine the top level `entity` in the response and call the corresponding `pydantic` model to validate it.'''
        if (FORMAT != 'json') or (not response):
            return response
        if 'error' in response:
            return models.Error(**response)
        entity = next(iter(response))
        if method not in ('auth.getToken'):
            response = response.pop(entity)
        if limit:
            cls.num_results(response=response, limit=limit)
        model = getattr(getattr(models, method.split('.')[0]), entity.capitalize())
        return model(**response)


class ISOcodes:

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


class StrEnum(str, enum.Enum):

    def __str__(self):
        return self.value

    @classmethod
    def list(cls):
        return sorted(enum.value for enum in cls)


class Type:

    @pydantic.validate_call
    def csv_tags(tags: typing.Iterable[int|str]) -> str:
        return ','.join(str(item).replace(',', '') for item in tags)

    @pydantic.validate_call
    def datetime_to_timestamp(val: int|float|str|datetime.datetime|None) -> int:
        '''Parse `val` into UTC unix timestamp.'''
        if not val:
            return
        if isinstance(val, (int, float)):
            return int(val)
        if isinstance(val, str):
            Validate.kwargs(check=dateparser.parse(val), message=f"Unable to parse '{val}' as a `datetime` object")
            val = dateparser.parse(val) if dateparser.parse(val).tzinfo else dateparser.parse(f'{val} UTC')
        return int(val.timestamp())

    def PosInt(max: int = None) -> typing_extensions._AnnotatedAlias:
        return pydantic.types.conint(ge=1, le=max) if max else pydantic.types.conint(ge=1)

    json = typing.Dict[str, typing.Any]
    response = xml.etree.ElementTree.Element if (FORMAT != 'json') else pydantic.BaseModel if VALIDATE_RESPONSE else json

    api_key = typing_extensions.Annotated[uuid.UUID, pydantic.AfterValidator(lambda val: val.hex if isinstance(val, uuid.UUID) else uuid.UUID(val).hex)]
    datetime = typing_extensions.Annotated[typing.TypeVar('DateTime'), pydantic.AfterValidator(datetime_to_timestamp)]
    tags = typing_extensions.Annotated[typing.TypeVar('Tags'), pydantic.AfterValidator(csv_tags)]

    limit = pydantic.types.conint(ge=1, le=1000)
    page = pydantic.types.conint(ge=1, le=1000000)

    bools = pydantic.types.conlist(item_type=bool, min_length=1, max_length=50)
    datetimes = pydantic.types.conlist(item_type=datetime, min_length=1, max_length=50)
    ints = pydantic.types.conlist(item_type=int, min_length=1, max_length=50)
    strs = pydantic.types.conlist(item_type=str, min_length=1, max_length=50)
    uuids = pydantic.types.conlist(item_type=uuid.UUID, min_length=1, max_length=50)

    country = StrEnum('Country', {_.upper(): _ for _ in ISOcodes.countries()})
    language = StrEnum('Language', {_.upper(): _ for _ in ISOcodes.languages()})
    period = StrEnum('Period', {_.upper(): _ for _ in ('overall', '7day', '1month', '3month', '6month', '12month')})
    taggingtype = StrEnum('TaggingType', {_.upper(): _ for _ in ('artist', 'album', 'track')})

    # methods = {'album': ['addTags', 'getInfo', 'getTags', 'getTopTags', 'removeTag', 'search'],
    #  'artist': ['addTags', 'getCorrection', 'getInfo', 'getSimilar', 'getTags', 'getTopAlbums', 'getTopTags', 'getTopTracks', 'removeTag', 'search'],
    #  'auth': ['getMobileSession', 'getSession', 'getToken'],
    #  'chart': ['getTopArtists', 'getTopTags', 'getTopTracks'],
    #  'geo': ['getTopArtists', 'getTopTracks'],
    #  'library': ['getArtists'],
    #  'tag': ['getInfo', 'getSimilar', 'getTopAlbums', 'getTopArtists', 'getTopTags', 'getTopTracks', 'getWeeklyChartList'],
    #  'track': ['addTags', 'getCorrection', 'getInfo', 'getSimilar', 'getTags', 'getTopTags', 'love', 'removeTag', 'scrobble', 'search', 'unlove', 'updateNowPlaying'],
    #  'user': ['getFriends', 'getInfo', 'getLovedTracks', 'getPersonalTags', 'getRecentTracks', 'getTopAlbums', 'getTopArtists', 'getTopTags', 'getTopTracks', 'getTrackScrobbles', 'getWeeklyAlbumChart', 'getWeeklyArtistChart', 'getWeeklyChartList', 'getWeeklyTrackChart']}
    # method = StrEnum('Method', {f'{package}.{method}'.upper(): f'{package}.{method}' for package, methods in methods.items() for method in methods})
    # method = StrEnum('Method', {_.upper(): _ for _ in methods() + ('user.getTrackScrobbles',)})


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


@dataclasses.dataclass
class Request:
    url: str = 'http://ws.audioscrobbler.com/2.0/'
    sleep: float = 0.2 # [Rate limit copied from pylast since it is not explicitly mentioned in the API Terms of Service](https://github.com/pylast/pylast/blob/master/src/pylast/__init__.py#L119)

    @classmethod
    def request(cls, request_method: str, data: Type.json = None, **kwargs) -> urllib.request.Request:
        '''Instantiate a `urllib.request.Request` of given `request_method` with url parameters given by `kwargs` dictionary.'''
        kwargs = {key.lower(): val for key, val in kwargs.items() if val is not None}
        params = {**kwargs, 'format': FORMAT}
        logging.debug(params)
        url = urllib.parse.urlparse(url=f'{cls.url}?{urllib.parse.urlencode(query=params)}')
        data = urllib.parse.urlencode(data).encode('utf-8') if data else None
        return urllib.request.Request(method=request_method, url=urllib.parse.urlunparse(url), headers=HEADERS, data=data)

    @staticmethod
    def error(response: Type.json):
        logging.error(f"{response['message'] = }")
        if response.get('error') in {e.value for e in Errors}:
            error_enum = Errors(response.get('error'))
            logging.error(f"{error_enum.name}: {error_enum.__doc__}")

    @classmethod
    def urlopen(cls, request: urllib.request.Request) -> Type.json|xml.etree.ElementTree.Element:
        '''Fetch response for `request`.'''
        with urllib.request.urlopen(url=request) as response:
            logging.info(f'HTTP Request: {request.method} | {response.status} | {request.full_url}')
            if FORMAT != 'json':
                return xml.etree.ElementTree.fromstring(response.read())
            response = json.loads(response.read().decode('utf-8'))
        if response.get('error'):
            cls.error(response)
        return response

    @classmethod
    def response(cls, request: urllib.request.Request) -> Type.json|xml.etree.ElementTree.Element:
        '''Fetch response for `request` and handle exceptions.'''
        try:
            return cls.urlopen(request=request)
        except json.JSONDecodeError as error:
            logging.error(f'json.JSONDecodeError: {error}')
        except urllib.error.HTTPError as http_error:
            logging.error(f'{http_error.status} | {http_error.reason} | {http_error.url} | {dict(http_error.headers)}')
            if not ('json' in http_error.headers.get('Content-Type', '')):
                return
            error = json.loads(http_error.read().decode('utf-8'))
            cls.error(error)
            return error

    @classmethod
    def get(cls, format: str = FORMAT, **kwargs) -> Type.response:
        '''Wrapper function for `urllib.request.urlopen` GET requests which accepts URL parameters from `kwargs`.'''
        request = cls.request(request_method='GET', **kwargs)
        response = cls.response(request=request)
        return Validate.response(response=response, method=kwargs.get('method'), limit=kwargs.get('limit')) if VALIDATE_RESPONSE else response

    @classmethod
    def post(cls, data: Type.json = None, **kwargs) -> Type.response:
        '''Wrapper function for `urllib.request.urlopen` POST requests which accepts URL parameters from `kwargs`.'''
        request = cls.request(request_method='POST', data=data, **kwargs)
        response = cls.response(request=request)
        return Validate.response(response=response, method=kwargs.get('method')) if VALIDATE_RESPONSE else response


@dataclasses.dataclass
class Auth:
    password: str = os.getenv('LASTFM_PASSWORD')
    secret: uuid.UUID = os.getenv('LASTFM_SECRET')
    session_key: str = os.getenv('LASTFM_SESSION_KEY')
    username: str = os.getenv('LASTFM_USER')

    @classmethod
    def calculate_api_sig(cls, params: Type.json) -> uuid.UUID:
        '''Calculates `api_sig` (sorts all method call `params`, merges them into a continous string of key & value pairs, and calculates md5).'''
        # [Authentication API](https://www.last.fm/api/authspec)
        # [Signature - Unofficial Last.fm API docs](https://lastfm-docs.github.io/api-docs/auth/signature/)
        # [Last.fm API invalid method signature but valid when getting session key](https://stackoverflow.com/a/45907546/13019084)
        Validate.kwargs(check=cls.secret, message='Please define your last.fm API secret as an environment variables:\nexport LASTFM_SECRET=your_lastfm_secret')
        params = {key: val for key, val in params.items() if val is not None}
        logging.debug(f"{dict(sorted(params.items()))} + '{cls.secret}'")
        sorted_params = [f'{key}{val}' for key, val in sorted(params.items()) if key not in ('api_sig', 'callback', 'format')]
        api_sig = str.join('', sorted_params) + uuid.UUID(cls.secret).hex
        logging.debug(f'{api_sig = }')
        api_sig = hashlib.md5(api_sig.encode('utf-8')).hexdigest()
        return uuid.UUID(api_sig).hex

    @classmethod
    def main(cls):
        '''[Authentication: Desktop Application How-To](https://www.last.fm/api/desktopauth)'''
        token = auth.getToken()
        confirm = input(f'\nPlease authorize application access from browser:\nhttp://www.last.fm/api/auth/?api_key={API_KEY}&token={token}\nand press `y` to confirm: ')
        if not confirm.lower() in ('y', 'yes', 'yep'):
            return
        sk = auth.getSession(token=token)
        if sk:
            log.log.warning(f'Session key: {sk}\n(store it securely and set as `LASTFM_SESSION_KEY` environment variable)')

    @classmethod
    def user(cls, user: str = None, required: bool = True) -> str:
        if required:
            Validate.kwargs(check=(user or cls.session_key), message='`user` is required unless a session key is provided as an environment variable:\nexport LASTFM_SESSION_KEY=your_lastfm_session_key')
        if (not user and cls.session_key):
            return cls.session_key


class album:

    @pydantic.validate_call
    def addTags(artist: str, album: str, tags: Type.tags, api_sig: uuid.UUID = None, sk: str = Auth.session_key, api_key: Type.api_key = API_KEY, method: str = 'album.addTags') -> Type.response:
        '''Tag an album using a list of user supplied tags.'''
        Validate.kwargs(check=sk, message=Validate.sk)
        api_sig = Auth.calculate_api_sig(locals())
        return Request.get(**locals())

    @pydantic.validate_call
    def getInfo(artist: str = None, album: str = None, mbid: uuid.UUID = None, user: str = None, autocorrect: bool = None, lang: Type.language = None, api_key: Type.api_key = API_KEY, method: str = 'album.getInfo') -> Type.response:
        '''Get the metadata and tracklist for an album on Last.fm using the album name or a musicbrainz id.'''
        Validate.kwargs(check=((artist and album) or mbid), message=Validate.album)
        if autocorrect:
            logging.warning('Note that `autocorrect` only affects `artist`, not `album`.')
        sk = Auth.user(user=user, required=True)
        return Request.get(**locals())

    @pydantic.validate_call
    def getTags(artist: str = None, album: str = None, mbid: uuid.UUID = None, user: str = None, autocorrect: bool = None, api_key: Type.api_key = API_KEY, method: str = 'album.getTags') -> Type.response:
        '''Get the tags applied by an individual user to an album on Last.fm.'''
        Validate.kwargs(check=((artist and album) or mbid), message=Validate.album)
        if autocorrect:
            logging.warning('Note that `autocorrect` only affects `artist`, not `album`.')
        sk = Auth.user(user=user, required=True)
        return Request.get(**locals())

    @pydantic.validate_call
    def getTopTags(artist: str = None, album: str = None, mbid: uuid.UUID = None, autocorrect: bool = None, api_key: Type.api_key = API_KEY, method: str = 'album.getTopTags') -> Type.response:
        '''Get the top tags for an album on Last.fm, ordered by popularity.'''
        Validate.kwargs(check=((artist and album) or mbid), message=Validate.album)
        if autocorrect:
            logging.warning('Note that `autocorrect` only affects `artist`, not `album`.')
        return Request.get(**locals())

    @pydantic.validate_call
    def removeTag(artist: str, album: str, tag: str|int, api_sig: uuid.UUID = None, sk: str = Auth.session_key, api_key: Type.api_key = API_KEY, method: str = 'album.removeTag') -> Type.response:
        '''Remove a user's tag from an album.'''
        Validate.kwargs(check=sk, message=Validate.sk)
        api_sig = Auth.calculate_api_sig(locals())
        return Request.get(**locals())

    @pydantic.validate_call
    def search(album: str, limit: Type.PosInt(max=10000) = 50, page: Type.PosInt(max=10000) = 1, api_key: Type.api_key = API_KEY, method: str = 'album.search') -> Type.response:
        '''Search for an album by name. Returns album matches sorted by relevance.'''
        return Request.get(**locals())


class artist:

    @pydantic.validate_call
    def addTags(artist: str, tags: Type.tags, api_sig: uuid.UUID = None, sk: str = Auth.session_key, api_key: Type.api_key = API_KEY, method: str = 'artist.addTags') -> Type.response:
        '''Tag an artist with one or more user supplied tags.'''
        Validate.kwargs(check=sk, message=Validate.sk)
        api_sig = Auth.calculate_api_sig(locals())
        return Request.get(**locals())

    @pydantic.validate_call
    def getCorrection(artist: str, api_key: Type.api_key = API_KEY, method: str = 'artist.getCorrection') -> Type.response:
        '''Use the last.fm corrections data to check whether the supplied artist has a correction to a canonical artist.'''
        return Request.get(**locals())

    @pydantic.validate_call
    def getInfo(artist: str = None, mbid: uuid.UUID = None, user: str = None, autocorrect: bool = None, lang: Type.language = None, api_key: Type.api_key = API_KEY, method: str = 'artist.getInfo') -> Type.response:
        '''Get the metadata for an artist. Includes biography, truncated at 300 characters.'''
        Validate.kwargs(check=(artist or mbid), message=Validate.artist)
        sk = Auth.user(user=user, required=False)
        return Request.get(**locals())

    @pydantic.validate_call
    def getSimilar(artist: str = None, mbid: uuid.UUID = None, autocorrect: bool = None, limit: Type.PosInt(max=250) = 100, api_key: Type.api_key = API_KEY, method: str = 'artist.getSimilar') -> Type.response:
        '''Get all the artists similar to this artist.'''
        Validate.kwargs(check=(artist or mbid), message=Validate.artist)
        return Request.get(**locals())

    @pydantic.validate_call
    def getTags(artist: str = None, mbid: uuid.UUID = None, user: str = None, autocorrect: bool = None, api_key: Type.api_key = API_KEY, method: str = 'artist.getTags') -> Type.response:
        '''Get the tags applied by an individual user to an artist on Last.fm.'''
        Validate.kwargs(check=(artist or mbid), message=Validate.artist)
        sk = Auth.user(user=user, required=True)
        return Request.get(**locals())

    @pydantic.validate_call
    def getTopAlbums(artist: str = None, mbid: uuid.UUID = None, autocorrect: bool = None, limit: Type.PosInt(max=9999) = 50, page: Type.PosInt() = 1, api_key: Type.api_key = API_KEY, method: str = 'artist.getTopAlbums') -> Type.response:
        '''Get the top albums for an artist on Last.fm, ordered by popularity.'''
        Validate.kwargs(check=(artist or mbid), message=Validate.artist)
        return Request.get(**locals())

    @pydantic.validate_call
    def getTopTags(artist: str = None, mbid: uuid.UUID = None, autocorrect: bool = None, api_key: Type.api_key = API_KEY, method: str = 'artist.getTopTags') -> Type.response:
        '''Get the top tags for an artist on Last.fm, ordered by popularity.'''
        Validate.kwargs(check=(artist or mbid), message=Validate.artist)
        return Request.get(**locals())

    @pydantic.validate_call
    def getTopTracks(artist: str = None, mbid: uuid.UUID = None, autocorrect: bool = None, limit: Type.PosInt(max=10000) = 50, page: Type.PosInt() = 1, api_key: Type.api_key = API_KEY, method: str = 'artist.getTopTracks') -> Type.response:
        '''Get the top tracks by an artist on Last.fm, ordered by popularity.'''
        Validate.kwargs(check=(artist or mbid), message=Validate.artist)
        return Request.get(**locals())

    @pydantic.validate_call
    def removeTag(artist: str, tag: str|int, api_sig: uuid.UUID = None, sk: str = Auth.session_key, api_key: Type.api_key = API_KEY, method: str = 'artist.removeTag') -> Type.response:
        '''Remove a user's tag from an artist.'''
        Validate.kwargs(check=sk, message=Validate.sk)
        api_sig = Auth.calculate_api_sig(locals())
        return Request.get(**locals())

    @pydantic.validate_call
    def search(artist: str, limit: Type.PosInt(max=10000) = 30, page: Type.PosInt(max=10000) = 1, api_key: Type.api_key = API_KEY, method: str = 'artist.search') -> Type.response:
        '''Search for an artist by name. Returns artist matches sorted by relevance.'''
        return Request.get(**locals())


class auth:

    @pydantic.validate_call
    def getMobileSession(username: str = Auth.username, password: str = Auth.password, api_sig: uuid.UUID = None, api_key: Type.api_key= API_KEY, method: str = 'auth.getMobileSession') -> Type.response:
        '''Create a web service session for a user.'''
        Validate.kwargs(check=(username and password), message='Please define your last.fm username and password as environment variables:\nexport LASTFM_USER=your_lastfm_username\nexport LASTFM_PASSWORD=your_lastfm_password')
        api_sig = Auth.calculate_api_sig(dict(username=username, password=password, method=method, api_key=api_key))
        return Request.post(**dict(username=username, password=password, method=method, api_key=api_key, api_sig=api_sig))

    @pydantic.validate_call
    def getSession(token: str, api_sig: uuid.UUID = None, api_key: Type.api_key= API_KEY, method: str = 'auth.getSession') -> Type.response:
        '''Fetch a session key for a user.'''
        api_sig = Auth.calculate_api_sig(dict(token=token, method=method, api_key=api_key))
        return Request.get(**dict(token=token, method=method, api_key=api_key, api_sig=api_sig))

    @pydantic.validate_call
    def getToken(api_sig: uuid.UUID = None, api_key: Type.api_key= API_KEY, method: str = 'auth.getToken') -> str:
        '''Fetch an unathorized request token for an API account.'''
        api_sig = Auth.calculate_api_sig(dict(method=method, api_key=api_key))
        response = Request.get(**dict(method=method, api_key=api_key, api_sig=api_sig))
        return response.token


class chart:

    @pydantic.validate_call
    def getTopArtists(limit: Type.PosInt(max=249) = 50, page: Type.page = 1, api_key: Type.api_key = API_KEY, method: str = 'chart.getTopArtists') -> Type.response:
        '''Get the top artists chart.'''
        return Request.get(**locals())

    @pydantic.validate_call
    def getTopTags(limit: Type.limit = 50, page: Type.page = 1, api_key: Type.api_key = API_KEY, method: str = 'chart.getTopTags') -> Type.response:
        '''Get the top artists chart.'''
        return Request.get(**locals())

    @pydantic.validate_call
    def getTopTracks(limit: Type.PosInt(max=249) = 50, page: Type.page = 1, api_key: Type.api_key = API_KEY, method: str = 'chart.getTopTracks') -> Type.response:
        '''Get the top tracks chart.'''
        return Request.get(**locals())


class geo:

    @pydantic.validate_call
    def getTopArtists(country: Type.country, limit: Type.limit = 50, page: Type.page = 1, api_key: Type.api_key = API_KEY, method: str = 'geo.getTopArtists') -> Type.response:
        '''Get the most popular artists on Last.fm by country.'''
        return Request.get(**locals())

    @pydantic.validate_call
    def getTopTracks(country: Type.country, location: str = None, limit: Type.limit = 50, page: Type.page = 1, api_key: Type.api_key = API_KEY, method: str = 'geo.getTopTracks') -> Type.response:
        '''Get the most popular tracks on Last.fm last week by country.'''
        return Request.get(**locals())


class library:

    @pydantic.validate_call
    def getArtists(user: str = None, limit: Type.PosInt(max=2000) = 50, page: Type.page = 1, api_key: Type.api_key = API_KEY, method: str = 'library.getArtists') -> Type.response:
        '''A paginated list of all the artists in a user's library, with play counts and tag counts.'''
        sk = Auth.user(user=user, required=True)
        return Request.get(**locals())


class tag:

    @pydantic.validate_call
    def getInfo(tag: str, lang: Type.language = None, api_key: Type.api_key = API_KEY, method: str = 'tag.getInfo') -> Type.response:
        '''Get the metadata for a tag.'''
        return Request.get(**locals())

    @pydantic.validate_call
    def getSimilar(tag: str, api_key: Type.api_key = API_KEY, method: str = 'tag.getSimilar') -> Type.response:
        '''Search for tags similar to this one. Returns tags ranked by similarity, based on listening data.'''
        logging.warning('The `tag.getSimilar` API endpoint currently broken and returns an empty array as a response.')
        return Request.get(**locals())

    @pydantic.validate_call
    def getTopAlbums(tag: str, limit: Type.limit = 50, page: Type.page = 1, api_key: Type.api_key = API_KEY, method: str = 'tag.getTopAlbums') -> Type.response:
        '''Get the top albums tagged by this tag, ordered by tag count.'''
        return Request.get(**locals())

    @pydantic.validate_call
    def getTopArtists(tag: str, limit: Type.limit = 50, page: Type.page = 1, api_key: Type.api_key = API_KEY, method: str = 'tag.getTopArtists') -> Type.response:
        '''Get the top artists tagged by this tag, ordered by tag count.'''
        return Request.get(**locals())

    @pydantic.validate_call
    def getTopTags(api_key: Type.api_key = API_KEY, method: str = 'tag.getTopTags') -> Type.response:
        '''Fetches the top global tags on Last.fm, sorted by popularity (number of times used).'''
        return Request.get(**locals())

    @pydantic.validate_call
    def getTopTracks(tag: str, limit: Type.limit = 50, page: Type.page = 1, api_key: Type.api_key = API_KEY, method: str = 'tag.getTopTracks') -> Type.response:
        '''Get the top tracks tagged by this tag, ordered by tag count.'''
        return Request.get(**locals())

    @pydantic.validate_call
    def getWeeklyChartList(tag: str, api_key: Type.api_key = API_KEY, method: str = 'tag.getWeeklyChartList') -> Type.response:
        '''Get a list of available charts for this tag, expressed as date ranges which can be sent to the chart services.'''
        return Request.get(**locals())


class track:

    @pydantic.validate_call
    def addTags(artist: str, track: str, tags: Type.tags, api_sig: uuid.UUID = None, sk: str = Auth.session_key, api_key: Type.api_key = API_KEY, method: str = 'track.addTags') -> Type.response:
        '''Tag an album using a list of user supplied tags.'''
        Validate.kwargs(check=sk, message=Validate.sk)
        api_sig = Auth.calculate_api_sig(locals())
        return Request.get(**locals())

    @pydantic.validate_call
    def getCorrection(artist: str, track: str, api_key: Type.api_key = API_KEY, method: str = 'track.getCorrection') -> Type.response:
        '''Use the last.fm corrections data to check whether the supplied track has a correction to a canonical track.'''
        return Request.get(**locals())

    @pydantic.validate_call
    def getInfo(artist: str = None, track: str = None, mbid: uuid.UUID = None, user: str = None, autocorrect: bool = None, lang: Type.language = None, api_key: Type.api_key = API_KEY, method: str = 'track.getInfo') -> Type.response:
        '''Get the metadata for a track on Last.fm using the artist/track name or a musicbrainz id.'''
        Validate.kwargs(check=((artist and track) or mbid), message=Validate.track)
        sk = Auth.user(user=user, required=False)
        return Request.get(**locals())

    @pydantic.validate_call
    def getSimilar(artist: str = None, track: str = None, mbid: uuid.UUID = None, autocorrect: bool = None, limit: Type.PosInt(max=10000) = 100, api_key: Type.api_key = API_KEY, method: str = 'track.getSimilar') -> Type.response:
        '''Get the similar tracks for this track on Last.fm, based on listening data.'''
        Validate.kwargs(check=((artist and track) or mbid), message=Validate.track)
        return Request.get(**locals())

    @pydantic.validate_call
    def getTags(artist: str = None, track: str = None, mbid: uuid.UUID = None, user: str = None, autocorrect: bool = None, api_key: Type.api_key = API_KEY, method: str = 'track.getTags') -> Type.response:
        '''Get the tags applied by an individual user to a track on Last.fm.'''
        Validate.kwargs(check=((artist and track) or mbid), message=Validate.track)
        sk = Auth.user(user=user, required=True)
        return Request.get(**locals())

    @pydantic.validate_call
    def getTopTags(artist: str = None, track: str = None, mbid: uuid.UUID = None, autocorrect: bool = None, api_key: Type.api_key = API_KEY, method: str = 'track.getTopTags') -> Type.response:
        '''Get the top tags for this track on Last.fm, ordered by tag count. Supply either track & artist name or mbid.'''
        Validate.kwargs(check=((artist and track) or mbid), message=Validate.track)
        return Request.get(**locals())

    @pydantic.validate_call
    def love(artist: str, track: str, api_sig: uuid.UUID = None, sk: str = Auth.session_key, api_key: Type.api_key = API_KEY, method: str = 'track.love') -> Type.response:
        '''Love a track for a user profile.'''
        Validate.kwargs(check=sk, message=Validate.sk)
        api_sig = Auth.calculate_api_sig(locals())
        return Request.post(**locals())

    @pydantic.validate_call
    def removeTag(artist: str, track: str, tag: str|int, api_sig: uuid.UUID = None, sk: str = Auth.session_key, api_key: Type.api_key = API_KEY, method: str = 'track.removeTag') -> Type.response:
        '''Remove a user's tag from a track.'''
        Validate.kwargs(check=sk, message=Validate.sk)
        api_sig = Auth.calculate_api_sig(locals())
        return Request.get(**locals())

    @pydantic.validate_call
    def scrobble(artist: Type.strs, track: Type.strs, timestamp: Type.datetimes, album: Type.strs, mbid: Type.uuids = (), albumArtist: Type.strs = (), trackNumber: Type.ints = (), duration: Type.ints = (), context: Type.strs = (), streamId: Type.strs = (), chosenByUser: Type.bools = (), api_sig: uuid.UUID = None, sk: str = Auth.session_key, api_key: Type.api_key = API_KEY, method: str = 'track.scrobble') -> Type.response:
        '''Used to add a track-play to a user's profile.'''
        Validate.kwargs(check=sk, message=Validate.sk)
        kwargs = locals()
        array_fields = ('artist', 'track', 'timestamp', 'album', 'mbid', 'trackNumber', 'albumArtist', 'duration', 'context', 'streamId', 'chosenByUser')
        fields = dict(sorted({f'{array_field}[{idx}]': val for array_field in array_fields for idx, val in enumerate(kwargs.pop(array_field)) if (val is not None)}.items()))
        kwargs.update(fields)
        kwargs.update(dict(api_sig=Auth.calculate_api_sig(kwargs)))
        return Request.post(**kwargs)

    @pydantic.validate_call
    def search(track: str, artist: str = None, limit: Type.PosInt(max=10000) = 30, page: Type.PosInt(max=10000) = 1, api_key: Type.api_key = API_KEY, method: str = 'track.search') -> Type.response:
        '''Search for a track by track name. Returns track matches sorted by relevance.'''
        return Request.get(**locals())

    @pydantic.validate_call
    def unlove(artist: str, track: str, api_sig: uuid.UUID = None, sk: str = Auth.session_key, api_key: Type.api_key = API_KEY, method: str = 'track.unlove') -> Type.response:
        '''Unlove a track for a user profile.'''
        Validate.kwargs(check=sk, message=Validate.sk)
        api_sig = Auth.calculate_api_sig(locals())
        return Request.post(**locals())

    @pydantic.validate_call
    def updateNowPlaying(artist: str, track: str, album: str = None, mbid: uuid.UUID = None, albumArtist: str = None, trackNumber: int = None, duration: int = None, context: str = None, api_sig: uuid.UUID = None, sk: str = Auth.session_key, api_key: Type.api_key = API_KEY, method: str = 'track.updateNowPlaying') -> Type.response:
        '''Used to notify Last.fm that a user has started listening to a track.'''
        Validate.kwargs(check=sk, message=Validate.sk)
        api_sig = Auth.calculate_api_sig(locals())
        logging.debug(api_sig)
        return Request.post(**locals())


class user:

    @pydantic.validate_call
    def getFriends(user: str = None, recenttracks: bool = False, limit: Type.PosInt(max=500) = 50, page: Type.PosInt() = 1, api_key: Type.api_key = API_KEY, method: str = 'user.getFriends') -> Type.response:
        '''Get a list of the user's friends on Last.fm.'''
        sk = Auth.user(user=user, required=True)
        return Request.get(**locals())

    @pydantic.validate_call
    def getInfo(user: str = None, api_key: Type.api_key = API_KEY, method: str = 'user.getInfo') -> Type.response:
        '''Get information about a user profile.'''
        sk = Auth.user(user=user, required=True)
        return Request.get(**locals())

    @pydantic.validate_call
    def getLovedTracks(user: str = None, limit: Type.limit = 50, page: Type.page = 1, api_key: Type.api_key = API_KEY, method: str = 'user.getLovedTracks') -> Type.response:
        '''Get the last 50 tracks loved by a user.'''
        sk = Auth.user(user=user, required=True)
        return Request.get(**locals())

    @pydantic.validate_call
    def getPersonalTags(tag: str, taggingtype: Type.taggingtype, user: str = None, limit: Type.PosInt(max=100000) = 50, page: Type.PosInt(max=10000) = 1, api_key: Type.api_key = API_KEY, method: str = 'user.getPersonalTags') -> Type.response:
        '''Get the user's personal tags.'''
        sk = Auth.user(user=user, required=True)
        return Request.get(**locals())

    @pydantic.validate_call
    def getRecentTracks(user: str = None, FROM: Type.datetime = None, TO: Type.datetime = None, extended: bool = None, limit: Type.limit = 50, page: Type.page = 1, api_key: Type.api_key = API_KEY, method: str = 'user.getRecentTracks') -> Type.response:
        '''Get a list of the recent tracks listened to by this user. Also includes the currently playing track with the nowplaying="true" attribute if the user is currently listening. Artist mbid is missing with the `extended` argument.'''
        sk = Auth.user(user=user, required=True)
        return Request.get(**locals())

    @pydantic.validate_call
    def getTopAlbums(user: str = None, period: Type.period = None, limit: Type.limit = 50, page: Type.page = 1, api_key: Type.api_key = API_KEY, method: str = 'user.getTopAlbums') -> Type.response:
        '''Get the top albums listened to by a user.'''
        sk = Auth.user(user=user, required=True)
        return Request.get(**locals())

    @pydantic.validate_call
    def getTopArtists(user: str = None, period: Type.period = None, limit: Type.limit = 50, page: Type.page = 1, api_key: Type.api_key = API_KEY, method: str = 'user.getTopArtists') -> Type.response:
        '''Get the top artists listened to by a user.'''
        sk = Auth.user(user=user, required=True)
        return Request.get(**locals())

    @pydantic.validate_call
    def getTopTags(user: str = None, limit: Type.PosInt(max=100000) = 50, api_key: Type.api_key = API_KEY, method: str = 'user.getTopTags') -> Type.response:
        '''Get the top tags used by this user.'''
        sk = Auth.user(user=user, required=True)
        return Request.get(**locals())

    @pydantic.validate_call
    def getTopTracks(user: str = None, period: Type.period = None, limit: Type.limit = 50, page: Type.page = 1, api_key: Type.api_key = API_KEY, method: str = 'user.getTopTracks') -> Type.response:
        '''Get the top tracks listened to by a user.'''
        sk = Auth.user(user=user, required=True)
        return Request.get(**locals())

    @pydantic.validate_call
    def getWeeklyAlbumChart(user: str = None, FROM: Type.datetime = None, TO: Type.datetime = None, api_key: Type.api_key = API_KEY, method: str = 'user.getWeeklyAlbumChart') -> Type.response:
        '''Get an album chart for a user profile for a given date range.'''
        sk = Auth.user(user=user, required=True)
        return Request.get(**locals())

    @pydantic.validate_call
    def getWeeklyArtistChart(user: str = None, FROM: Type.datetime = None, TO: Type.datetime = None, api_key: Type.api_key = API_KEY, method: str = 'user.getWeeklyArtistChart') -> Type.response:
        '''Get an artist chart for a user profile for a given date range.'''
        sk = Auth.user(user=user, required=True)
        return Request.get(**locals())

    @pydantic.validate_call
    def getWeeklyChartList(user: str = None, api_key: Type.api_key = API_KEY, method: str = 'user.getWeeklyChartList') -> Type.response:
        '''Get a list of available charts for this user expressed as date ranges which can be sent to the chart services.'''
        sk = Auth.user(user=user, required=True)
        return Request.get(**locals())

    @pydantic.validate_call
    def getWeeklyTrackChart(user: str = None, FROM: Type.datetime = None, TO: Type.datetime = None, api_key: Type.api_key = API_KEY, method: str = 'user.getWeeklyTrackChart') -> Type.response:
        '''Get a track chart for a user profile for a given date range.'''
        sk = Auth.user(user=user, required=True)
        return Request.get(**locals())

    @pydantic.validate_call # (config=pydantic.ConfigDict(validate_default=True))
    def getTrackScrobbles(artist: str, track: str, user: str = None, FROM: Type.datetime = None, TO: Type.datetime = None, limit: Type.limit = 50, page: Type.page = 1, api_key: Type.api_key = API_KEY, method: str = 'user.getTrackScrobbles') -> Type.response:
        '''[... there is a new method user.getTrackScrobbles which is just like user.getArtistTracks, except also takes a "track" parameter.](https://github.com/pylast/pylast/issues/298)'''
        sk = Auth.user(user=user, required=True)
        return Request.get(**locals())
