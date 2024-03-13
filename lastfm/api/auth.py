#!/usr/bin/env python3

import hashlib
import os

import rich.traceback
import pydantic

import log
import param
import request
import typ

rich.traceback.install(show_locals=False, max_frames=10)

try:
    user = os.environ['LASTFM_USER']
    password = os.getenv('LASTFM_PASSWORD')
except KeyError as error:
    log.log.error('Please define you last.fm username as an environment variable:\nexport LASTFM_USER=your_username')
    raise error

# [Create API account](https://www.last.fm/api/account/create)
# [API Applications(https://www.last.fm/api/accounts)
api_key = typ.UUID(hex=os.getenv('LASTFM_KEY', '12345678-1234-5678-1234-567812345678'))
api_secret = typ.UUID(hex=os.getenv('LASTFM_SECRET', '12345678-1234-5678-1234-567812345678'))

# [auth.getSession](https://www.last.fm/api/show/auth.getSession)
sk = os.getenv('LASTFM_SESSION_KEY')

@pydantic.validate_arguments
def calculate_api_sig(params: typ.json, api_secret: typ.UUID = api_secret) -> typ.UUID:
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
def getMobileSession(method: str, api_key: typ.UUID, username: str, password: str, api_sig: typ.UUID = None, sk: str = sk) -> typ.response:
    '''Create a web service session for a user. Used for authenticating a user when the password can be inputted by the user. Accepts email address as well, so please use the username supplied in the output. Only suitable for standalone mobile devices. See the authentication how-to for more. You must use HTTPS and POST in order to use this method.
        username : Required : The last.fm username or email address.
        password : Required : The password in plain text.
        api_sig  : Required : A Last.fm method signature. See authentication for more information.
        api_key  : Required : A Last.fm API key.
    '''
    api_sig = calculate_api_sig(param.params(locals()))
    return request.post(url=param.url, headers=param.headers, params=param.params(locals()))

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
    return response.token

def main():
    '''[Authentication: Desktop Application How-To](https://www.last.fm/api/desktopauth)'''
    token = getToken()
    confirm = input(f'\nPlease authorize application access from browser:\nhttp://www.last.fm/api/auth/?api_key={api_key}&token={token}\nand press `y` to confirm: ')
    if confirm.lower() in ('y', 'yes', 'yep'):
        sk = getSession(token=token)
        if sk:
            log.log.warning(f'Session key: {sk}\n(store it securely and set as `LASTFM_SESSION_KEY` environment variable)')
