#!/usr/bin/env python3

'''
Explore LastFM user data via multiple LastFM API methods.
Exports lastFM data as JSON files and merge them into a flat pandas.DataFrame.
'''

# to do:
    # exception handler (hide traceback and keep process alive) based on logging level?
    # determine if pagination is needed and set 'writeToDisk' flag in U.flattenDF() accordingly?

# [Last.fm API Introduction](https://www.last.fm/api/intro)
# [Tutorial: Getting Music Data with the Last.fm API using Python](https://www.dataquest.io/blog/last-fm-api-python/)
# [Analyzing Last.fm Listening History](https://geoffboeing.com/2016/05/analyzing-lastfm-history/)

from __future__ import annotations # [https://www.python.org/dev/peps/pep-0563/]
import typing as T # [https://realpython.com/python-type-checking/]
import util as U
import htmlParse as H
import dataclasses, datetime, enlighten, io, json, logging, math, pandas, pathlib, requests, sys, time


@dataclasses.dataclass
class Param:
    '''Set API parameters.'''
    user:str = U.Cred.user
    apiKey:str = U.Cred.apiKey
    method:str = None
    period:T.Union[str,int] = 'overall' # ['overall', '7day', '1month', '3month', '6month', '12month']
    fmt:str = 'json'
    lim:int = 1000
    fr:T.Union[str,int] = None
    to:T.Union[str,int] = None
    extended:int = 0 # Includes more artist data (artist_url, artist_images, track_loved) when calling user.getRecentTracks, but it strips artist_mbid for some reason.
    page:int = 1
    nPages:int = 1
    sleep:float = 0.2 # [Rate limit copied from pylast since it is not explicitly mentioned in the API TOS](https://github.com/pylast/pylast/blob/master/src/pylast/__init__.py#L115)
    outFmt:str = 'feather' # [The Best Format to Save Pandas Data](https://towardsdatascience.com/the-best-format-to-save-pandas-data-414dca023e0d)

    def __post_init__(self):
        if not self.method:
            logging.error(f'Available LastFM API methods:')
            availableMethods = H.apiDocs()
            logging.error(f"For more info/documentation, run:\n>>> H.apiDocs('api.method')")
            sys.exit()

    def requestParams(self, **kwargs) -> T.Dict[str,T.Union[str,int]]:
        '''Configure API request parameters.'''
        rParams  = {'method':self.method, 'user':self.user, 'api_key':self.apiKey, 'period':self.period, \
                    'limit':self.lim, 'page':self.page, 'format':self.fmt, 'extended':self.extended}
        if self.method not in ['user.getTopArtists', 'user.getTopAlbums', 'user.getTopTracks']: _ = rParams.pop('period')
        if self.fr: rParams = {**rParams, 'from':U.toUnixTime(dt=self.fr, log=True)}
        if self.to: rParams = {**rParams, 'to':U.toUnixTime(dt=self.to, log=True)}
        if (rParams.get('from')) and (rParams.get('to')) and (rParams.get('from') > rParams.get('to')):
            logging.error(f"Please make sure the 'from' timestamp ({rParams.get('from')}) corresponds to a time before the 'to' timestamp ({rParams.get('to')})")
        return {**rParams, **kwargs}

    def splitMethod(self, plural:bool=True, lower=False, strip=False) -> str:
        '''Split {method} at the '.', strip 'get', strip trailing 's' if {plural} is True, convert to lowercase if {lower} is True, and strip {substr} if {strip} is True'''
        method = self.method.lower() if lower else self.method
        (_,method) = method.split('.')
        method = method.replace('get','') if plural else method.replace('get','').rstrip('s')
        # if sys.version_info < (3,8): if strip: for substr in ['add','chart','loved','personal','recent','scrobble','remove','top','weekly']: method = method.lower().replace(substr, '')
        if strip: [(method := method.lower().replace(substr, '')) for substr in ['add','chart','loved','personal','recent','scrobble','remove','top','weekly']] # [https://stackoverflow.com/a/55889140/13019084]
        return method

    def filePath(self, glob:str=None, ext:str='', reverse:bool=False, **kwargs) -> T.Union[str,T.List[str]]:
        '''Return path for output files.'''
        method = self.splitMethod(self)
        period = kwargs.get('period', self.period)
        filepath = f"{method}/{self.user}.{method}.{period}{ext}"
        if glob: return sorted(pathlib.Path.cwd().glob(f'{filepath}{glob}'), reverse=reverse)
        else: return pathlib.Path.cwd().joinpath(f'{filepath}')


def getReq(param:Param, pbarManager:enlighten._manager.Manager=enlighten.get_manager(enabled=False), collapse:bool=True, **kwargs) -> T.Dict[str,T.Any]:
    '''Fetch request with optional enlighten progress bar. Additional request parameters may be provided via {kwargs}'''
    # [https://stackoverflow.com/a/63832993/13019084]
    endpoint = 'http://ws.audioscrobbler.com/2.0/'
    header = {'User-Agent': 'delannoy/0.0.1 (a@delannoy.cc)'}
    paramInfo = f"{param.filePath().name.replace('.', '|')}|{param.page:04d}"
    attempts = 0
    with requests.get(url=endpoint, headers=header, params=param.requestParams(**kwargs), stream=True) as response:
        while response.status_code != requests.codes.ok: # and response.json().get('code') in [8, 16]:
            attempts += 1
            logging.warning(f"Query failed :'( Trying again... [{attempts} attempt(s)]\n{response.request.url}\n{response.json()}")
            # if 'Invalid Method' in response.json().get('message'): break
            if attempts >= 10: break
            time.sleep(param.sleep)
            response = requests.get(url=endpoint, headers=header, params=param.requestParams(**kwargs), stream=True)
        logging.debug(f'{response.status_code}: {response.request.url}')
        total = int(response.headers.get('content-length', 0))
        chkSize = 2**10
        data = io.BytesIO()
        with pbarManager.counter(color='green', total=math.ceil(total/chkSize), desc=paramInfo, unit='KiB', leave=False) as pbar:
            for chunk in response.iter_content(chunk_size=chkSize):
                data.write(chunk)
                pbar.update()
    resp = json.loads(data.getvalue())
    data.close()
    if collapse: resp = U.collapseResp(resp=resp, returnDF=True, param=param)
    return resp

def downloadData(param:Param, download:bool=True):
    '''Download lastFM data for the given {param.method} and {param.period} to json files, merge them into a flat pandas.DataFrame, and write it to disk'''
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
                pbar.total = param.nPages # [https://stackoverflow.com/a/58961015/13019084]
                pbar.update()
                param.filePath().parent.mkdir(exist_ok=True)
                with open(file=fileName, mode='w') as jsonF: json.dump(obj=response, fp=jsonF)
                param.page += 1
                time.sleep(param.sleep)
        pbarManager.stop()
    DF = U.loadJSON(param)
    df = U.flattenDF(param=param, DF=DF, writeToDisk=True)
    if param.splitMethod() in ['TopArtists','TopAlbums','TopTracks']: U.writeCSV(param=param, df=df)

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
    U.mergeRecentTracks(param)

def loadUserData(param):
    try: myData = U.pandasRead(param=param, inFile=f'{param.filePath()}.{param.outFmt}')
    except FileNotFoundError:
        downloadData(param)
        myData = U.pandasRead(param=param, inFile=f'{param.filePath()}.{param.outFmt}')
    return myData

def weeklyChart(method:str='user.getWeeklyArtistChart', weeksAgo:int=4, nWeeks:int=1, thr:int=6, **kwargs) -> pandas.DataFrame:
    '''Fetch data for {user.getWeekly*Chart} methods.'''
    (fr,to) = U.dateRange(weeksAgo=weeksAgo, nWeeks=nWeeks, **kwargs)
    param = Param(method=method, fr=fr, to=to)
    # ts = getReq(Param(method='user.getWeeklyChartList'))[::-1].reset_index() # [https://www.last.fm/api/show/user.getWeeklyChartList]
    # DF = getReq(param=Param(method=method, fr=ts.loc[weeksAgo+nWeeks,'list_from'], to=ts.loc[weeksAgo,'list_to']))
    DF = getReq(param=param)
    return DF[DF[f'{param.splitMethod(plural=False, strip=True)}_playcount'] >= thr]

def recommFromNeighbor(neighbor:str=None, method:str='user.getTopArtists', neighborThr:int=100, myThr:int=1000, **kwargs):
    if not neighbor: return H.lastfmNeighbors()
    else:
        myData = loadUserData(Param(method=method)).head(myThr)
        param = Param(method=method, user=neighbor, lim=neighborThr)
        entity = param.splitMethod(lower=True, plural=False, strip=True)
        neighborData = getReq(param)
        cols = [f'{entity}_name', f'{entity}_playcount']
        if entity != 'artist': cols = [f'artist_name', *cols]
        # numpy.setdiff1d(neighborData.get(f'{entity}_name'), myData.get(f'{entity}_name')) # [https://stackoverflow.com/a/58544291/13019084]
        return neighborData[[item not in myData.get(f'{entity}_name').to_list() for item in neighborData.get(f'{entity}_name').to_list()]][cols]

def recentDiscovery(entity:str='artist', weeksAgo:int=10, nWeeks:int=4, thr:int=10, **kwargs):
    (fr,to) = U.dateRange(weeksAgo=weeksAgo, nWeeks=nWeeks, **kwargs)
    param = Param(method='user.getRecentTracks', fr=fr, to=to)
    myData = loadUserData(param)
    query = myData[(myData.date_uts > U.toUnixTime(param.fr)) & (myData.date_uts < U.toUnixTime(param.to))].get(entity).unique()
    beforeQuery = myData[(myData.date_uts < U.toUnixTime(param.fr))].get(entity).unique()
    return [item for item in query if item not in beforeQuery]

@dataclasses.dataclass
class Examples:
    def getTopArtistTags(artist='opeth', **kwargs): return getReq(param=Param(method='artist.getTopTags'), artist=artist, **kwargs)
    def topArtistsCountry(country:str='spain', **kwargs): return getReq(param=Param(method='geo.getTopArtists', lim=10), country=country, **kwargs)
    def getTopSimilarArtist(artist:str, **kwargs):
        topArtist = getReq(Param(method='user.getTopArtists', period='7day', lim=1)).loc[0,'artist_name'] if not artist else artist
        logging.info(f"Similar artists to '{topArtist}':")
        return getReq(Param(method='artist.getSimilar'), artist=topArtist, **kwargs)
    def getAlbumDuration(artist:str='opeth', album:str='damnation'):
        albumInfo = getReq(Param(method='album.getInfo'), artist=artist, album=album)
        return sum(int(track.get('duration')) for track in albumInfo.get('tracks').get('track')) if not 'error' in albumInfo.keys() else albumInfo
    def lovedTracks(): return getReq(Param(method='user.getLovedTracks', lim=20))
    def friends(): return getReq(Param(method='user.getFriends', lim=10))
    def getTopPersonalTag():
        topTags = getReq(Param(method='user.getTopTags'))
        return getReq(param=Param(method='user.getPersonalTags'), tag=topTags.loc[0,'tag_name'], taggingtype='artist')
    def trackScrobbles(artist:str='opeth', track:str='windowpane'): # [https://github.com/pylast/pylast/issues/298]
        return getReq(Param(method='user.getTrackScrobbles', lim=20), artist=artist, track=track)
    def monthlyTrackChart(weeksAgo:int=4, nWeeks:int=4, **kwargs): return weeklyChart('user.getWeeklyTrackChart', weeksAgo=weeksAgo, nWeeks=nWeeks, **kwargs)
    def weeklyAlbumChart(weeksAgo:int=1, nWeeks:int=1, **kwargs): return weeklyChart('user.getWeeklyAlbumChart', weeksAgo=weeksAgo, **kwargs)[['artist', 'album_name', 'album_playcount']]
    def weeklyArtistChart(weeksAgo:int=1, nWeeks:int=1, thr:int=10, **kwargs): return weeklyChart('user.getWeeklyArtistChart', **kwargs)
    def findDuplicateScrobbles(year:int=datetime.datetime.now().year, thr:int=600):
        recentTracks = loadUserData(Param(method='user.getRecentTracks', period=year))
        return recentTracks[recentTracks.groupby('track_name')['date_uts'].diff().abs().fillna(thr+1) < thr] # [https://stackoverflow.com/a/44779167/13019084]
    def earliestListen(query:str, entity:str='artist'):
        myData = loadUserData(Param(method='user.getRecentTracks'))
        matches = myData[myData.get(entity).str.contains(query, case=False)]
        if len(matches): return matches.get('date').iloc[-1]


def main():
    # downloadData(Param(method='user.getTopTracks', period='overall'))
    downloadData(Param(method='user.getTopAlbums', period='overall'))
    downloadData(Param(method='user.getTopArtists', period='overall'))
    exportScrobbles()

if __name__== "__main__":
    main()
