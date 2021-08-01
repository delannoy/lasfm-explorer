#!/usr/bin/env python3

from __future__ import annotations # [PEP 563 -- Postponed Evaluation of Annotations](https://www.python.org/dev/peps/pep-0563/)
from typing import Any, Callable, Dict, List, Union
import datetime, dateutil, functools, itertools, json, logging, pandas, pathlib, sys, timeit


class Cred:
    '''Fetch user data from json file.'''
    filePath:str = f"{pathlib.Path.cwd().joinpath('user.json')}"
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


def timer(func:Callable) -> Callable:
    '''Timer decorator. Logs execution time for functions.'''
    # [Primer on Python Decorators](https://realpython.com/primer-on-python-decorators/)
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        t0      = timeit.default_timer()
        value   = func(*args, **kwargs)
        t1      = timeit.default_timer()
        logging.debug(f'{func.__name__}(): {t1-t0:.6f} s')
        return value
    return wrapper

def toUnixTime(dt:Union[str,int], log:bool=False, **kwargs) -> int:
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

def collapseResp(resp:Dict[str,Any], ignoreKey:string='@attr', returnDF:bool=False, **kwargs) -> List[Dict[str,Any]]:
    '''Traverse single keys in nested dictionary (ignoring {ignoreKey}) until reaching a list or muti-key dict.'''
    def collapseOnlyKey(resp:Dict[str,Any]) -> Dict[str,Any]:
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
    # [Intermission: Flattening A List of Lists](https://realpython.com/python-itertools/#intermission-flattening-a-list-of-lists)
    # if sys.version_info < (3,8): jsonFiles = param.filePath(glob='*json'); if jsonFiles: jsonListData = [json.load(open(file)) for file in jsonFiles]
    if (jsonFiles := param.filePath(glob='*json')): jsonListData = [json.load(open(file)) for file in jsonFiles]
    else: sys.exit(logging.error(f"No files found matching {param.filePath(ext='*json')}"))
    flatListData = itertools.chain.from_iterable(collapseResp(data) for data in jsonListData)
    return pandas.DataFrame(flatListData)

def flattenCol(dfCol:pandas.Series, prefix:str=None) -> pandas.DataFrame:
    '''Flatten {dfCol} (pandas.Series) as needed and prepend {prefix} to {dfCol.name} (series/column name). Convert elements to integer if possible.'''
    def fillNan(dfCol:pandas.Series, obj:Union[list,dict]): return dfCol.fillna({i: obj for i in dfCol.index}) # [How to fill dataframe Nan values with empty list [] in pandas?](https://stackoverflow.com/a/62689667/13019084)
    def concatFlatCols(df:pandas.DataFrame): return pandas.concat(objs=[flattenCol(df[col]) for col in df], axis=1)
    if any(isinstance(row, list) for row in dfCol):
        # if dfCol contains list entries, fill any None/Nan values with empty list, flatten via dfCol.values.tolist(), and prepend {dfCol.name} to each column name
        dfCol = fillNan(dfCol=dfCol, obj=[])
        listDF = pandas.concat(objs=[pandas.DataFrame(dfCol.values.tolist()).add_prefix(f'{dfCol.name}_')], axis=1) # [DataFrame Pandas - Flatten column of lists to multiple columns](https://stackoverflow.com/a/44821357/13019084)
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

def shiftCols(df:pandas.DataFrame, firstCols=List[int]) -> pandas.Dataframe:
    '''Shift {firstCols} to be left-most in {df}'''
    return df[firstCols + [col for col in df.columns if col not in firstCols]]

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
    return getattr(pandas, f'read_{param.outFmt}')(inFile) # [Calling a function of a module by using its name (a string)](https://stackoverflow.com/a/3071/13019084)

def pandasWrite(param, df:pandas.DataFrame, outFile:str):
    '''Write {df} to disk in {fmt} format.'''
    outFile.unlink(missing_ok=True)
    getattr(df, f'to_{param.outFmt}')(outFile) # [Calling a function of a module by using its name (a string)](https://stackoverflow.com/a/3071/13019084)

@timer
def writeCSV(param, df:pandas.DataFrame):
    '''Write subset of dataframe columns to csv.'''
    subMethod = param.splitMethod()
    # if sys.version_info < (3,8): outFile = param.filePath(ext='.csv')); outFile.unlink(missing_ok=True)
    (outFile := param.filePath(ext='.csv')).unlink(missing_ok=True)
    if (subMethod == 'TopArtists'):
        df.to_csv(path_or_buf=outFile, columns=['artist_playcount','artist_mbid','artist_name'], sep='|', header=True, index=False)
    elif (subMethod == 'TopAlbums'):
        df.to_csv(path_or_buf=outFile, columns=['album_playcount','artist_mbid','album_mbid','artist_name','album_name'], sep='|', header=True, index=False)
    elif (subMethod == 'TopTracks'):
        df.to_csv(path_or_buf=outFile, columns=['track_playcount','artist_mbid','track_mbid','artist_name','track_name'], sep='|', header=True, index=False)
