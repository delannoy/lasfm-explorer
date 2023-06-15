# lastfm-explorer
Python wrapper for lastFM API to explore and/or export user data.

## setup
A LastFM API key is required for most API methods (can be obtained [here](https://www.last.fm/api/authentication)).

## usage examples
```python
from api import *

sum(album.getInfo(artist='tool', album='undertow').tracks.track.duration)
# 3958

artist.getTopTags(artist='the contortionist').tag[:4].name.to_list()
# ['deathcore', 'Progressive deathcore', 'Progressive metal', 'experimental']

artist.getSimilar(artist='rivers of nihil', limit=4).artist.name.to_list()
# ['Black Crown Initiate', 'Allegaeon', 'Archspire', 'Fallujah']

geo.getTopArtists(country='germany', limit=4).artist.name.to_list()
# ['Queen', 'Coldplay', 'Red Hot Chili Peppers', 'David Bowie']

user.getTrackScrobbles(artist='opeth', track='ghost of perdition', limit=4).track.date.dateTime.to_list()
# ['2022-10-14T13:19:00', '2022-07-20T11:12:00', '2022-05-01T03:21:00', '2022-03-29T14:42:00']

playcount = int(user.getInfo().playcount)
user.getRecentTracks(limit=1, page=playcount).track.date.dateTime[-1]
# '2007-11-04T20:07:00'
```
