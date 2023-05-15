#!/usr/bin/env python3

import functools
import logging
import typing

import secret
import typ

url = 'http://ws.audioscrobbler.com/2.0/'

headers = {'User-Agent': 'delannoy/0.2 (a@delannoy.cc)'}

sleep = 0.2 # [Rate limit copied from pylast since it is not explicitly mentioned in the API Terms of Service](https://github.com/pylast/pylast/blob/master/src/pylast/__init__.py#L125)

def params(_locals: typ.json) -> typ.json:
    '''Drop keys with no value from `_locals` and append json `format` parameter.'''
    params = {key.lower(): val for key, val in _locals.items() if val is not None}
    params = {**params, 'format': 'json'}
    logging.debug(params)
    return params

def required(func: typing.Callable = None) -> typing.Callable:
    '''Wrapper/decorator to extract the module and function names and pass them to the function itself (also passes `api_key`). Note that the `inner` function *does not* pass positional arguments.'''
    @functools.wraps(func)
    def inner(**kwargs) -> typ.response:
        return func(method=f'{func.__module__}.{func.__name__}', api_key=secret.api_key, **kwargs)
    return inner

def listToCSV(array: typing.List[str]) -> str:
    '''Convert each item in `array` into a string, remove any comma characters, and join into a comma-separated string'''
    array = (str(item).replace(',', '') for item in array)
    return str.join(',', array)

def arrayParams(_locals: typ.json) -> typ.json:
    return {f'{field}[{i}]': val for field, array in _locals.items() for i, val in enumerate(array)}

def validate(check: bool, descr: str):
    '''Raise `ValueError` with `descr` if `check` is `False`'''
    if not check:
        raise ValueError(descr)
