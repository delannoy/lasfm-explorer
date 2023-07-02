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
import rich.progress
import rich.live

from api import auth
from api import user
import log
import param

log.log.setLevel(logging.getLevelName('INFO'))

PARAMS = {'method': 'user.getRecentTracks', 'api_key': auth.api_key, 'user': auth.user, 'format': 'json', 'limit': 1000}
EXPORT_PATH = pathlib.Path(f'data/{auth.user}/RecentTracks')
PROGRESS_COLS = (rich.progress.TextColumn("[bold blue]{task.fields[year]}-{task.fields[page]:03d}", justify="right"),
                rich.progress.BarColumn(bar_width=None),
                rich.progress.TaskProgressColumn(text_format='[progress.percentage]{task.percentage:>3.1f}%'),
                rich.progress.DownloadColumn(),
                rich.progress.TransferSpeedColumn(),
                rich.progress.TimeRemainingColumn())

def getURL(year: int) -> list[httpx.URL]:
    '''Return paginate URLs for the given `year`.'''
    FROM = int(datetime.datetime.fromisoformat(f'{year}-01-01T00:00:00+00:00').timestamp())
    TO = int(datetime.datetime.fromisoformat(f'{year}-12-31T23:59:59+00:00').timestamp())
    total_pages = math.ceil(int(user.getRecentTracks(FROM=FROM, to=TO, limit=1).attr.totalPages) / PARAMS.get('limit'))
    return [httpx.URL(url=param.url, params={**PARAMS, 'from': FROM, 'to': TO, 'page': page}) for page in range(1, total_pages+1)]

async def download(url: httpx.URL, progress: rich.progress.Progress, task: rich.progress.Task):
    '''Query `url`, remove `nowplaying` track from response, and write to disk.'''
    year = task.fields.get('year')
    page = task.fields.get('page')
    filepath = pathlib.Path(f'{EXPORT_PATH}/{year}-{page:03d}.json')
    async with httpx.AsyncClient(timeout=30.0) as async_client:
        async with async_client.stream(method='GET', url=url, headers=param.headers) as response:
            task.total = int(response.headers.get('Content-Length'))
            data = ''
            async for chunk in response.aiter_bytes():
                data = data + chunk.decode('utf-8')
                progress.update(task_id=task.id, completed=response.num_bytes_downloaded)
    response = json.loads(data)
    response['recenttracks']['track'] = [track for track in response.get('recenttracks').get('track') if not track.get('@attr')] # remove `nowplaying` track from response
    with open(filepath, mode='w') as out_file:
        json.dump(obj=response, fp=out_file)

def validateExport(playcount: int):
    '''Verify that the number of plays on disk matches the reported total number of plays'''
    log.log.info('validating export...')
    with fileinput.input(files=pathlib.Path(EXPORT_PATH).glob('*.json'), mode='r') as files:
        scrobbles_on_disk = sum(len(json.loads(f).get('recenttracks').get('track')) for f in files)
    if scrobbles_on_disk == playcount:
        log.log.info('export completed successfully!')
    else:
        log.log.error('export did not complete successfully :({\nplaycount = }\n{scrobbles_on_disk = }')

async def export(begin_year: int = None):
    '''Export all data or export data starting from `begin_year`.'''
    playcount = int(user.getInfo().playcount)
    if not begin_year:
        first_scrobble = user.getRecentTracks(limit=1, page=playcount).track.date.dateTime[-1]
        begin_year = datetime.datetime.fromisoformat(f'{first_scrobble}+00:00').year
    current_year = datetime.datetime.now(tz=datetime.timezone.utc)
    for year in range(begin_year, current_year.year+1):
        urls = getURL(year)
        log.log.info(f'{year} [{len(urls)} pages]')
        progress = rich.progress.Progress(*PROGRESS_COLS)
        _ = [progress.add_task(description=f'{year}-{page:03d}', year=year, page=page) for page, url in enumerate(urls, start=1)]
        with rich.live.Live(progress):
            jobs = [functools.partial(download, url=url, progress=progress, task=progress.tasks[page]) for page, url in enumerate(urls)]
            await aiometer.run_all(jobs, max_per_second=1/param.sleep)
    validateExport(playcount=playcount)

def main(all: bool = False):
    '''Export all data unless exported files already exist on disk (in which case, export data starting from the most recently exported year).'''
    EXPORT_PATH.mkdir(parents=True, exist_ok=True)
    if all or not sorted(pathlib.Path(EXPORT_PATH).glob('*json')):
        return asyncio.run(export())
    else:
        year = int(sorted(pathlib.Path(EXPORT_PATH).glob('*json'))[-1].stem.split('-')[0])
        return asyncio.run(export(begin_year=year))

if __name__ == '__main__':
    main()
