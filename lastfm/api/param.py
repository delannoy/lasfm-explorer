#!/usr/bin/env python3

from __future__ import annotations
import functools

import typ

url: str = 'http://ws.audioscrobbler.com/2.0/'

headers: dict[str, str] = {'User-Agent': 'delannoy/0.2 (a@delannoy.cc)'}

default: dict[str, str] = {'format': 'json'}

sleep: float = 0.2 # [Rate limit copied from pylast since it is not explicitly mentioned in the API TOS](https://github.com/pylast/pylast/blob/master/src/pylast/__init__.py#L115)

def method(func):
    '''Wrapper/decorator to extract the function name and pass it as a `method` argument to the function itself'''
    @functools.wraps(func)
    def inner(*args, **kwargs):
        return func(method=f'{func.__module__}.{func.__name__}', *args, **kwargs)
    return inner

def params(_locals: typ.json) -> typ.json:
    '''Drop keys with no value from `_locals` and merge with `default` dict.'''
    params = {k: v for k, v in _locals.items() if v}
    return {**default, **params}
