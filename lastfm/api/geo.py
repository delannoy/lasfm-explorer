#!/usr/bin/env python3

import pydantic

import param
import request
import typ

@param.required
@pydantic.validate_arguments
def getTopArtists(method: str, api_key: typ.UUID, country: str, limit: int = 50, page: int = 1) -> typ.response:
    '''Get the most popular artists on Last.fm by country
        country : Required : A country name, as defined by the ISO 3166-1 country names standard
        limit   : Optional : The number of results to fetch per page. Defaults to 50.
        page    : Optional : The page number to fetch. Defaults to first page.
        api_key : Required : A Last.fm API key.
    '''
    return request.get(url=param.url, headers=param.headers, params=param.params(locals()))

@param.required
@pydantic.validate_arguments
def getTopTracks(method: str, api_key: typ.UUID, country: str, location: str = None, limit: int = 50, page: int = 1) -> typ.response:
    '''Get the most popular tracks on Last.fm last week by country
        country  : Required : A country name, as defined by the ISO 3166-1 country names standard
        location : Optional : A metro name, to fetch the charts for (must be within the country specified)
        limit    : Optional : The number of results to fetch per page. Defaults to 50.
        page     : Optional : The page number to fetch. Defaults to first page.
        api_key  : Required : A Last.fm API key.
    '''
    return request.get(url=param.url, headers=param.headers, params=param.params(locals()))
