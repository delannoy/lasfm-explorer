#!/usr/bin/env python3

import typ
import auth
import param
import request
import secret

import pydantic

@param.required
@pydantic.validate_arguments
def addTags(method: str, api_key: typ.UUID, artist: str, tags: typ.tags, api_sig: typ.UUID = None, sk: str = secret.sk) -> typ.response:
    '''Tag an artist with one or more user supplied tags.
        artist  : Required : The artist name
        tags    : Required : A comma delimited list of user supplied tags to apply to this artist. Accepts a maximum of 10 tags.
        api_sig : Required : A Last.fm method signature. See authentication for more information.
        sk      : Required : A session key generated by authenticating a user via the authentication protocol.
        api_key : Required : A Last.fm API key.
        '''
    tags = param.listToCSV(tags)
    api_sig = auth.calculate_api_sig(param.params(locals()))
    return request.get(url=param.url, headers=param.headers, params=param.params(locals()))

@param.required
@pydantic.validate_arguments
def getCorrection(method: str, api_key: typ.UUID, artist: str,) -> typ.response:
    '''Use the last.fm corrections data to check whether the supplied artist has a correction to a canonical artist
        artist  : Required : The artist name to correct.
        api_key : Required : A Last.fm API key.
    '''
    return request.get(url=param.url, headers=param.headers, params=param.params(locals()))

@param.required
@pydantic.validate_arguments
def getInfo(method: str, api_key: typ.UUID, artist: str = None, mbid: typ.UUID = None, user: str = secret.user, autocorrect: int = 0, lang: str = 'eng') -> typ.response:
    '''Get the metadata for an artist. Includes biography, truncated at 300 characters.
        artist      : Required [unless mbid] : The artist name
        mbid        : Optional               : The musicbrainz id for the artist
        username    : Optional               : The username for the context of the request. If supplied, the user's playcount for this artist is included in the response.
        autocorrect : Optional               : Transform misspelled artist names into correct artist names, returning the correct version instead. The corrected artist name will be returned in the response. [0|1]
        lang        : Optional               : The language to return the biography in, expressed as an ISO 639 alpha-2 code.
        api_key     : Required               : A Last.fm API key.
    '''
    param.validate(check=(artist or mbid), descr='`artist` must be provided unless `mbid` is specified') # param.mbid(mbid, artist=artist) # assert artist or mbid, '`artist` must be provided unless `mbid` is specified'
    return request.get(url=param.url, headers=param.headers, params=param.params(locals()))

@param.required
@pydantic.validate_arguments
def getSimilar(method: str, api_key: typ.UUID, artist: str = None, mbid: typ.UUID = None, autocorrect: int = 0, limit: int = 100) -> typ.response:
    '''Get all the artists similar to this artist
        artist      : Required [unless mbid] : The artist name
        mbid        : Optional               : The musicbrainz id for the artist
        autocorrect : Optional               : Transform misspelled artist names into correct artist names, returning the correct version instead. The corrected artist name will be returned in the response. [0|1]
        limit       : Optional               : Limit the number of similar artists returned
        api_key     : Required               : A Last.fm API key.
    '''
    param.validate(check=(artist or mbid), descr='`artist` must be provided unless `mbid` is specified')
    return request.get(url=param.url, headers=param.headers, params=param.params(locals()))

@param.required
@pydantic.validate_arguments
def getTags(method: str, api_key: typ.UUID, artist: str = None, mbid: typ.UUID = None, user: str = secret.user, autocorrect: int = 0) -> typ.response:
    '''Get the tags applied by an individual user to an artist on Last.fm. If accessed as an authenticated service /and/ you don't supply a user parameter then this service will return tags for the authenticated user. To retrieve the list of top tags applied to an artist by all users use artist.getTopTags.
        artist      : Required [unless mbid] : The artist name
        mbid        : Optional               : The musicbrainz id for the artist
        user        : Optional               : If called in non-authenticated mode you must specify the user to look up
        autocorrect : Optional               : Transform misspelled artist names into correct artist names, returning the correct version instead. The corrected artist name will be returned in the response. [0|1]
        api_key     : Required               : A Last.fm API key.
    '''
    param.validate(check=(artist or mbid), descr='`artist` must be provided unless `mbid` is specified')
    return request.get(url=param.url, headers=param.headers, params=param.params(locals()))

@param.required
@pydantic.validate_arguments
def getTopAlbums(method: str, api_key: typ.UUID, artist: str = None, mbid: typ.UUID = None, autocorrect: int = 0, limit: int = 50, page: int = 1) -> typ.response:
    '''Get the top albums for an artist on Last.fm, ordered by popularity.
        artist      : Required [unless mbid] : The artist name
        mbid        : Optional               : The musicbrainz id for the artist
        autocorrect : Optional               : Transform misspelled artist names into correct artist names, returning the correct version instead. The corrected artist name will be returned in the response. [0|1]
        limit       : Optional               : The number of results to fetch per page. Defaults to 50.
        page        : Optional               : The page number to fetch. Defaults to first page.
        api_key     : Required               : A Last.fm API key.
    '''
    param.validate(check=(artist or mbid), descr='`artist` must be provided unless `mbid` is specified')
    return request.get(url=param.url, headers=param.headers, params=param.params(locals()))

@param.required
@pydantic.validate_arguments
def getTopTags(method: str, api_key: typ.UUID, artist: str = None, mbid: typ.UUID = None, autocorrect: int = 0) -> typ.response:
    '''Get the top tags for an artist on Last.fm, ordered by popularity.
        artist      : Required [unless mbid] : The artist name
        mbid        : Optional               : The musicbrainz id for the artist
        autocorrect : Optional               : Transform misspelled artist names into correct artist names, returning the correct version instead. The corrected artist name will be returned in the response. [0|1]
        api_key     : Required               : A Last.fm API key.
    '''
    param.validate(check=(artist or mbid), descr='`artist` must be provided unless `mbid` is specified')
    return request.get(url=param.url, headers=param.headers, params=param.params(locals()))

@param.required
@pydantic.validate_arguments
def getTopTracks(method: str, api_key: typ.UUID, artist: str = None, mbid: typ.UUID = None, autocorrect: int = 0, limit: int = 50, page: int = 1) -> typ.response:
    '''Get the top tracks by an artist on Last.fm, ordered by popularity
        artist      : Required [unless mbid] : The artist name
        mbid        : Optional               : The musicbrainz id for the artist
        autocorrect : Optional               : Transform misspelled artist names into correct artist names, returning the correct version instead. The corrected artist name will be returned in the response. [0|1]
        limit       : Optional               : The number of results to fetch per page. Defaults to 50.
        page        : Optional               : The page number to fetch. Defaults to first page.
        api_key     : Required               : A Last.fm API key.
    '''
    param.validate(check=(artist or mbid), descr='`artist` must be provided unless `mbid` is specified')
    return request.get(url=param.url, headers=param.headers, params=param.params(locals()))

@param.required
@pydantic.validate_arguments
def removeTag(method: str, api_key: typ.UUID, artist: str, tag: str, api_sig: typ.UUID = None, sk: str = secret.sk) -> typ.response:
    '''Remove a user's tag from an artist.
        artist  : Required : The artist name
        tag     : Required : A single user tag to remove from this artist.
        api_sig : Required : A Last.fm method signature. See authentication for more information.
        sk      : Required : A session key generated by authenticating a user via the authentication protocol.
        api_key : Required : A Last.fm API key.
    '''
    api_sig = auth.calculate_api_sig(locals())
    return request.get(url=param.url, headers=param.headers, params=param.params(locals()))

@param.required
@pydantic.validate_arguments
def search(method: str, api_key: typ.UUID, artist: str, limit: int = 30, page: int = 1) -> typ.response:
    '''Search for an artist by name. Returns artist matches sorted by relevance.
        artist  : Required : The artist name
        limit   : Optional : The number of results to fetch per page. Defaults to 30.
        page    : Optional : The page number to fetch. Defaults to first page.
        api_key : Required : A Last.fm API key.
    '''
    return request.get(url=param.url, headers=param.headers, params=param.params(locals()))
