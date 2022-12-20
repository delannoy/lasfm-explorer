#!/usr/bin/env python3

import pydantic

import param
import request
import secret
import typ

@param.required
@pydantic.validate_arguments # (config={'arbitrary_types_allowed': True})
def getArtists(method: str, api_key: typ.UUID, user: str = secret.user, limit: int = 50, page: int = 1) -> typ.response:
    '''A paginated list of all the artists in a user's library, with play counts and tag counts.
        user    : Required : The user whose library you want to fetch.
        limit   : Optional : The number of results to fetch per page. Defaults to 50.
        page    : Optional : The page number you wish to scan to.
        api_key : Required : A Last.fm API key.
    '''
    return request.get(url=param.url, headers=param.headers, params=param.params(locals()))
