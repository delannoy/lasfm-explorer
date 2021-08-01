#!/usr/bin/env python3

'''
Export lastFM data as JSON files and merge them into a flat pandas.DataFrame.
'''

from __future__ import annotations # [PEP 563 -- Postponed Evaluation of Annotations](https://www.python.org/dev/peps/pep-0563/)
from apiWrapper import Param, getReq
from util import flattenDF, loadJSON, mergeRecentTracks, writeCSV
import logFormat
import datetime, enlighten, json, logging, math, time

def downloadData(param:Param, download:bool=True):
    '''Download user data (if {download} is True) to json files, merge them into a flat pandas.DataFrame, and write it to disk.'''
    logging.info(f"{param.filePath().name.replace('.','|')}")
    if download:
        subMethod = param.splitMethod(lower=True)
        for f in param.filePath(glob='*json'): f.unlink()
        pbarManager = enlighten.get_manager()
        with pbarManager.counter(unit='page', leave=False) as pbar:
            while param.page <= param.nPages:
                fileName = param.filePath(ext=f'.{param.page:04d}.json')
                response = getReq(param=param, pbarManager=pbarManager, collapse=False)
                param.page = int(response.get(subMethod).get('@attr').get('page'))
                param.nPages = int(response.get(subMethod).get('@attr').get('totalPages'))
                pbar.total = param.nPages # [tqdm: update total without resetting time elapsed](https://stackoverflow.com/a/58961015/13019084)
                pbar.update()
                param.filePath().parent.mkdir(exist_ok=True)
                with open(file=fileName, mode='w') as jsonF: json.dump(obj=response, fp=jsonF)
                param.page += 1
                time.sleep(param.sleep)
        pbarManager.stop()
    DF = loadJSON(param)
    df = flattenDF(param=param, DF=DF, writeToDisk=True)
    if param.splitMethod() in ['TopArtists','TopAlbums','TopTracks']: writeCSV(param=param, df=df)

def exportScrobbles():
    '''Fetch and process user scrobbles for the current year and for any year where exported json files are not present.'''
    def earliestScrobbleYear() -> int:
        '''Determine the earliest year for the user's scrobbles.'''
        lastPage = int(getReq(param=Param(method='user.getInfo')).get('playcount')) - 100 # subtract 100 plays, in case some have "unknown" scrobble dates, i.e. 1970
        return getReq(param=Param(method='user.getRecentTracks', lim=1, page=lastPage)).loc[0,'date'].year
    param = Param(method='user.getRecentTracks', period='overall')
    currentYear = datetime.datetime.now().year
    for year in range(earliestScrobbleYear(), currentYear):
        paramYear = Param(method='user.getRecentTracks', period=year, fr=f'{year}-01-01 00:00:00', to=f'{year}-12-31 23:59:59')
        response = getReq(param=paramYear, collapse=False, limit=1)
        numPages = math.ceil(int(response.get('recenttracks').get('@attr').get('total'))/param.lim)
        if numPages != len(paramYear.filePath(glob='*json')): downloadData(paramYear, download=True)
        else: downloadData(paramYear, download=False)
    downloadData(Param(method='user.getRecentTracks', period=currentYear, fr=f'{currentYear}-01-01 00:00:00', to=f'{currentYear}-12-31 23:59:59'))
    mergeRecentTracks(param)

def main():
    # downloadData(Param(method='user.getTopTracks', period='overall'))
    downloadData(Param(method='user.getTopAlbums', period='overall'))
    downloadData(Param(method='user.getTopArtists', period='overall'))
    exportScrobbles()

if __name__== "__main__":
    main()
