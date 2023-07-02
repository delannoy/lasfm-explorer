#!/usr/bin/env python3

from __future__ import annotations
import asyncio
import datetime
import fileinput
import functools
import json
import logging
import math
import pathlib

import aiometer
import httpx
import rich.console
import rich.live
import rich.progress

from api import auth
from api import user
import log
import param

log.log.setLevel(logging.getLevelName('INFO'))

PARAMS = {'method': 'user.getRecentTracks', 'api_key': auth.api_key, 'user': auth.user, 'format': 'json', 'limit': 1000}
EXPORT_PATH = pathlib.Path(f"data/{PARAMS.get('user')}/RecentTracks")
HTTPX_TIMEOUT = 60.0
PROGRESS_COLS = (rich.progress.TextColumn(text_format='[bold blue]{task.fields[year]}-{task.fields[page]:03d}'),
                rich.progress.BarColumn(bar_width=None),
                rich.progress.TaskProgressColumn(text_format='[progress.percentage]{task.percentage:>3.1f}%'),
                rich.progress.DownloadColumn(),
                rich.progress.TransferSpeedColumn(),
                rich.progress.TimeRemainingColumn())

def yearRange(year: int) -> tuple[int, int]:
    '''Calculate unix timestamps corresponding to the start and end of `year`.'''
    FROM = int(datetime.datetime.fromisoformat(f'{year}-01-01T00:00:00+00:00').timestamp())
    TO = int(datetime.datetime.fromisoformat(f'{year}-12-31T23:59:59+00:00').timestamp())
    return (FROM, TO)

def getURL(year: int) -> list[httpx.URL]:
    '''Return paginated URLs for the given `year`.'''
    FROM, TO = yearRange(year=year)
    total_pages = math.ceil(int(user.getRecentTracks(user=PARAMS.get('user'), FROM=FROM, TO=TO, limit=1).attr.totalPages) / PARAMS.get('limit'))
    return [httpx.URL(url=param.url, params={**PARAMS, 'from': FROM, 'to': TO, 'page': page}) for page in range(1, total_pages+1)]

async def download(url: httpx.URL, progress: rich.progress.Progress, task: rich.progress.Task):
    '''Query `url`, remove `nowplaying` track from response, and write to disk.'''
    year = task.fields.get('year')
    page = task.fields.get('page')
    filepath = pathlib.Path(f'{EXPORT_PATH}/{year}-{page:03d}.json')
    async with httpx.AsyncClient(timeout=HTTPX_TIMEOUT) as async_client:
        async with async_client.stream(method='GET', url=url, headers=param.headers) as response:
            task.total = int(response.headers.get('Content-Length'))
            data = bytes()
            async for chunk in response.aiter_bytes():
                data = data + chunk
                progress.update(task_id=task.id, completed=response.num_bytes_downloaded)
    response = json.loads(data.decode('utf-8'))
    response['recenttracks']['track'] = [track for track in response.get('recenttracks').get('track') if not track.get('@attr')] # remove `nowplaying` track from response
    with open(filepath, mode='w') as out_file:
        json.dump(obj=response, fp=out_file)

def playsOnDisk(filepath_glob: str = '*json') -> int:
    '''Calculate number of track plays on disk for files matching `filepath_glob`.'''
    try:
        with fileinput.input(files=pathlib.Path(EXPORT_PATH).glob(filepath_glob), mode='r') as files:
            return sum(len(json.loads(f).get('recenttracks').get('track')) for f in files)
    except json.decoder.JSONDecodeError as error:
        log.log.error(f'JSON decode error when reading exported files:\n{sorted(pathlib.Path(EXPORT_PATH).glob(filepath_glob))}\nplease remove incomplete/corrupted file(s)\n')
        raise error

def validateExport(playcount: int, filepath_glob: str = '*json'):
    '''Verify that the number of track plays for files matching `filepath_glob` is equal to `playcount`.'''
    playcount_on_disk = playsOnDisk(filepath_glob=filepath_glob)
    log.log.info(f'{playcount} plays already exported') if playcount_on_disk == playcount else log.log.warning(f'export incomplete\n{playcount = }\n{playcount_on_disk = }')
    return playcount_on_disk == playcount

def alreadyExported(year: int):
    '''Check if all files corresponding to `year` have been exported with the expected number of track plays.'''
    if not sorted(pathlib.Path(EXPORT_PATH).glob(f'{year}*json')):
        return False
    FROM, TO = yearRange(year=year)
    playcount = int(user.getRecentTracks(user=PARAMS.get('user'), FROM=FROM, TO=TO, limit=1).attr.totalPages)
    return validateExport(playcount=playcount, filepath_glob=f'{year}*.json')

async def export(force: bool = False):
    '''Export all last.fm data for `PARAMS['user']`.'''
    total_playcount = int(user.getInfo(user=PARAMS.get('user')).playcount)
    first_scrobble = user.getRecentTracks(user=PARAMS.get('user'), limit=1, page=total_playcount).track.date.dateTime[-1]
    begin_year = datetime.datetime.fromisoformat(f'{first_scrobble}+00:00').year
    current_year = datetime.datetime.now(tz=datetime.timezone.utc).year
    for year in range(begin_year, current_year+1):
        rich.console.Console().rule(title=str(year))
        if (not force) and alreadyExported(year=year):
            continue
        urls = getURL(year)
        progress = rich.progress.Progress(*PROGRESS_COLS)
        _ = [progress.add_task(description=f'{year}-{page:03d}', year=year, page=page) for page, url in enumerate(urls, start=1)]
        with rich.live.Live(progress):
            jobs = [functools.partial(download, url=url, progress=progress, task=progress.tasks[page]) for page, url in enumerate(urls)]
            await aiometer.run_all(jobs, max_per_second=1/param.sleep)

def main():
    '''Run data export asynchronously.'''
    EXPORT_PATH.mkdir(parents=True, exist_ok=True)
    return asyncio.run(export())

if __name__ == '__main__':
    main()
