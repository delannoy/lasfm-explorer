#!/usr/bin/env python3

import hashlib
import logging

import pydantic

import typ
import param
import request
import secret

@pydantic.validate_arguments
def calculate_api_sig(params: typ.json, api_secret: typ.UUID = secret.api_secret) -> typ.UUID:
    '''Calculates `api_sig` (sorts all method call `params`, merges them into a continous string of key & value pairs, and calculates md5)'''
    # https://www.last.fm/api/authspec
    # https://lastfm-docs.github.io/api-docs/auth/signature/
    # [Last.fm API invalid method signature but valid when getting session key](https://stackoverflow.com/a/45907546/13019084)
    sorted_params = [f'{key}{val}' for key, val in sorted(params.items()) if key not in ('api_sig', 'callback', 'format')]
    api_sig = str.join('', sorted_params) + str(api_secret)
    api_sig = hashlib.md5(api_sig.encode('utf-8')).hexdigest()
    return typ.UUID(api_sig)

@param.required
@pydantic.validate_arguments
def getMobileSession(method: str, api_key: typ.UUID, username: str, password: str, api_sig: typ.UUID = None, sk: str = secret.sk) -> typ.response:
    '''Create a web service session for a user. Used for authenticating a user when the password can be inputted by the user. Accepts email address as well, so please use the username supplied in the output. Only suitable for standalone mobile devices. See the authentication how-to for more. You must use HTTPS and POST in order to use this method.
        username : Required : The last.fm username or email address.
        password : Required : The password in plain text.
        api_sig  : Required : A Last.fm method signature. See authentication for more information.
        api_key  : Required : A Last.fm API key.
    '''
    api_sig = calculate_api_sig(param.params(locals()))
    return request.get(url=param.url, headers=param.headers, params=param.params(locals()))

@param.required
@pydantic.validate_arguments
def getSession(method: str, api_key: typ.UUID, token: str, api_sig: typ.UUID = None) -> typ.response:
    '''Fetch a session key for a user. The third step in the authentication process. See the authentication how-to for more information.
        token   : Required : A 32-character ASCII hexadecimal MD5 hash returned by step 1 of the authentication process (following the granting of permissions to the application by the user)
        api_sig : Required : A Last.fm method signature. See authentication for more information.
        api_key : Required : A Last.fm API key.
    '''
    api_sig = calculate_api_sig(param.params(locals()))
    return request.get(url=param.url, headers=param.headers, params=param.params(locals()))

@param.required
@pydantic.validate_arguments
def getToken(method: str, api_key: typ.UUID, api_sig: typ.UUID = None) -> str:
    '''Fetch an unathorized request token for an API account. This is step 2 of the authentication process for desktop applications. Web applications do not need to use this service.
        api_sig : Required : A Last.fm method signature. See authentication for more information.
        api_key : Required : A Last.fm API key.
    '''
    api_sig = calculate_api_sig(param.params(locals()))
    response = request.get(url=param.url, headers=param.headers, params=param.params(locals()))
    logging.info(f'Please authorize application access from browser: http://www.last.fm/api/auth/?api_key={secret.api_key}&token={response.get("token")}')
    return response.get('token')
