# lastfm-explorer
Python/Pandas wrapper for lastFM API to explore and/or export user data.

## setup
A LastFM API key is required for most API methods (can be obtained [here](https://www.last.fm/api/authentication)).
The `main()` function exports user data (`TopAlbums`, `TopArtists`, and all scrobble data using `RecentTracks`).
```
$ python3 -m downloadLastFM
[ERROR] [util.py:62] [Cred()] [Please specify 'username' and 'apikey' in '/path/to/repo/lastfm-explorer/cred.json']
[ERROR] [util.py:63] [Cred()] [A LastFM API key can be obtained from [https://www.last.fm/api/authentication]]

$ cat '/path/to/repo/lastfm-explorer/cred.json'
{
"username": "your_username",
"apikey": "your_api_key"
}
```

## usage examples
```
>>> from downloadLastFM import Examples

>>> Examples.getAlbumDuration(artist='opeth', album='damnation')
3124

>>> Examples.getTopArtistTags(artist='the contortionist')[['tag_count', 'tag_name']].head(4)
   tag_count               tag_name
0        100              deathcore
1         90  Progressive deathcore
2         71      Progressive metal
3         50           experimental

>>> Examples.getTopSimilarArtist(artist='rivers of nihil', limit=4)[['similar_name', 'similar_mbid', 'similar_match']]
           similar_name                          similar_mbid  similar_match
0              Fallujah  54fc6a93-57bb-4192-a4cb-c5850d64afd2       1.000000
1  Black Crown Initiate  a33bc9b0-6b88-4593-a812-6124b7368361       0.992736
2       Beyond Creation  27a11ee4-9fcd-4834-978e-10f60faae646       0.939188
3             Allegaeon  1d71cfe3-f105-4dd5-bdfe-61f6fde2cac7       0.905205

>>> Examples.topArtistsCountry(country='germany', limit=4)[['artist_name', 'artist_listeners', 'artist_mbid']]
             artist_name  artist_listeners                           artist_mbid
0                  Queen           4473635  420ca290-76c5-41af-999e-564d7c71f1a7
1               Coldplay           5829011  cc197bad-dc9c-440d-a5b5-d52ba2e14234
2            David Bowie           3690398  5441c29d-3602-4898-b1a1-b77fa23b8e50
3  Red Hot Chili Peppers           4941475  8bfac288-ccc5-448d-9573-c33ea2aa5c30
```

## more examples
```python
from downloadLastFM import Examples
Examples.monthlyTrackChart(weeksAgo=8)
Examples.weeklyAlbumChart(fr='2020-01-01', to='2020-02-01')
Examples.weeklyArtistChart(weeksAgo='20', nWeeks=4)
Examples.trackScrobbles(artist='opeth', track='ghost of perdition')
Examples.findDuplicateScrobbles()
Examples.earliestListen(query='watershed', entity='album')
```
