#!/usr/bin/env python3

from __future__ import annotations
import json
import logging
import os
import time
import urllib

import awkward
import rich.logging

import api

rich_handler = rich.logging.RichHandler(rich_tracebacks=True, log_time_format="[%Y-%m-%d %H:%M:%S]") # [rich.logging](https://rich.readthedocs.io/en/stable/reference/logging.html)
logging.basicConfig(level=logging.DEBUG, format='%(message)s', handlers=[rich_handler])

def auth():
    # [HTTP Authentication in Python](https://stackoverflow.com/questions/720867/http-authentication-in-python)
    username, password = os.getenv('MUSICBRAINZ_USERNAME'), os.getenv('MUSICBRAINZ_PASSWORD')
    if username and password:
        password_manager = urllib.request.HTTPPasswordMgr()
        password_manager.add_password(realm='musicbrainz.org', uri='musicbrainz.org', user=username, passwd=password)
        auth_handler = urllib.request.HTTPDigestAuthHandler(password_manager)
        opener = urllib.request.build_opener(auth_handler)
        return opener

def get(endpoint: str, **kwargs) -> awkward.Record:
    time.sleep(api.SLEEP)
    url = f'https://musicbrainz.org/ws/2{endpoint}'
    headers = {'User-Agent': api.USER_AGENT, 'Accept': 'application/json'}
    params = {k: v for k, v in kwargs.items() if v is not None}
    if (kwargs.get('inc') is not None) and ('user' in kwargs.get('inc')):
        params.update(dict(client=api.CLIENT))
        urllib.request.install_opener(auth())
    logging.debug(f'{endpoint} | {params}')
    request = urllib.request.Request(url=f'{url}?{urllib.parse.urlencode(params)}', headers=headers)
    try:
        with urllib.request.urlopen(request) as response:
            return awkward.from_json(source=response.read().decode('utf-8'))
    except urllib.error.HTTPError as http_error:
        logging.error(f'{http_error.status} | {http_error.reason} | {http_error.url}')
        if 'json' in http_error.headers.get('Content-Type', ''):
            logging.error(json.loads(http_error.read().decode('utf-8')).get('error'))
