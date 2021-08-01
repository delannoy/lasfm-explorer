#!/usr/bin/env python3

from __future__ import annotations # [PEP 563 -- Postponed Evaluation of Annotations](https://www.python.org/dev/peps/pep-0563/)
from htmlParse import apiDocs
from util import Cred, collapseResp, toUnixTime
import dataclasses, enlighten, io, json, logging, math, pathlib, requests, sys, time

# [Last.fm API Introduction](https://www.last.fm/api/intro)
# [Tutorial: Getting Music Data with the Last.fm API using Python](https://www.dataquest.io/blog/last-fm-api-python/)
# [Analyzing Last.fm Listening History](https://geoffboeing.com/2016/05/analyzing-lastfm-history/)

# to do:
    # exception handler (hide traceback and keep process alive) based on logging level?
    # determine if pagination is needed and set 'writeToDisk' flag in flattenDF() accordingly?


@dataclasses.dataclass
class Param:
    user:str = Cred.user
    apiKey:str = Cred.apiKey
    method:str = None
    period:Union[str,int] = 'overall' # ['overall', '7day', '1month', '3month', '6month', '12month']
    fmt:str = 'json'
    lim:int = 1000
    fr:Union[str,int] = None
    to:Union[str,int] = None
    extended:int = 0 # Includes more artist data (artist_url, artist_images, track_loved) when calling user.getRecentTracks, but it strips artist_mbid for some reason.
    page:int = 1
    nPages:int = 1
    sleep:float = 0.2 # [Rate limit copied from pylast since it is not explicitly mentioned in the API TOS](https://github.com/pylast/pylast/blob/master/src/pylast/__init__.py#L115)
    outFmt:str = 'feather' # [The Best Format to Save Pandas Data](https://towardsdatascience.com/the-best-format-to-save-pandas-data-414dca023e0d)

    def __post_init__(self):
        '''Query all available API methods if one is not provided when class is instantiated.'''
        if not self.method:
            logging.error(f'Available LastFM API methods:')
            availableMethods = apiDocs()
            logging.error(f'For more info/documentation, run:')
            logging.error('>>> import htmlParse; htmlParse.apiDocs(api.method)')
            sys.exit()

    def requestParams(self, **kwargs) -> Dict[str,Union[str,int]]:
        '''Configure API request parameters.'''
        rParams  = {'method':self.method, 'user':self.user, 'api_key':self.apiKey, 'period':self.period, \
                    'limit':self.lim, 'page':self.page, 'format':self.fmt, 'extended':self.extended}
        if self.method not in ['user.getTopArtists', 'user.getTopAlbums', 'user.getTopTracks']: _ = rParams.pop('period')
        if self.fr: rParams = {**rParams, 'from':toUnixTime(dt=self.fr, log=True)}
        if self.to: rParams = {**rParams, 'to':toUnixTime(dt=self.to, log=True)}
        if (rParams.get('from')) and (rParams.get('to')) and (rParams.get('from') > rParams.get('to')):
            logging.error(f"Please make sure the 'from' timestamp ({rParams.get('from')}) corresponds to a time before the 'to' timestamp ({rParams.get('to')})")
        return {**rParams, **kwargs}

    def splitMethod(self, plural:bool=True, lower=False, strip=False) -> str:
        '''Split {method} at the '.' and strip 'get'. If {plural} is False, strip trailing 's'. If {lower} is True, convert to lowercase. If {strip} is True, strip {substr}.'''
        method = self.method.lower() if lower else self.method
        (_,method) = method.split('.')
        method = method.replace('get','') if plural else method.replace('get','').rstrip('s')
        # if sys.version_info < (3,8): if strip: for substr in ['add','chart','loved','personal','recent','scrobble','remove','top','weekly']: method = method.lower().replace(substr, '')
        if strip: [(method := method.lower().replace(substr, '')) for substr in ['add','chart','loved','personal','recent','scrobble','remove','top','weekly']] # [How to replace multiple substrings of a string?](https://stackoverflow.com/a/55889140/13019084)
        return method

    def filePath(self, glob:str=None, ext:str='', reverse:bool=False, **kwargs) -> Union[str,List[str]]:
        '''Output file path. If {glob} is True, return list of matching files.'''
        method = self.splitMethod(self)
        period = kwargs.get('period', self.period)
        filepath = f"{method}/{self.user}.{method}.{period}{ext}"
        if glob: return sorted(pathlib.Path.cwd().glob(f'{filepath}{glob}'), reverse=reverse)
        else: return pathlib.Path.cwd().joinpath(f'{filepath}')


def getReq(param:Param, pbarManager:enlighten._manager.Manager=enlighten.get_manager(enabled=False), collapse:bool=True, **kwargs) -> Dict[str,Any]:
    '''Fetch request with optional enlighten progress bar. Additional request parameters may be provided via {kwargs}.'''
    # [Progress Bar while download file over http with Requests](https://stackoverflow.com/a/63832993/13019084)
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
    if collapse: resp = collapseResp(resp=resp, returnDF=True, param=param)
    return resp
