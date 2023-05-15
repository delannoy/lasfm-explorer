#!/usr/bin/env python3

import pydantic

import param
import request
import typ

@param.required
@pydantic.validate_arguments
def getInfo(method: str, api_key: typ.UUID, tag: str, lang: str = 'eng') -> typ.response:
    '''Get the metadata for a tag
        tag     : Required : The tag name
        lang    : Optional : The language to return the wiki in, expressed as an ISO 639 alpha-2 code.
        api_key : Required : A Last.fm API key.
    '''
    return request.get(url=param.url, headers=param.headers, params=param.params(locals()))

@param.required
@pydantic.validate_arguments
def getSimilar(method: str, api_key: typ.UUID, tag: str) -> typ.response:
    '''Search for tags similar to this one. Returns tags ranked by similarity, based on listening data.
        tag     : Required : The tag name
        api_key : Required : A Last.fm API key.
    '''
    return request.get(url=param.url, headers=param.headers, params=param.params(locals()))

@param.required
@pydantic.validate_arguments
def getTopAlbums(method: str, api_key: typ.UUID, tag: str, limit: int = 50, page: int = 1) -> typ.response:
    '''Get the top albums tagged by this tag, ordered by tag count.
        tag     : Required : The tag name
        limit   : Optional : The number of results to fetch per page. Defaults to 50.
        page    : Optional : The page number to fetch. Defaults to first page.
        api_key : Required : A Last.fm API key.
    '''
    return request.get(url=param.url, headers=param.headers, params=param.params(locals()))

@param.required
@pydantic.validate_arguments
def getTopArtists(method: str, api_key: typ.UUID, tag: str, limit: int = 50, page: int = 1) -> typ.response:
    '''Get the top artists tagged by this tag, ordered by tag count.
        tag     : Required : The tag name
        limit   : Optional : The number of results to fetch per page. Defaults to 50.
        page    : Optional : The page number to fetch. Defaults to first page.
        api_key : Required : A Last.fm API key.
    '''
    return request.get(url=param.url, headers=param.headers, params=param.params(locals()))

@param.required
@pydantic.validate_arguments
def getTopTags(method: str, api_key: typ.UUID) -> typ.response:
    '''Fetches the top global tags on Last.fm, sorted by popularity (number of times used)
        api_key : Required : A Last.fm API key.
    '''
    return request.get(url=param.url, headers=param.headers, params=param.params(locals()))

@param.required
@pydantic.validate_arguments
def getTopTracks(method: str, api_key: typ.UUID, tag: str, limit: int = 50, page: int = 1) -> typ.response:
    '''Get the top tracks tagged by this tag, ordered by tag count.
        tag     : Required : The tag name
        limit   : Optional : The number of results to fetch per page. Defaults to 50.
        page    : Optional : The page number to fetch. Defaults to first page.
        api_key : Required : A Last.fm API key.
    '''
    return request.get(url=param.url, headers=param.headers, params=param.params(locals()))

@param.required
@pydantic.validate_arguments
def getWeeklyChartList(method: str, api_key: typ.UUID, tag: str) -> typ.response:
    '''Get a list of available charts for this tag, expressed as date ranges which can be sent to the chart services.
        tag     : Required : The tag name
        api_key : Required : A Last.fm API key.
    '''
    return request.get(url=param.url, headers=param.headers, params=param.params(locals()))
