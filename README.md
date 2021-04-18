# lastfm-explorer
Python/Pandas wrapper for lastFM API to explore or export user data.

## Usage
```
$ python3 -m downloadLastFM.py
[ERROR] [util.py:62] [Cred()] [Please specify 'username' and 'apikey' in '/path/to/repo/lastfm-explorer/cred.json']
[ERROR] [util.py:63] [Cred()] [A LastFM API key can be obtained from [https://www.last.fm/api/authentication]]
$ cat '/path/to/repo/lastfm-explorer/cred.json'
{
"username": "your_username",
"apikey": "your_api_key"
}
$ python3
>>> from downloadLastFM import Examples
>>> Examples.lovedTracks()
>>> Examples.friends()
>>> Examples.getTopPersonalTag()
>>> Examples.topArtistsCountry('germany')
>>> Examples.trackScrobbles(artist='opeth', track='ghost of perdition')
>>> Examples.monthlyTrackChart(weeksAgo=8, nWeeks=4)
>>> Examples.weeklyAlbumChart(fr='2020-01-01', to='2020-02-01')
>>> Examples.weeklyArtistChart(weeksAgo='20')
>>> Examples.getAlbumDuration(artist='opeth', album='damnation')
>>> Examples.getTopSimilarArtist(artist='opeth')
>>> Examples.findDuplicates()
>>> Examples.earliestListen(query='watershed', entity='album')
```
