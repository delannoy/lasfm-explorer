#!/usr/bin/env python3

from spotify import *

auth = Auth()

def testAlbum():
    id = '4aawyAB9vmqN3uQ7FjRGTy'
    ids = ['382ObEPsp2rxGrnsizN5TX', '1A2GTWGtFfWp7KSQTwWOyo', '2noRn2Aes5aoNVsU6iWThc']
    album = Album(auth)
    album.infoSingle(id=id)
    album.info(ids=ids)
    album.tracks(id=id)
    album.saved()
    album.save(ids=ids)
    album.unsave(ids=ids)
    album.isSaved(ids=ids)
    album.newReleases()

def testArtist():
    id = '0TnOYISbd1XYRBk9myaseg'
    ids = ['2CIMQHirSU0MQqyYHq0eOx', '57dN52uHvrHOxijzpIgu3E', '1vCWHaC5f2uS3yhpwWbIA6']
    artist = Artist(auth)
    artist.infoSingle(id=id)
    artist.info(ids=ids)
    artist.albums(id=id, include_groups=['album'])
    artist.topTracks(id=id, market='ES')
    artist.related(id=id)

def testAudiobook():
    id = '7iHfbu1YPACw6oZPAFJtqe'
    ids = ['18yVqkdbdRvS24c0Ilj2ci', '1HGw3J3NxZO1TP1BTtVhpZ', '7iHfbu1YPACw6oZPAFJtqe']
    audiobook = Audiobook(auth)
    audiobook.infoSingle(id=id, market='US')
    audiobook.info(ids=ids, market='US')
    audiobook.chapters(id=id, market='US')
    audiobook.saved()
    audiobook.save(ids=ids)
    audiobook.unsave(ids=ids)
    audiobook.isSaved(ids=ids)

def testCategory():
    category = Category(auth)
    category.browse()
    category.info(category_id='dinner')

def testChapter():
    id = '0D5wENdkdwbqlrHoaJ9g29'
    ids = ['0IsXVP0JmcB2adSE338GkK', '3ZXb8FKZGU0EHALYX6uCzU', '0D5wENdkdwbqlrHoaJ9g29']
    chapter = Chapter(auth)
    chapter.infoSingle(id=id, market='US')
    chapter.info(ids=ids, market='US')

def testEpisode():
    id = '512ojhOuo1ktJprKbVcKyQ'
    ids = ['77o6BIVlYM3msb4MMIL1jH', '0Q86acNRm6V9GYx55SXKwf']
    episode = Episode(auth)
    episode.infoSingle(id=id)
    episode.info(ids=ids)
    episode.saved()
    episode.save(ids=ids)
    episode.unsave(ids=ids)
    episode.isSaved(ids=ids)

def testGenre():
    Genre(auth).seeds()

def testMarket():
    Market(auth).info()

def testPlayer():
    device_ids = ['74ASZWbe4lXaubB36ztrGX']
    uri = 'spotify:track:4iV5W9uYEdYUVa79Axb7Rh'
    player = Player(auth)
    player.playbackState()
    player.transferPlayback(device_ids=device_ids)
    player.availableDevices()
    player.nowPlaying()
    player.play(device_id=device_ids[0])
    player.pause(device_id=device_ids[0])
    player.next(device_id=device_ids[0])
    player.previous(device_id=device_ids[0])
    player.seek(device_id=device_ids[0], position_ms=100)
    player.repeat(device_id=device_ids[0], state='track')
    player.volume(device_id=device_ids[0], volume_percent=50)
    player.shuffle(device_id=device_ids[0], state=True)
    player.recent()
    player.queue()
    player.add(device_id=device_ids[0], uri=uri)

def testPlaylist():
    uris = [f'spotify:track:{id}' for id in ('4iV5W9uYEdYUVa79Axb7Rh', '1301WleyT98MSxVHPZCA6M')]
    image = b'/9j/2wCEABoZGSccJz4lJT5CLy8vQkc9Ozs9R0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0cBHCcnMyYzPSYmPUc9Mj1HR0dEREdHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR0dHR//dAAQAAf/uAA5BZG9iZQBkwAAAAAH/wAARCAABAAEDACIAAREBAhEB/8QASwABAQAAAAAAAAAAAAAAAAAAAAYBAQAAAAAAAAAAAAAAAAAAAAAQAQAAAAAAAAAAAAAAAAAAAAARAQAAAAAAAAAAAAAAAAAAAAD/2gAMAwAAARECEQA/AJgAH//Z'
    user_id = User(auth).me().id
    playlist = Playlist(auth)
    playlist_id = playlist.create(user_id=user_id, name='Your Coolest Playlist').id
    playlist.info(playlist_id=playlist_id)
    playlist.modify(playlist_id=playlist_id, name='My New Playlist Title')
    playlist.addTracks(playlist_id=playlist_id, uris=uris)
    playlist.getTracks(playlist_id=playlist_id, fields='items(added_by.id,track(name,href,album(name,href)))')
    snapshot_id = playlist.info(playlist_id=playlist_id).snapshot_id
    playlist.reorder(playlist_id=playlist_id, range_start=0, insert_before=2, snapshot_id=snapshot_id)
    playlist.overwrite(playlist_id=playlist_id, uris=uris)
    playlist.removeTracks(playlist_id=playlist_id, tracks=[{'uri': uri} for uri in uris])
    playlist.mine()
    playlist.get(user_id='spotify')
    playlist.featured()
    playlist.category(category_id='dinner')
    playlist.cover(playlist_id=playlist_id)
    playlist.uploadCover(playlist_id=playlist_id, image=image)
    User(auth).unfollowPlaylist(playlist_id=playlist_id) # [Delete Spotify playlist programmatically](https://stackoverflow.com/a/62811488)

def testSearch():
    Search(auth).item(q='remaster track:Doxy artist:Miles Davis', type=['album', 'track'])

def testShow():
    id = '38bS44xjbVVZ3No3ByF1dJ'
    ids = ['5CfCWKI5pZ28U0uOzXkDHe', '5as3aKmN2k11yfDDDSrvaZ']
    show = Show(auth)
    show.infoSingle(id=id)
    show.info(ids=ids)
    show.episodes(id=id)
    show.saved()
    show.save(ids=ids)
    show.unsave(ids=ids)
    show.isSaved(ids=ids)

def testTrack():
    id = '11dFghVXANMlKmJXsNCbNl'
    ids = ['7ouMYWpwJ422jRcDASZB7P', '4VqPOruhp5EdPBeR92t6lQ', '2takcwOaAZWiXQijPHIx7B']
    track = Track(auth)
    track.infoSingle(id=id)
    track.info(ids=ids)
    track.saved()
    track.save(ids=ids)
    track.unsave(ids=ids)
    track.isSaved(ids=ids)
    track.audioFeatures(ids=ids)
    track.audioFeaturesSingle(id=id)
    track.audioAnalysis(id=id)
    track.recommendations(seed_artists=['4NHQUGzhtTLFvgF5SZesLK'], seed_genres=['classical', 'country'], seed_tracks=['0c6xIDDpzE81m2q797ordA'], min_instrumentalness=0.75)

def testUser():
    user_id = 'smedjan'
    playlist_id = '3cEYpjA9oz9GiPac4AsH4n'
    ids= ['2CIMQHirSU0MQqyYHq0eOx', '57dN52uHvrHOxijzpIgu3E', '1vCWHaC5f2uS3yhpwWbIA6']
    user = User(auth)
    user.me()
    user.topItems(type='artists')
    user.profile(user_id=user_id)
    user.followPlaylist(playlist_id=playlist_id)
    user.unfollowPlaylist(playlist_id=playlist_id)
    user.followedArtists()
    user.follow(type='artist', ids=ids)
    user.unfollow(type='artist', ids=ids)
    user.isFollowing(type='artist', ids=ids)
    user.areFollowingPlaylist(playlist_id=playlist_id, ids=['jmperezperez', 'thelinmichael', 'wizzler'])

def main():
    testAlbum()
    testArtist()
    testAudiobook()
    testCategory()
    testChapter()
    testEpisode()
    testGenre()
    testMarket()
    if User(auth).me().product == 'premium':
        testPlayer()
    testPlaylist()
    testSearch()
    testShow()
    testTrack()
    testUser()
