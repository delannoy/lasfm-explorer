#!/usr/bin/env python3

from __future__ import annotations
import json
import logging
import pathlib
import urllib.error
import urllib.parse
import urllib.request

import rich.logging
import rich.progress

import typ
import errors
import param

 # [Logging Handler](https://rich.readthedocs.io/en/stable/logging.html)
 # [rich.logging](https://rich.readthedocs.io/en/stable/reference/logging.html)
log_level = logging.DEBUG
handler = rich.logging.RichHandler(rich_tracebacks=True, log_time_format="[%Y-%m-%d %H:%M:%S]")
logging.basicConfig(level=log_level, format='%(message)s', handlers=[handler])
log = logging.getLogger()

# [Progress Display](https://rich.readthedocs.io/en/stable/progress.html)
# [rich.progress.Progress](https://rich.readthedocs.io/en/stable/reference/progress.html#rich.progress.Progress)
progress = rich.progress.Progress(
            rich.progress.TextColumn("[bold blue]{task.fields[filename]}", justify="right"),
            rich.progress.BarColumn(bar_width=None),
            "[progress.percentage]{task.percentage:>3.1f}%",
            "•",
            rich.progress.DownloadColumn(),
            "•",
            rich.progress.TransferSpeedColumn(),
            "•",
            rich.progress.TimeRemainingColumn(),
            refresh_per_second=10, # Number of times per second to refresh the progress information or None to use default (10).
            speed_estimate_period=1, # Period (in seconds) used to calculate the speed estimate. Defaults to 30.
            transient=False, # Clear the progress on exit. Defaults to False.
            expand=True, # Expand tasks table to fit width. Defaults to False.
            )

def get(url: str = param.url, headers: dict[str, str] = param.headers, params: typ.json = param.default, **kwargs) -> typ.response:
    '''Wrapper function for `urllib.request.urlopen` GET requests which accepts URL parameters from the union of `params` and `kwargs` dictionaries.'''
    url = f'{url}?{urllib.parse.urlencode({**params, **kwargs})}'
    log.info(url)
    try:
        response = urllib.request.urlopen(urllib.request.Request(url, headers=headers))
        return json.loads(response.read().decode('utf-8'))
    except json.JSONDecodeError as error:
        json_error(error=error)
    except urllib.error.HTTPError as error:
        http_error(error=error)

def http_error(error: urllib.error.HTTPError):
    '''Log `urllib.error.HTTPError`. Log corresponding `__doc__` string from `errors.Errors` enum.'''
    log.debug(f'{error.code = }')
    log.debug(f'{error.reason = }')
    log.debug(f'{dict(error.headers) = }')
    response = error.read().decode('utf-8')
    if not 'json' in error.headers.get('Content-Type'):
        return log.error(response)
    response = json.loads(response)
    if not response.get('error') in {e.value for e in errors.Errors}:
        return log.error(response)
    error_enum = errors.Errors(response.get('error'))
    log.error(error_enum.name)
    log.error(error_enum.__doc__)

def json_error(error: json.JSONDecodeError):
    '''Log `json.JSONDecodeError`.'''
    log.debug(f'{error.doc = }')
    log.debug(f'{error.msg = }')
    log.debug(f'{error.lineno = }')
    log.debug(f'{error.colno = }')
    log.debug(f'{error.pos = }')
    return log.error(f'json.JSONDecodeError: {error}')

def download(filepath: pathlib.Path, url: str = param.url, headers: dict[str, str] = param.headers, params: typ.json = param.default, **kwargs) -> None:
    '''Wrapper function to download the response to a GET request with a `rich` progress bar.'''
    # https://github.com/Textualize/rich/blob/master/examples/downloader.py
    url = f'{url}?{urllib.parse.urlencode({**params, **kwargs})}'
    try:
        response = urllib.request.urlopen(urllib.request.Request(url, headers=headers))
    except urllib.error.HTTPError as error:
        return http_error(error=error)
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
