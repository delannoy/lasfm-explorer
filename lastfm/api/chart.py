#!/usr/bin/env python3

import pydantic

import param
import request
import typ

@param.required
@pydantic.validate_arguments
def getTopArtists(method: str, api_key: typ.UUID, limit: int = 50, page: int = 1) -> typ.response:
    '''Get the top artists chart
        limit   : Optional : The number of results to fetch per page. Defaults to 50.
        page    : Optional : The page number to fetch. Defaults to first page.
        api_key : Required : A Last.fm API key.
    '''
    return request.get(url=param.url, headers=param.headers, params=param.params(locals()))

@param.required
@pydantic.validate_arguments
def getTopTags(method: str, api_key: typ.UUID, limit: int = 50, page: int = 1) -> typ.response:
    '''Get the top artists chart
        limit   : Optional : The number of results to fetch per page. Defaults to 50.
        page    : Optional : The page number to fetch. Defaults to first page.
        api_key : Required : A Last.fm API key.
    '''
    return request.get(url=param.url, headers=param.headers, params=param.params(locals()))

@param.required
@pydantic.validate_arguments
def getTopTracks(method: str, api_key: typ.UUID, limit: int = 50, page: int = 1) -> typ.response:
    '''Get the top tracks chart
        limit   : Optional : The number of results to fetch per page. Defaults to 50.
        page    : Optional : The page number to fetch. Defaults to first page.
        api_key : Required : A Last.fm API key.
    '''
    return request.get(url=param.url, headers=param.headers, params=param.params(locals()))
