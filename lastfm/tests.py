#!/usr/bin/env python3

from api import album
from api import artist
from api import chart
from api import geo
from api import library
from api import tag
from api import track
from api import user

artist1 = 'failure'
mbid_artist1 = 'f0ed9f50-70b9-4406-9374-7d76ae21a04a'
artist2 = 'guns and roses'
artists = ['artist0','artist1','artist2']
album1 = 'fantastic planet'
mbid_album1 = '56d98466-411b-435f-941e-01f1877e59e9'
album2 = 'tree of stars'
albums = ['album0','album1','album2']
mbid_album2 = 'aeea1802-9cd1-44b7-b211-f3d9d23e1025'
track1 = 'stuck on you'
mbid_track1 = '357497cc-da8c-4efb-85dc-e121866a12c6'
track2 = 'mrbrownstone'
tracks = ['track0','track1','track2']
tag1='manchester'
country1='france'
FROM = 1555555555
to = 1666666666
timestamps = ['1970-01-01 12:00:00','1970-01-01 13:00:00', '1970-01-01 14:00:00']

def testAlbum():
    album.addTags(artist='_', album='_', tags=(0,1,2,3,4,5))
    [album.removeTag(artist='_', album='_', tag=tag) for tag in (0,1,2,3,4,5)]
    album.getInfo(artist=artist1, album=album1)
    album.getInfo(mbid=mbid_album1)
    [album.getInfo(artist=artist2, album=artist2, autocorrect=_) for _ in (True, False)]
    [album.getTags(artist=artist1, album=_) for _ in (album1, album2)]
    album.getTopTags(artist=artist1, album=album1)
    album.getTopTags(artist=artist2, album=artist2)
    album.search(album=album1)

def testArtist():
    artist.addTags(artist='_', tags=(0,1,2,3,4,5))
    [artist.removeTag(artist='_', tag=tag) for tag in (0,1,2,3,4,5)]
    [artist.getCorrection(artist=_) for _ in (artist1, artist2)]
    artist.getInfo(artist=artist1)
    [artist.getInfo(artist=artist2, autocorrect=_) for _ in (True, False)]
    artist.getSimilar(artist=artist1)
    artist.getSimilar(mbid=mbid_artist1)
    [artist.getSimilar(artist=artist2, autocorrect=_) for _ in (True, False)]
    [artist.getTags(artist=_) for _ in (artist1, artist2)]
    artist.getTopAlbums(artist=artist1)
    [artist.getTopAlbums(artist=artist2, autocorrect=_) for _ in (True, False)]
    artist.getTopTags(artist=artist1)
    [artist.getTopTags(artist=artist2, autocorrect=_) for _ in (True, False)]
    artist.getTopTracks(artist=artist1)
    [artist.getTopTracks(artist=artist2, autocorrect=_) for _ in (True, False)]
    [artist.search(artist=_) for _ in (artist1, artist2)]

def testChart():
    chart.getTopArtists()
    chart.getTopTags()
    chart.getTopTracks()

def testGeo():
    geo.getTopArtists(country=country1)
    geo.getTopTracks(country=country1)

def testLibrary():
    library.getArtists()

def testTag():
    tag.getInfo(tag=tag1)
    tag.getSimilar(tag=tag1)
    tag.getTopAlbums(tag=tag1)
    tag.getTopArtists(tag=tag1)
    tag.getTopTags()
    tag.getTopTracks(tag=tag1)
    tag.getWeeklyChartList(tag=tag1)

def testTrack():
    track.addTags(artist='_', track='_', tags=(0,1,2,3,4,5))
    [track.removeTag(artist='_', track='_', tag=tag) for tag in (0,1,2,3,4,5)]
    track.getCorrection(artist=artist2, track=track2)
    track.getInfo(artist=artist1, track=track1)
    track.getInfo(mbid=mbid_track1)
    [track.getInfo(artist=artist2, track=track2, autocorrect=_) for _ in (True, False)]
    track.getSimilar(artist=artist1, track=track1)
    [track.getSimilar(artist=artist2, track=track2, autocorrect=_) for _ in (True, False)]
    track.getTags(artist=artist1, track=track1)
    track.getTopTags(artist=artist1, track=track1)
    [track.getTopTags(artist=artist2, track=track2, autocorrect=_) for _ in (True, False)]
    track.love(artist='_', track='_')
    track.unlove(artist='_', track='_')
    track.scrobble(artist=artists, album=albums, track=tracks, timestamp=timestamps)
    track.search(artist=artist1, track=track1)
    track.updateNowPlaying(artist=artist1, album=album1, track=track1)

def testUser():
    [user.getFriends(recenttracks=_) for _ in (True, False)]
    user.getInfo()
    user.getLovedTracks()
    [user.getPersonalTags(tag=tag1, taggingtype=_.value) for _ in user.TaggingType]
    user.getRecentTracks()
    user.getRecentTracks(FROM=FROM, to=to)
    user.getTopAlbums()
    [user.getTopAlbums(period=e.value) for e in user.Period]
    user.getTopArtists()
    [user.getTopArtists(period=e.value) for e in user.Period]
    user.getTopTags()
    user.getTopTracks()
    [user.getTopTracks(period=e.value) for e in user.Period]
    user.getWeeklyAlbumChart()
    user.getWeeklyAlbumChart(FROM=FROM, to=to)
    user.getWeeklyArtistChart()
    user.getWeeklyArtistChart(FROM=FROM, to=to)
    user.getWeeklyChartList()
    user.getWeeklyTrackChart()
    user.getWeeklyTrackChart(FROM=FROM, to=to)
    user.getTrackScrobbles(artist=artist1, track=track1)

def main():
    testAlbum()
    testArtist()
    testChart()
    testGeo()
    testLibrary()
    testTag()
    testTrack()
    testUser()

if __name__ == '__main__':
    main()
