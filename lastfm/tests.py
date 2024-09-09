#!/usr/bin/env python3

from lastfm import *


class Misspelt:
    artist = 'guns roses'
    artist_mbid = '6f1018cd-67e4-4193-bace-34453d254b88'
    album = 'appetite for destruction'
    album_mbid = '7b6a56e7-e33d-4b89-bee5-1363437f2108'
    track = 'sweet child of mine'
    track_mbid = 'a088e6f7-0023-41e4-a9b2-71552d42e5fd'
    country = 'lol'
    language = 'lol'
    username: 'lool'


artists = ['metallica', 'failure']
artist_mbid = ['65f4f0c5-ef9e-490c-aee3-909e7ae6b2ab', 'f0ed9f50-70b9-4406-9374-7d76ae21a04a']
albums = ['metallica', 'fantastic planet']
album_mbid = ['69a8ca83-a182-3375-a702-a30e216748c9', '56d98466-411b-435f-941e-01f1877e59e9']
tracks = ['enter sandman', 'stuck on you']
track_mbid = ['5cbb546d-5c1c-490e-9908-761b89dd5166', '357497cc-da8c-4efb-85dc-e121866a12c6']
countries = ['france', 'uruguay']
languages = ['fr', 'es']
tags = ['metal', 'manchester']
usernames = ['rj', Auth.username]

limit = 4
page = 2
FROM = 1555555555
TO = 1666666666

def testAlbum():
    album.addTags(artist='_', album='_', tags=(0,1,2,3,4,5))
    [album.removeTag(artist='_', album='_', tag=tag) for tag in (0,1,2,3,4,5)]
    [album.getInfo(artist=_, album=__, user=usernames[0]) for _, __ in zip(artists, albums)]
    [album.getInfo(mbid=_, lang=languages[0]) for _ in album_mbid]
    [album.getInfo(artist=Misspelt.artist, album=Misspelt.album, user=usernames[0], autocorrect=_,) for _ in (False, True)]
    [album.getTags(artist=_, album=__, user=usernames[0]) for _, __ in zip(artists, albums)]
    [album.getTags(artist=Misspelt.artist, album=Misspelt.album, user=usernames[0], autocorrect=_) for _ in (False, True)]
    [album.getTopTags(artist=_, album=__) for _, __ in zip(artists, albums)]
    [album.getTopTags(artist=Misspelt.artist, album=Misspelt.album, autocorrect=_) for _ in (False, True)]
    [album.search(album=_, limit=limit, page=page) for _ in albums]

def testArtist():
    artist.addTags(artist='_', tags=(0,1,2,3,4,5))
    [artist.removeTag(artist='_', tag=tag) for tag in (0,1,2,3,4,5)]
    [artist.getCorrection(artist=_) for _ in artists + [Misspelt.artist]]
    [artist.getInfo(artist=_, user=usernames[0]) for _ in artists]
    [artist.getInfo(mbid=_, lang=languages[0]) for _ in artist_mbid]
    [artist.getInfo(artist=Misspelt.artist, autocorrect=_) for _ in (False, True)]
    [artist.getSimilar(artist=_, limit=limit) for _ in artists]
    [artist.getSimilar(artist=Misspelt.artist, limit=limit, autocorrect=_) for _ in (False, True)]
    [artist.getTags(artist=_, user=usernames[0]) for _ in artists]
    [artist.getTags(artist=Misspelt.artist, user=usernames[0], autocorrect=_) for _ in (False, True)]
    [artist.getTopAlbums(artist=_, limit=limit, page=page) for _ in artists]
    [artist.getTopAlbums(artist=Misspelt.artist, autocorrect=_, limit=limit, page=page) for _ in (False, True)]
    [artist.getTopTags(artist=_) for _ in artists]
    [artist.getTopTags(artist=Misspelt.artist, autocorrect=_) for _ in (False, True)]
    [artist.getTopTracks(artist=_, limit=limit, page=page) for _ in artists]
    [artist.getTopTracks(artist=Misspelt.artist, autocorrect=_) for _ in (False, True)]
    [artist.search(artist=_, limit=limit, page=page) for _ in artists]

def testChart():
    chart.getTopArtists(limit=limit, page=page)
    chart.getTopTags(limit=limit, page=page)
    chart.getTopTracks(limit=limit, page=page)

def testGeo():
    [geo.getTopArtists(country=_, limit=limit, page=page) for _ in countries]
    [geo.getTopTracks(country=_, limit=limit, page=page) for _ in countries]

def testLibrary():
    [library.getArtists(user=_, limit=limit, page=page) for _ in usernames]

def testTag():
    [tag.getInfo(tag=_, lang=languages[0]) for _ in tags]
    [tag.getSimilar(tag=_) for _ in tags] # `tag.getSimilar` seems to be broken; no data returned
    [tag.getTopAlbums(tag=_, limit=limit, page=page) for _ in tags]
    [tag.getTopArtists(tag=_, limit=limit, page=page) for _ in tags]
    tag.getTopTags()
    [tag.getTopTracks(tag=_, limit=limit, page=page) for _ in tags]
    [tag.getWeeklyChartList(tag=_) for _ in tags]

def testTrack():
    track.addTags(artist='_', track='_', tags=(0,1,2,3,4,5))
    [track.removeTag(artist='_', track='_', tag=tag) for tag in (0,1,2,3,4,5)]
    [track.getCorrection(artist=_, track=__) for _, __ in zip(artists+[Misspelt.artist], tracks+[Misspelt.track])]
    [track.getInfo(artist=_, track=__, user=usernames[0]) for _, __ in zip(artists, tracks)]
    [track.getInfo(mbid=_, lang=languages[0], user=usernames[0]) for _ in track_mbid]
    [track.getInfo(artist=Misspelt.artist, track=Misspelt.track, autocorrect=_) for _ in (False, True)]
    [track.getSimilar(artist=_, track=__, limit=limit) for _, __ in zip(artists, tracks)]
    [track.getSimilar(artist=Misspelt.artist, track=Misspelt.track, limit=limit, autocorrect=_) for _ in (False, True)]
    [track.getTags(artist=_, track=__, user=usernames[0]) for _, __ in zip(artists, tracks)]
    [track.getTags(artist=Misspelt.artist, track=Misspelt.track, user=usernames[0], autocorrect=_) for _ in (False, True)]
    [track.getTopTags(artist=_, track=__) for _, __ in zip(artists, tracks)]
    [track.getTopTags(Misspelt.artist, track=Misspelt.track, autocorrect=_) for _ in (False, True)]
    track.love(artist='_', track='_')
    track.unlove(artist='_', track='_')
    track.scrobble(artist=['artist0', 'artist1', 'artist2'], album=['album0', 'album1', 'album2'], track=['track0', 'track1', 'track2'], timestamp=['1970-01-01 12:00:00','1970-01-01 13:00:00', '1970-01-01 14:00:00'])
    [track.search(artist=_, track=__, limit=limit, page=page) for _, __ in zip(artists, tracks)]
    track.updateNowPlaying(artist=artists[1], album=albums[1], track=tracks[1])

def testUser():
    [user.getFriends(user=usernames[0], recenttracks=_, limit=limit, page=page) for _ in (False, True)]
    [user.getInfo(user=_) for _ in usernames]
    [user.getLovedTracks(user=_, limit=limit, page=page) for _ in usernames]
    [user.getPersonalTags(user=usernames[0], tag=tags[0], taggingtype=_) for _ in TaggingType]
    [user.getRecentTracks(user=usernames[0], FROM=FROM, TO=TO, extended=extended, limit=limit, page=page) for extended in (False, True)]
    [user.getTopAlbums(user=_, limit=limit, page=page) for _ in usernames]
    [user.getTopAlbums(user=usernames[0], period=e, limit=limit, page=page) for e in Period]
    [user.getTopArtists(user=_, limit=limit, page=page) for _ in usernames]
    [user.getTopArtists(user=usernames[0], period=e, limit=limit, page=page) for e in Period]
    [user.getTopTags(user=_, limit=limit) for _ in usernames]
    [user.getTopTracks(user=_, limit=limit, page=page) for _ in usernames]
    [user.getTopTracks(user=usernames[0], period=e, limit=limit, page=page) for e in Period]
    [user.getWeeklyAlbumChart(user=_, FROM=FROM, TO=TO) for _ in usernames]
    [user.getWeeklyArtistChart(user=_, FROM=FROM, TO=TO) for _ in usernames]
    [user.getWeeklyChartList(user=_) for _ in usernames]
    [user.getWeeklyTrackChart(user=_, FROM=FROM, TO=TO) for _ in usernames]
    [user.getTrackScrobbles(user=_, artist=artists[0], track=tracks[0], TO=TO, limit=limit, page=page) for _ in usernames]

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
