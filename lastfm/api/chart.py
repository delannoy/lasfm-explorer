#!/usr/bin/env python3

import typ
import auth
import param
import request

@param.method
def getTopArtists(limit: int = 50, page: int = 1, api_key: typ.uuid = auth.api_key, method: str = None) -> typ.response:
    '''Get the top artists chart
        limit   : Optional : The number of results to fetch per page. Defaults to 50.
        page    : Optional : The page number to fetch. Defaults to first page.
        api_key : Required : A Last.fm API key.
    '''
    return request.get(url=param.url, headers=param.headers, params=param.params(locals()))

@param.method
def getTopTags(limit: int = 50, page: int = 1, api_key: typ.uuid = auth.api_key, method: str = None) -> typ.response:
    '''Get the top artists chart
        limit   : Optional : The number of results to fetch per page. Defaults to 50.
        page    : Optional : The page number to fetch. Defaults to first page.
        api_key : Required : A Last.fm API key.
    '''
    return request.get(url=param.url, headers=param.headers, params=param.params(locals()))

@param.method
def getTopTracks(limit: int = 50, page: int = 1, api_key: typ.uuid = auth.api_key, method: str = None) -> typ.response:
    '''Get the top tracks chart
        limit   : Optional : The number of results to fetch per page. Defaults to 50.
        page    : Optional : The page number to fetch. Defaults to first page.
        api_key : Required : A Last.fm API key.
    '''
    return request.get(url=param.url, headers=param.headers, params=param.params(locals()))
