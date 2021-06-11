#!/usr/bin/env python3

from __future__ import annotations # [https://www.python.org/dev/peps/pep-0563/]
import typing as T # [https://realpython.com/python-type-checking/]
import datetime, dateutil, functools, itertools, json, logging, os, pandas, pathlib, sys, timeit


class C:
    '''Manage text format and text via tput'''
    # [https://stackoverflow.com/a/287944/13019084]
    # [https://janakiev.com/blog/python-shell-commands/]
    # [https://www.gnu.org/software/termutils/manual/termutils-2.0/html_chapter/tput_1.html]
    reset = os.popen('tput sgr 0 0').read() # Turn off all attributes
    bold = os.popen('tput bold').read() # Begin double intensity mode
    uline = os.popen('tput smul').read() # Begin underscore mode
    class F: # foreground
        black, red, green, yellow, blue, magenta, cyan, white = [os.popen(f'tput setaf {c}').read() for c in range(0,8)]
        grey, lred, lgreen, lyellow, lblue, lmagenta, lcyan, lwhite = [os.popen(f'tput setaf {c}').read() for c in range(8,16)]
    class B: # background
        black, red, green, yellow, blue, magenta, cyan, white = [os.popen(f'tput setab {c}').read() for c in range(0,8)]
        grey, lred, lgreen, lyellow, lblue, lmagenta, lcyan, lwhite = [os.popen(f'tput setab {c}').read() for c in range(8,16)]


class LogFmt(logging.Formatter):
    '''Custom logging formatter with color.'''
    # [https://docs.python.org/3/howto/logging-cookbook.html#customized-exception-formatting]
    # [https://stackoverflow.com/a/56944256/13019084]
    FORMATS = {
        logging.DEBUG: f'{C.F.grey}[%(levelname)s] [%(message)s]{C.reset}',
        logging.INFO: f'{C.F.grey}%(message)s{C.reset}',
        logging.WARNING: f'{C.F.yellow}%(message)s{C.reset}',
        logging.ERROR: f'{C.F.red}[%(levelname)s] [%(filename)s:%(lineno)d] [%(funcName)s()] [%(message)s]{C.reset}',
        logging.CRITICAL: f'{C.B.red}{C.F.black}[%(levelname)s] [%(filename)s:%(lineno)d] [%(funcName)s()] [%(message)s]{C.reset}'
    }
    def format(self, record):
        logFmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(logFmt)
        return formatter.format(record)


def logConfig(level:str='INFO'):
    log = logging.getLogger()
    handler = logging.StreamHandler()
    handler.setFormatter(LogFmt())
    log.addHandler(handler)
    log.setLevel(level)

logConfig(level='DEBUG')
logging.getLogger('urllib3').setLevel(logging.INFO) # [https://stackoverflow.com/a/11029841/13019084]


class Cred:
    '''Fetch user data from json file.'''
    filePath:str = f"{pathlib.Path.cwd().joinpath('cred.json')}"
    try:
        with open(file=filePath, mode='r') as jsonFile: credData = json.load(jsonFile)
        user = credData.get('username')
        apiKey = credData.get('apikey')
        if user == 'your_username' or apiKey == 'your_api_key': raise Exception
    except (FileNotFoundError, Exception):
        with open(file=filePath, mode='w') as jsonFile: jsonFile.write('{\n"username": "your_username",\n"apikey": "your_api_key"\n}')
        logging.error(f"Please specify 'username' and 'apikey' in '{filePath}'")
        logging.error(f"A LastFM API key can be obtained from [https://www.last.fm/api/authentication]")
        sys.exit()


def timer(func:T.Callable) -> T.Callable:
    '''Timer decorator. Logs execution time for functions.'''
    # [https://realpython.com/primer-on-python-decorators/]
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        t0      = timeit.default_timer()
        value   = func(*args, **kwargs)
        t1      = timeit.default_timer()
        logging.debug(f'{func.__name__}(): {t1-t0:.6f} s')
        return value
    return wrapper

def toUnixTime(dt:T.Union[str,int], log:bool=False, **kwargs) -> int:
    '''Convert {dt} (assumes UTC) to unix time.'''
    if isinstance(dt, str): dt = int(dateutil.parser.parse(str(dt)).replace(tzinfo=dateutil.tz.UTC).timestamp())
    if isinstance(dt, datetime.datetime): dt = int(dt.replace(tzinfo=dateutil.tz.UTC).timestamp())
    if log: logging.debug(fromUnixTime(dt))
    return dt

def fromUnixTime(ts:int) -> str:
    '''Convert {ts} unix timestamp (assumes UTC) to datetime string.'''
    return datetime.datetime.utcfromtimestamp(ts).strftime('%Y-%m-%d %H:%M:%S')

def dateRange(weeksAgo:int, nWeeks:int, **kwargs) -> int:
    '''Handle date range timestamps. Prioritizes {to} and {fr} if present in {kwargs}.'''
    now = datetime.datetime.now()
    if 'fr' in kwargs: fr = toUnixTime(dt=kwargs.get('fr'), **kwargs)
    else: fr = toUnixTime(dt=(now - datetime.timedelta(weeks=weeksAgo)), **kwargs)
    if 'to' in kwargs:
        if kwargs.get('to') == -1: to = toUnixTime(dt=now, **kwargs)
        else: to = toUnixTime(dt=kwargs.get('to'), **kwargs)
    else:
        if nWeeks == -1: to = toUnixTime(dt=now, **kwargs)
        else: to = toUnixTime(dt=(datetime.datetime.utcfromtimestamp(fr) + datetime.timedelta(weeks=nWeeks)), **kwargs)
    return (fr,to)

def collapseResp(resp:T.Dict[str,T.Any], ignoreKey:string='@attr', returnDF:bool=False, **kwargs) -> T.List[T.Dict[str,T.Any]]:
    '''Traverse single keys in nested dictionary (ignoring {ignoreKey}) until reaching a list or muti-key dict.'''
    def collapseOnlyKey(resp:T.Dict[str,T.Any]) -> T.Dict[str,T.Any]:
        '''Return the contents of a dict if it has only one key.'''
        return resp.get(list(resp.keys())[0]) if len(resp.keys()) == 1 else resp
    while isinstance(resp, dict):
        if ignoreKey in resp.keys(): attr = resp.pop(ignoreKey) # toss resp['@attr'] into the trash (contains user and pagination info)
        resp = collapseOnlyKey(resp)
        if isinstance(resp, list):
            if returnDF: resp = flattenDF(param=kwargs.get('param'), DF=pandas.DataFrame(resp), writeToDisk=False)
            break
        if len(resp.keys()) > 1 and ignoreKey not in resp: break
    return resp

@timer
def loadJSON(param) -> pandas.DataFrame:
    '''Append json data from files into a list of lists, then flatten the list, and return as a pandas.DataFrame.'''
    # [https://realpython.com/python-itertools/#intermission-flattening-a-list-of-lists]
    # if sys.version_info < (3,8): jsonFiles = param.filePath(glob='*json'); if jsonFiles: jsonListData = [json.load(open(file)) for file in jsonFiles]
    if (jsonFiles := param.filePath(glob='*json')): jsonListData = [json.load(open(file)) for file in jsonFiles]
    else: sys.exit(logging.error(f"No files found matching {param.filePath(ext='*json')}"))
    flatListData = itertools.chain.from_iterable(collapseResp(data) for data in jsonListData)
    return pandas.DataFrame(flatListData)

def flattenCol(dfCol:pandas.Series, prefix:str=None) -> pandas.DataFrame:
    '''Flatten {dfCol} (pandas.Series) as needed and prepend {prefix} to {dfCol.name} (series/column name). Convert elements to integer if possible.'''
    def fillNan(dfCol:pandas.Series, obj:T.Union[list,dict]): return dfCol.fillna({i: obj for i in dfCol.index}) # [https://stackoverflow.com/a/62689667/13019084]
    def concatFlatCols(df:pandas.DataFrame): return pandas.concat(objs=[flattenCol(df[col]) for col in df], axis=1)
    if any(isinstance(row, list) for row in dfCol):
        # if dfCol contains list entries, fill any None/Nan values with empty list, flatten via dfCol.values.tolist(), and prepend {dfCol.name} to each column name
        dfCol = fillNan(dfCol=dfCol, obj=[])
        listDF = pandas.concat(objs=[pandas.DataFrame(dfCol.values.tolist()).add_prefix(f'{dfCol.name}_')], axis=1) # [https://stackoverflow.com/a/44821357/13019084]
        return concatFlatCols(listDF)
    elif any(isinstance(row, dict) for row in dfCol):
        # if dfCol contains dict entries, fill any None/Nan values with empty dict, flatten via pandas.json_normalize(), and prepend {dfCol.name} to each column name
        dfCol = fillNan(dfCol=dfCol, obj={})
        dictDF = pandas.json_normalize(dfCol).add_prefix(f'{dfCol.name}_')
        return concatFlatCols(dictDF)
    else:
        dfCol = pandas.to_numeric(arg=dfCol, errors='ignore')
        return dfCol.rename(f'{prefix}_{dfCol.name}') if prefix else dfCol

@timer
def flattenDF(param, DF:pandas.DataFrame, writeToDisk:bool=True) -> pandas.DataFrame:
    '''Flatten all columns in {DF}, apply pandas.Timestamp dtype if applicable, and write to disk.'''
    DF = DF[DF['@attr'] != {'nowplaying': 'true'}].reset_index(drop=True).drop(columns=['@attr']) if '@attr' in DF else DF # drop 'nowplaying' rows and '@attr' column (first entry in every 'RecentTracks' page response)
    flatDF = pandas.concat(objs=[flattenCol(DF[col], prefix=param.splitMethod(plural=False, strip=True)) for col in DF.columns], axis=1) # .fillna('')
    flatDF.columns = [col.replace('_#text','').replace('@attr_','') for col in flatDF.columns]
    if 'date' in flatDF: flatDF['date'] = pandas.to_datetime(arg=flatDF['date'], format='%d %b %Y, %H:%M', utc=True)
    if writeToDisk: pandasWrite(param=param, df=flatDF, outFile=param.filePath(ext=f'.{param.outFmt}'))
    return flatDF

@timer
def mergeRecentTracks(param):
    '''Merge individual-year {RecentTracks} serialized files into a single "overall" file.'''
    # if sys.version_info < (3,8): outFile = param.filePath(ext=f'.{param.outFmt}'); outFile.unlink(missing_ok=True)
    (outFile := param.filePath(ext=f'.{param.outFmt}')).unlink(missing_ok=True)
    inFiles = param.filePath(period='', glob=f'*.{param.outFmt}', reverse=True)
    df = pandas.concat(objs=[pandasRead(param, f) for f in inFiles], ignore_index=True)
    pandasWrite(param=param, df=df, outFile=outFile)

def pandasRead(param, inFile:str) -> pandas.DataFrame:
    '''Read {inFile} and return as a pandas.DataFrame.'''
    return getattr(pandas, f'read_{param.outFmt}')(inFile) # [https://stackoverflow.com/a/3071/13019084]

def pandasWrite(param, df:pandas.DataFrame, outFile:str):
    '''Write {df} to disk in {fmt} format.'''
    outFile.unlink(missing_ok=True)
    getattr(df, f'to_{param.outFmt}')(outFile) # [https://stackoverflow.com/a/3071/13019084]

def loadUserData(param) -> pandas.DataFrame:
    '''Read user data from disk (download if needed).'''
    try: myData = pandasRead(param=param, inFile=f'{param.filePath()}.{param.outFmt}')
    except FileNotFoundError:
        downloadData(param)
        myData = pandasRead(param=param, inFile=f'{param.filePath()}.{param.outFmt}')
    return myData

@timer
def writeCSV(param, df:pandas.DataFrame):
    '''Write selected dataframe columns to csv.'''
    subMethod = param.splitMethod()
    # if sys.version_info < (3,8): outFile = param.filePath(ext='.csv')); outFile.unlink(missing_ok=True)
    (outFile := param.filePath(ext='.csv')).unlink(missing_ok=True)
    if (subMethod == 'TopArtists'):
        df.to_csv(path_or_buf=outFile, columns=['artist_playcount','artist_mbid','artist_name'], sep='|', header=True, index=False)
    elif (subMethod == 'TopAlbums'):
        df.to_csv(path_or_buf=outFile, columns=['album_playcount','artist_mbid','album_mbid','artist_name','album_name'], sep='|', header=True, index=False)
    elif (subMethod == 'TopTracks'):
        df.to_csv(path_or_buf=outFile, columns=['track_playcount','artist_mbid','track_mbid','artist_name','track_name'], sep='|', header=True, index=False)
