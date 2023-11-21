#!/usr/bin/env python3

from __future__ import annotations
import asyncio
import dataclasses
import datetime
import functools
import json
import logging
import math
import pathlib
import typing

import aiofiles
import aiometer
import httpx
import pandas
import rich.console
import rich.live
import rich.progress

from api import auth
from api import user
import log
import param

# to do:
    # export in series (urllib) if `httpx` is unavailable?
    # async/parallelize all years

log.log.setLevel(logging.getLevelName('INFO'))

PARAMS = {'method': 'user.getRecentTracks', 'api_key': auth.api_key, 'user': auth.user, 'format': 'json', 'limit': 1000}
EXPORT_PATH = pathlib.Path(f"data/{PARAMS.get('user')}/RecentTracks")
HTTPX_TIMEOUT = 60.0
PROGRESS_COLS = (rich.progress.TextColumn(text_format='[bold blue]{task.description}'),
                 rich.progress.BarColumn(bar_width=None),
                 rich.progress.TaskProgressColumn(text_format='[progress.percentage]{task.percentage:>3.1f}%'),
                 rich.progress.DownloadColumn(),
                 rich.progress.TransferSpeedColumn(),
                 rich.progress.TimeRemainingColumn())


class Disk:

    @staticmethod
    async def readTracks(file: pathlib.Path) -> int:
        '''Calculate number of track plays on disk for `file`.'''
        async with aiofiles.open(file, mode='r') as f:
            data = await f.read()
        try:
            return json.loads(data).get('recenttracks').get('track')
        except json.decoder.JSONDecodeError as error:
            log.log.error(f'JSON decode error when reading exported file: "{file}"\n') # please remove incomplete/corrupted file(s)\n')
            return list()

    @classmethod
    async def readAllTracks(cls, filepath_glob: str = '*json') -> int:
        '''Return track plays on disk for files matching `filepath_glob`.'''
        return [track for file in EXPORT_PATH.glob(filepath_glob) for track in await cls.readTracks(file)]

    @classmethod
    async def playcount(cls, filepath_glob: str = '*json') -> int:
        '''Calculate number of track plays on disk for files matching `filepath_glob`.'''
        return sum([len(await cls.readTracks(file)) for file in EXPORT_PATH.glob(filepath_glob)])

    @classmethod
    async def exported(cls, year: int, api_playcount: int) -> bool:
        '''Check if all files corresponding to `year` have been exported with the expected number of track plays.'''
        filepath_glob = f'{year}*json'
        if not list(EXPORT_PATH.glob(filepath_glob)):
            return False
        disk_playcount = await cls.playcount(filepath_glob=filepath_glob)
        log.log.info(f'{disk_playcount} plays already exported') if (disk_playcount == api_playcount) else log.log.warning(f'export incomplete:\n{disk_playcount = }\n{api_playcount  = }')
        return disk_playcount == api_playcount


class Playcount:

    @staticmethod
    async def annual(year: int) -> int:
        '''Query playcount for `year`'''
        FROM, TO = yearRange(year=year)
        url = httpx.URL(url=param.url, params={**PARAMS, 'from': FROM, 'to': TO, 'page': 1, 'limit': 1})
        async with httpx.AsyncClient(timeout=HTTPX_TIMEOUT) as async_client:
            response = await async_client.get(url=url)
        return int(response.json().get('recenttracks').get('@attr').get('total'))

    @classmethod
    async def overall(cls, begin_year: int, end_year: int) -> dict[str, int]:
        '''Query playcount for all years between `begin_year` and `end_year`.'''
        jobs = [functools.partial(cls.annual, year=year) for year in range(begin_year, end_year+1)]
        playcount = await aiometer.run_all(jobs, max_per_second=1/param.sleep)
        year = list(map(str, range(begin_year, end_year+1)))
        return dict(zip(year, playcount))


@dataclasses.dataclass
class Response:
    url: httpx.URL
    progress: rich.progress.Progress
    task: rich.progress.Task

    async def collect(self) -> dict[str, typing.Any]:
        '''Stream async GET request with `rich.progress`.'''
        data = bytearray()
        async with httpx.AsyncClient(timeout=HTTPX_TIMEOUT).stream(method='GET', url=self.url, headers=param.headers) as response:
            self.task.total = int(response.headers.get('Content-Length'))
            async for chunk in response.aiter_bytes():
                data.extend(chunk)
                self.progress.update(task_id=self.task.id, completed=response.num_bytes_downloaded)
        return json.loads(data.decode('utf-8'))

    async def download(self) -> None:
        '''Query `self.url`, remove `nowplaying` track from response, and write to disk.'''
        response = await self.collect()
        response['recenttracks']['track'] = [track for track in response.get('recenttracks').get('track') if not track.get('@attr')] # remove `nowplaying` track from response
        filepath = pathlib.Path(f'{EXPORT_PATH}/{self.task.description}.json')
        with filepath.open(mode='w') as out_file:
            json.dump(obj=response, fp=out_file)


@dataclasses.dataclass
class Serialize:
    out_file: pathlib.Path = pathlib.Path(EXPORT_PATH/'pd_tracks.feather')

    @staticmethod
    def akToParquet():
        '''Serialize exported data to `awkward.Array` in parquet format.'''
        import awkward
        tracks = awkward.Array(asyncio.run(Disk.readAllTracks()))
        awkward.to_parquet(array=tracks, destination=pathlib.Path(EXPORT_PATH/'ak_tracks.parquet'))

    def pdToFeather(self):
        '''Serialize exported data to `pandas.DataFrame` in feather format.'''
        log.log.info(f'Serializing all exported data: "{self.out_file}"')
        tracks = pandas.DataFrame(asyncio.run(Disk.readAllTracks()))
        tracks.to_feather(path=self.out_file)

    def topTracks(self) -> pandas.DataFrame:
        '''Read exported data and group by artist_name and track_name.'''
        import pandas
        if not self.out_file.exists():
            self.pdToFeather()
        tracks = pandas.read_feather(self.out_file)
        tracks = [pandas.json_normalize(tracks.artist)['#text'].rename('artist'), tracks.name.rename('track'), tracks.streamable.rename('playcount')]
        top_tracks = pandas.concat(objs=tracks, axis=1).apply(lambda col: col.str.casefold())
        top_tracks = top_tracks.groupby(['artist', 'track']).count().sort_values(by='playcount', ascending=False).reset_index()
        return top_tracks

    @classmethod
    def _topTracks(self) -> pandas.DataFrame:
        '''Read exported data and group by artist_name, artist_mbid, album_name, album_mbid, track_name, and track_mbid.'''
        import pandas
        if not self.out_file.exists():
            self.pdToFeather()
        data = pandas.read_feather(self.out_file)
        artists = pandas.json_normalize(data.artist).rename(columns={'#text': 'artist_name', 'mbid': 'artist_mbid'})
        albums = pandas.json_normalize(data.album).rename(columns={'#text': 'album_name', 'mbid': 'album_mbid'})
        tracks = data[['name', 'mbid', 'streamable']].rename(columns={'name': 'track_name', 'mbid': 'track_mbid', 'streamable': 'playcount'})
        top_tracks = pandas.concat(objs=[artists, albums, tracks], axis=1).apply(lambda col: col.str.casefold())
        top_tracks = top_tracks.groupby([col for col in top_tracks.columns if col != 'playcount']).count().sort_values(by='playcount', ascending=False).reset_index().replace('', None)
        return top_tracks


def yearRange(year: int) -> tuple[int, int]:
    '''Return unix timestamps corresponding to the start and end of `year`.'''
    FROM = int(datetime.datetime.fromisoformat(f'{year}-01-01T00:00:00+00:00').timestamp())
    TO = int(datetime.datetime.fromisoformat(f'{year}-12-31T23:59:59+00:00').timestamp())
    return (FROM, TO)

def getURL(year: int) -> list[httpx.URL]:
    '''Return paginated URLs for the given `year`.'''
    FROM, TO = yearRange(year=year)
    total_pages = math.ceil(user.getRecentTracks(user=PARAMS.get('user'), FROM=FROM, TO=TO, limit=1).attr.totalPages / PARAMS.get('limit'))
    return [httpx.URL(url=param.url, params={**PARAMS, 'from': FROM, 'to': TO, 'page': page}) for page in range(1, total_pages+1)]

async def exportYear(year: int) -> None:
    '''Export all last.fm data for `PARAMS[user]` during `year`.'''
    urls = getURL(year=year)
    progress = rich.progress.Progress(*PROGRESS_COLS)
    _ = [progress.add_task(description=f'{year}-{page:03d}') for page, url in enumerate(urls, start=1)]
    with rich.live.Live(progress):
        jobs = [Response(url=url, progress=progress, task=progress.tasks[task_id]).download for task_id, url in enumerate(urls)]
        await aiometer.run_all(jobs, max_per_second=1/param.sleep)

async def export(force: bool = False) -> None:
    '''Export all last.fm data for `PARAMS['user']`.'''
    playcount_total = user.getInfo(user=PARAMS.get('user')).playcount
    begin_year = user.getRecentTracks(user=PARAMS.get('user'), limit=1, page=playcount_total).track[-1].date.dateTime.year
    current_year = datetime.datetime.now(tz=datetime.timezone.utc).year
    playcount_per_year = await Playcount.overall(begin_year, current_year)
    for year in range(begin_year, current_year+1):
        rich.console.Console().rule(title=str(year))
        already_exported = await Disk.exported(year=year, api_playcount=playcount_per_year.get(str(year)))
        if (not force) and already_exported:
            continue
        await exportYear(year=year)

def main() -> None:
    '''Export data asynchronously.'''
    EXPORT_PATH.mkdir(parents=True, exist_ok=True)
    asyncio.run(export())
    Serialize().pdToFeather()

if __name__ == '__main__':
    main()
