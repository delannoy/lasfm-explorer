#!/usr/bin/env python3

from __future__ import annotations
import dataclasses
import inspect
import logging

import typ
import param
import request

logging.basicConfig(format='%(levelname)s: %(message)s', level=logging.DEBUG)


@dataclasses.dataclass
class Library:

    method: str = __module__
    url: str = param.url
    headers: dict[str, str] = dataclasses.field(default_factory=lambda: param.headers)
    params: typ.json = dataclasses.field(default_factory=lambda: {**param.default, **param.params})

    def __getattribute__(self, attr: str, descr: bool = True):
        '''Intercept all attribute accesses and append user-defined method/function names to `self.method`'''
        logging.debug(f'{attr = }')
        logging.debug(f'{hasattr(Library, attr) = }')
        if hasattr(Library, attr):
            logging.debug(f'{getattr(Library, attr) = }')
            logging.debug(f'{dir(getattr(Library, attr)) = }')
        logging.debug(f'{inspect.getattr_static(self, attr) = }')
        logging.debug(f'{type(inspect.getattr_static(self, attr)) = }')
        logging.debug(f'{inspect.isfunction(inspect.getattr_static(self, attr)) = }')
        logging.debug(f'{callable(inspect.getattr_static(self, attr)) = }')
        logging.debug(f'{hasattr(type(inspect.getattr_static(self, attr)), "__call__") = }')
        attribute = object.__getattribute__(self, attr) # super().__getattribute__(attr) # [object.__getattribute__](https://docs.python.org/3/reference/datamodel.html#object.__getattribute__)
        if descr:
            attribute_descriptor = inspect.getattr_static(self, attr) # [Retrieve attributes without triggering dynamic lookup via the descriptor protocol](https://docs.python.org/3.3/library/inspect.html#inspect.getattr_static)
            if inspect.isfunction(attribute_descriptor): # [How do I detect whether a Python variable is a function?](https://stackoverflow.com/a/8302728)
                self.params['method'] = f'{self.method}.{attr}'
                return attribute
            else:
                return attribute
        else:
            if callable(attribute): # [How do I detect whether a Python variable is a function?](https://stackoverflow.com/a/624939)
                self.params['method'] = f'{self.method}.{attr}'
                return attribute
            else:
                return attribute

    def getArtists(self, user: str = param.params.get('user'), limit: int = 50, page: int = 1, api_key: typ.uuid = param.params.get('api_key')) -> typ.response:
        '''A paginated list of all the artists in a user's library, with play counts and tag counts.
            user    : Required : The user whose library you want to fetch.
            limit   : Optional : The number of results to fetch per page. Defaults to 50.
            page    : Optional : The page number you wish to scan to.
            api_key : Required : A Last.fm API key.
        '''
        kwargs = {k: v for k, v in locals().items() if k != 'self'}
        return request.get(url=param.url, headers=self.headers, params={**self.params, **kwargs})
