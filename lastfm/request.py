#!/usr/bin/env python3

import json
import urllib.error
import urllib.parse
import urllib.request

# import awkward
import pydantic

import api.errors
import api.models
import log
import typ

def validate(response: typ.json, method: str) -> pydantic.BaseModel:
    '''Determine the top level `entity` in the response and call the corresponding model to validate it.'''
    if len(response) != 1:
        return response
    entity = next(iter(response))
    if method not in ('auth.getToken'):
        response = response.pop(entity)
    module = getattr(api.models, method.split('.')[0])
    model = getattr(module, entity.capitalize())
    return model(**response)

def parseError(error: typ.json) -> None:
    '''Log error information from `api.errors.Errors` corresponding to `error`.'''
    response = json.loads(error)
    if response.get('error') in {e.value for e in api.errors.Errors}:
        error_enum = api.errors.Errors(response.get('error'))
        log.log.error(f'{error_enum.name = }')
        log.log.error(f'{error_enum.__doc__ = }')
    log.log.error(f'{response = }')

def httpError(error: urllib.error.HTTPError) -> None:
    '''Log `urllib.error.HTTPError`. Log corresponding `__doc__` string from `api.errors.Errors` enum.'''
    log.log.debug(f'{error.code = }')
    log.log.debug(f'{error.reason = }')
    log.log.debug(f'{dict(error.headers) = }')
    response = error.read().decode('utf-8')
    if 'json' not in error.headers.get('Content-Type'):
        return log.log.error(f'{response = }')
    return parseError(error=response)

def jsonError(error: json.JSONDecodeError) -> None:
    '''Log `json.JSONDecodeError`.'''
    log.log.debug(f'{error.doc = }')
    log.log.debug(f'{error.msg = }')
    log.log.debug(f'{error.lineno = }')
    log.log.debug(f'{error.colno = }')
    log.log.debug(f'{error.pos = }')
    return log.log.error(f'json.JSONDecodeError: {error}')

def request(url: str, headers: typ.json, params: typ.json) -> urllib.request.Request:
    '''Instantiate a `GET` or `POST` HTTP request depending on `params[method]`.'''
    if params.get('method') in ('auth.getMobileSession', 'track.love', 'track.unlove', 'track.scrobble', 'track.updateNowPlaying'):
        return urllib.request.Request(method='POST', url=url, data=urllib.parse.urlencode(params).encode('utf-8'), headers=headers)
    url = urllib.parse.urlparse(url=f'{url}?{urllib.parse.urlencode(query=params)}')
    return urllib.request.Request(method='GET', url=urllib.parse.urlunparse(url), headers=headers)

def get(url: str, headers: typ.json, params: typ.json, **kwargs) -> pydantic.BaseModel:
    '''Wrapper function for `urllib.request.urlopen` GET/POST requests which accepts URL parameters from the union of `params` and `kwargs` dictionaries.'''
    params.update(kwargs)
    log.log.debug(params)
    try:
        req = request(url=url, headers=headers, params=params)
        with urllib.request.urlopen(req) as resp:
            log.log.info(f'HTTP Request: {req.method} {resp.url} {resp.status}')
            response = json.loads(resp.read().decode('utf-8'))
        if response:
            return validate(response=response, method=params.get('method'))
        # data = validate(response=response, method=params.get('method'))
        # return return awkward.from_json(source=data.model_dump_json(exclude_none=True)) if isinstance(data, pydantic.BaseModel) else data
    except json.JSONDecodeError as error:
        jsonError(error=error)
    except urllib.error.HTTPError as error:
        httpError(error=error)
