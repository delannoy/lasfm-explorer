#!/usr/bin/env python3

from __future__ import annotations

url: str = 'http://ws.audioscrobbler.com/2.0/'

headers: dict[str, str] = {'User-Agent': 'delannoy/0.1 (a@delannoy.cc)'}

default: dict[str, str] = {'format': 'json'}

params: typing.Dict[str, typing.Any] = {'user': 'USER', 'api_key': 'APIKEY'}

sleep: float = 0.2 # [Rate limit copied from pylast since it is not explicitly mentioned in the API TOS](https://github.com/pylast/pylast/blob/master/src/pylast/__init__.py#L115)
