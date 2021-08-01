#!/usr/bin/env python3

'''
Explore LastFM user data via multiple LastFM API methods.
'''

from __future__ import annotations # [PEP 563 -- Postponed Evaluation of Annotations](https://www.python.org/dev/peps/pep-0563/)
from typing import List
from apiWrapper import Param, getReq
from download import downloadData
from htmlParse import lastfmNeighbors
from util import dateRange, pandasRead, shiftCols, toUnixTime
import logFormat
import dataclasses, datetime, pandas

def loadUserData(param) -> pandas.DataFrame:
    '''Read user data from disk (download if needed).'''
    try: myData = pandasRead(param=param, inFile=f'{param.filePath()}.{param.outFmt}')
    except FileNotFoundError:
        downloadData(param)
        myData = pandasRead(param=param, inFile=f'{param.filePath()}.{param.outFmt}')
    return myData

def weeklyChart(method:str='user.getWeeklyArtistChart', weeksAgo:int=4, nWeeks:int=1, thr:int=6, **kwargs) -> pandas.DataFrame:
    '''Fetch data for {user.getWeekly*Chart} methods.'''
    (fr,to) = dateRange(weeksAgo=weeksAgo, nWeeks=nWeeks, **kwargs)
    param = Param(method=method, fr=fr, to=to)
    # ts = getReq(Param(method='user.getWeeklyChartList'))[::-1].reset_index() # [user.getWeeklyChartList](https://www.last.fm/api/show/user.getWeeklyChartList)
    # DF = getReq(param=Param(method=method, fr=ts.loc[weeksAgo+nWeeks,'list_from'], to=ts.loc[weeksAgo,'list_to']))
    DF = getReq(param=param)
    return DF[DF[f'{param.splitMethod(plural=False, strip=True)}_playcount'] >= thr]

def recommFromNeighbor(neighbor:str=None, method:str='user.getTopArtists', neighborThr:int=100, myThr:int=1000, **kwargs) -> pandas.DataFrame:
    '''Return neighbor's top artists/albums/songs missing from the user's top listens'''
    if not neighbor: return lastfmNeighbors()
    else:
        myData = loadUserData(Param(method=method)).head(myThr)
        param = Param(method=method, user=neighbor, lim=neighborThr)
        entity = param.splitMethod(lower=True, plural=False, strip=True)
        neighborData = getReq(param)
        cols = [f'{entity}_name', f'{entity}_playcount']
        if entity != 'artist': cols = [f'artist_name', *cols]
        # numpy.setdiff1d(neighborData.get(f'{entity}_name'), myData.get(f'{entity}_name')) # [Compare and find missing strings in pandas Series](https://stackoverflow.com/a/58544291/13019084)
        return neighborData[[item not in myData.get(f'{entity}_name').to_list() for item in neighborData.get(f'{entity}_name').to_list()]][cols]

def recentDiscovery(entity:str='artist', weeksAgo:int=25, nWeeks:int=4, thr:int=10, **kwargs) -> List(str):
    '''Return artist/album/track_name listens that are not present in listening history before query period.'''
    (fr,to) = dateRange(weeksAgo=weeksAgo, nWeeks=nWeeks, **kwargs)
    param = Param(method='user.getRecentTracks', fr=fr, to=to)
    myData = loadUserData(param)
    query = myData[(myData.date_uts > toUnixTime(param.fr)) & (myData.date_uts < toUnixTime(param.to))].get(entity).value_counts()
    query = query[query >= thr].index
    beforeQuery = myData[(myData.date_uts < toUnixTime(param.fr))].get(entity).unique()
    return [item for item in query if item not in beforeQuery]

def forgottenAlbums(earlierYear:int=datetime.datetime.now().year-2, laterYear:int=datetime.datetime.now().year-1, minThr:int=50, maxThr:int=10) -> pandas.DataFrame:
    '''Return albums with many listens during {earlierYear} but few listens during {laterYear}.'''
    def filterAlbumScrobbles(scrobbles:pandas.DataFrame, year:int, thr:int, bound:str):
        yearScrobbles = scrobbles[(scrobbles.date >= f'{year}-01-01') & (scrobbles.date <= f'{year}-12-31')]
        yearAlbumFreq = yearScrobbles[['artist','album']].value_counts() # [Pandas: How to filter results of value_counts?](https://blog.softhints.com/pandas-how-to-filter-results-of-value_counts/)
        if bound == 'lower': yearAlbumFreq = yearAlbumFreq[yearAlbumFreq >= thr]
        if bound == 'upper': yearAlbumFreq = yearAlbumFreq[yearAlbumFreq <= thr]
        return yearAlbumFreq.rename(f'scrobbles{year}').reset_index()
    scrobbles = loadUserData(Param(method='user.getRecentTracks'))
    prev = filterAlbumScrobbles(scrobbles, year=earlierYear, thr=minThr, bound='lower')
    later = filterAlbumScrobbles(scrobbles, year=laterYear, thr=maxThr, bound='upper')
    return pandas.merge(prev, later, on=['artist','album'])

@dataclasses.dataclass
class Examples:
    def getTopArtistTags(artist='opeth', **kwargs): return getReq(param=Param(method='artist.getTopTags'), artist=artist, **kwargs)
    def topArtistsCountry(country:str='spain', **kwargs): return getReq(param=Param(method='geo.getTopArtists', lim=10), country=country, **kwargs)
    def getTopSimilarArtist(artist:str, **kwargs):
        topArtist = getReq(Param(method='user.getTopArtists', period='7day', lim=1)).loc[0,'artist_name'] if not artist else artist
        return getReq(Param(method='artist.getSimilar'), artist=topArtist, **kwargs)
    def getAlbumDuration(artist:str='opeth', album:str='damnation'):
        albumInfo = getReq(Param(method='album.getInfo'), artist=artist, album=album)
        return sum(int(track.get('duration')) for track in albumInfo.get('tracks').get('track')) if not 'error' in albumInfo.keys() else albumInfo
    def getArtistListeners(artist:str='opeth'):
        return int(getReq(Param(method='artist.getInfo'), artist=artist).get('stats').get('listeners'))
    def lovedTracks(): return getReq(Param(method='user.getLovedTracks', lim=20))
    def friends(): return getReq(Param(method='user.getFriends', lim=10))
    def getTopPersonalTag():
        topTags = getReq(Param(method='user.getTopTags'))
        return getReq(param=Param(method='user.getPersonalTags'), tag=topTags.loc[0,'tag_name'], taggingtype='artist')
    def trackScrobbles(artist:str='opeth', track:str='windowpane'): # [there is a new method user.getTrackScrobbles which is just like user.getArtistTracks, except also takes a "track" parameter](https://github.com/pylast/pylast/issues/298#issue-414708387)
        return getReq(Param(method='user.getTrackScrobbles', lim=20), artist=artist, track=track)
    def monthlyTrackChart(weeksAgo:int=4, nWeeks:int=4, **kwargs): return shiftCols(weeklyChart('user.getWeeklyTrackChart', weeksAgo=weeksAgo, nWeeks=nWeeks, **kwargs), ['artist','track_name','track_playcount'])
    def weeklyAlbumChart(weeksAgo:int=1, nWeeks:int=1, **kwargs): return shiftCols(weeklyChart('user.getWeeklyAlbumChart', weeksAgo=weeksAgo, **kwargs), ['artist', 'album_name', 'album_playcount'])
    def weeklyArtistChart(weeksAgo:int=1, nWeeks:int=1, thr:int=10, **kwargs): return shiftCols(weeklyChart('user.getWeeklyArtistChart', **kwargs), ['artist_name','artist_playcount'])
    def findDuplicateScrobbles(year:int=datetime.datetime.now().year, thr:int=600):
        recentTracks = loadUserData(Param(method='user.getRecentTracks', period=year))
        return recentTracks[recentTracks.groupby('track_name')['date_uts'].diff().abs().fillna(thr+1) < thr] # [https://stackoverflow.com/a/44779167/13019084]
    def earliestListen(query:str, entity:str='artist'):
        myData = loadUserData(Param(method='user.getRecentTracks'))
        matches = myData[myData.get(entity).str.contains(query, case=False)]
        if len(matches): return matches.get('date').iloc[-1]
