#!/usr/bin/env python3

from __future__ import annotations
import functools
import logging
import uuid

import request
import secret
import typ

url = 'http://ws.audioscrobbler.com/2.0/'

headers = {'User-Agent': 'delannoy/0.2 (a@delannoy.cc)'}

sleep = 0.2 # [Rate limit copied from pylast since it is not explicitly mentioned in the API Terms of Service](https://github.com/pylast/pylast/blob/master/src/pylast/__init__.py#L125)

def params(_locals: typ.json) -> typ.json:
    '''Drop keys with no value from `_locals` and append json `format` parameter.'''
    params = {key: val for key, val in _locals.items() if val}
    params = {**params, 'format': 'json'}
    logging.debug(params)
    return params

def required(func: typing.Callable = None) -> typing.Callable:
    '''Wrapper/decorator to extract the module and function names and pass them to the function itself (also passes `api_key`). Note that the `inner` function *does not* pass positional arguments.'''
    @functools.wraps(func)
    def inner(**kwargs) -> typ.response:
        return func(method=f'{func.__module__}.{func.__name__}', api_key=secret.api_key, **kwargs)
    return inner
