#!/usr/bin/env python3

import json
import pathlib
import urllib.error
import urllib.parse
import urllib.request

import pydantic
import rich.progress

import api.errors
import api.models
import log
import typ

def http_error(error: urllib.error.HTTPError):
    '''Log `urllib.error.HTTPError`. Log corresponding `__doc__` string from `api.errors.Errors` enum.'''
    log.log.debug(f'{error.code = }')
    log.log.debug(f'{error.reason = }')
    log.log.debug(f'{dict(error.headers) = }')
    response = error.read().decode('utf-8')
    if 'json' not in error.headers.get('Content-Type'):
        return log.log.error(f'{response = }')
    response = json.loads(response)
    if response.get('error') in {e.value for e in api.errors.Errors}:
        error_enum = api.errors.Errors(response.get('error'))
        log.log.error(f'{error_enum.name = }')
        log.log.error(f'{error_enum.__doc__ = }')
    log.log.error(f'{response = }')

def json_error(error: json.JSONDecodeError):
    '''Log `json.JSONDecodeError`.'''
    log.log.debug(f'{error.doc = }')
    log.log.debug(f'{error.msg = }')
    log.log.debug(f'{error.lineno = }')
    log.log.debug(f'{error.colno = }')
    log.log.debug(f'{error.pos = }')
    return log.log.error(f'json.JSONDecodeError: {error}')

def get(url: str, headers: typ.json = pydantic.Field(default_factory=dict), params: typ.json = pydantic.Field(default_factory=dict), **kwargs) -> typ.response:
    '''Wrapper function for `urllib.request.urlopen` GET requests which accepts URL parameters from the union of `params` and `kwargs` dictionaries.'''
    data = urllib.parse.urlencode({**params, **kwargs})
    try:
        if params.get('method') in ('track.love', 'track.unlove', 'track.scrobble', 'track.updateNowPlaying'):
            request = urllib.request.Request(url=url, data=data.encode('utf-8'), headers=headers)
        else:
            request = urllib.request.Request(url=f'{url}?{data}', headers=headers)
        log.log.debug(request.full_url)
        response = urllib.request.urlopen(request)
        return json.loads(response.read().decode('utf-8'))
    except json.JSONDecodeError as error:
        json_error(error=error)
    except urllib.error.HTTPError as error:
        http_error(error=error)

def download(filepath: pathlib.Path, url: str, headers: typ.json = pydantic.Field(default_factory=dict), params: typ.json = pydantic.Field(default_factory=dict), **kwargs) -> None:
    '''Wrapper function to download the response to a GET request with a `rich` progress bar.'''
    # https://github.com/Textualize/rich/blob/master/examples/downloader.py
    url = f'{url}?{urllib.parse.urlencode({**params, **kwargs})}'
    try:
        response = urllib.request.urlopen(urllib.request.Request(url, headers=headers))
    except urllib.error.HTTPError as error:
        return http_error(error=error)

    # [Progress Display](https://rich.readthedocs.io/en/stable/progress.html)
    progress = rich.progress.Progress( # [rich.progress.Progress](https://rich.readthedocs.io/en/stable/reference/progress.html#rich.progress.Progress)
                rich.progress.TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
                rich.progress.BarColumn(bar_width=None),
                '[progress.percentage]{task.percentage:>3.1f}%', '|', rich.progress.DownloadColumn(), '|', rich.progress.TransferSpeedColumn(), '|', rich.progress.TimeRemainingColumn(),
                refresh_per_second=10, # Number of times per second to refresh the progress information or None to use default (10).
                speed_estimate_period=1, # Period (in seconds) used to calculate the speed estimate. Defaults to 30.
                transient=False, # Clear the progress on exit. Defaults to False.
                expand=True, # Expand tasks table to fit width. Defaults to False.
                )

    task_id = progress.add_task(description="download", start=False, filename=filepath)
    progress.console.log(f"Requesting {url}")
    progress.update(task_id=task_id, total=float(response.headers.get('Content-length')))
    with progress:
        with open(filepath, 'wb') as out_file:
            progress.start_task(task_id=task_id)
            for chunk in iter(lambda: response.read(2**10), b''):
                out_file.write(chunk)
                progress.update(task_id=task_id, advance=len(chunk))
        progress.console.log(f'Downloaded {filepath}')
