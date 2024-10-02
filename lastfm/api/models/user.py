#!/usr/bin/env python3

import typing
import uuid

import pydantic

from api.models import common


class Attr(common.BaseModel):
    user: str


'''user.getFriends'''


class Friend(common.BaseModel):
    name: str
    realname: typing.Optional[str] = None
    url: pydantic.HttpUrl
    image: typing.List[common.Image]
    country: typing.Optional[str] = None
    registered: common.Registered
    usertype: common.UserType = pydantic.Field(alias='type')
    subscriber: bool
    bootstrap: bool
    playcount: int
    playlists: int


class Friends(common.BaseModel):
    user: typing.List[Friend]
    attr: common.AttrUser = pydantic.Field(alias='@attr')


'''user.getInfo'''


class User(common.BaseModel):
    name: str
    realname: typing.Optional[str] = None
    url: pydantic.HttpUrl
    image: typing.List[common.Image]
    country: typing.Optional[str] = None
    gender: str
    age: int
    registered: common.Registered
    usertype: common.UserType = pydantic.Field(alias='type')
    subscriber: bool
    bootstrap: bool
    playcount: int
    artist_count: int
    track_count: int
    album_count: int
    playlists: int


'''user.getLovedTracks'''


class Lovedtrack(common.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID] = None
    url: pydantic.HttpUrl
    image: typing.List[common.Image]
    artist: common.Entity
    streamable: common.Streamable
    date: common.Date


class Lovedtracks(common.BaseModel):
    track: typing.List[Lovedtrack]
    attr: common.AttrUser = pydantic.Field(alias='@attr')


'''user.getPersonalTags'''


class AttrTaggings(common.BaseModel):
    user: str
    tag: str
    page: int
    perPage: int
    totalPages: int
    total: int


class PersonalTag(common.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID] = None
    url: pydantic.HttpUrl
    image: typing.List[common.Image]
    streamable: bool


class PersonalTags(common.BaseModel):
    artist: typing.Optional[typing.List[PersonalTag]] = None
    album: typing.Optional[typing.List[PersonalTag]] = None
    track: typing.Optional[typing.List[PersonalTag]] = None


class Taggings(common.BaseModel):
    artists: typing.Optional[PersonalTags] = None
    albums: typing.Optional[PersonalTags] = None
    tracks: typing.Optional[PersonalTags] = None
    attr: AttrTaggings = pydantic.Field(alias='@attr')


'''user.getRecentTracks'''


class AttrNowPlaying(common.BaseModel):
    nowplaying: bool


class RecentTrack(common.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID] = None
    url: pydantic.HttpUrl
    image: typing.List[common.Image]
    date: typing.Optional[common.Date] = None
    artist: common.Artist
    album: common.Album
    streamable: bool
    attr: typing.Optional[AttrNowPlaying] = pydantic.Field(alias='@attr', default=None)


class ArtistExtended(common.BaseModel):
    name: str
    mbid: None # artist mbid is missing with the `extended` option
    url: pydantic.HttpUrl
    image: typing.List[common.Image]


class RecentTrackExtended(common.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID] = None
    url: pydantic.HttpUrl
    image: typing.List[common.Image]
    date: typing.Optional[common.Date] = None
    artist: ArtistExtended
    album: common.Album
    streamable: bool
    loved: bool
    attr: typing.Optional[AttrNowPlaying] = pydantic.Field(alias='@attr', default=None)


class Recenttracks(common.BaseModel):
    track: typing.Union[typing.List[RecentTrack], RecentTrack, typing.List[RecentTrackExtended], RecentTrackExtended] # if no scrobbles are recorded, an empty list will be returned or a single `RecentTrack` (if user is "now playing") will be returned
    attr: common.AttrUser = pydantic.Field(alias='@attr')


'''user.getTopAlbums'''


class TopAlbum(common.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID] = None
    url: pydantic.HttpUrl
    image: typing.List[common.Image]
    artist: common.Entity
    playcount: int
    attr: common.Rank = pydantic.Field(alias='@attr')


class Topalbums(common.BaseModel):
    album: typing.List[TopAlbum]
    attr: common.AttrUser = pydantic.Field(alias='@attr')


'''user.getTopArtists'''


class TopArtist(common.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID] = None
    url: pydantic.HttpUrl
    image: typing.List[common.Image]
    playcount: int
    streamable: bool
    attr: common.Rank = pydantic.Field(alias='@attr')


class Topartists(common.BaseModel):
    artist: typing.List[TopArtist]
    attr: common.AttrUser = pydantic.Field(alias='@attr')


'''user.getTopTags'''


class TopTag(common.BaseModel):
    name: str
    count: int
    url: pydantic.HttpUrl


class Toptags(common.BaseModel):
    tag: typing.List[TopTag]
    attr: Attr = pydantic.Field(alias='@attr')


'''user.getTopTracks'''


class TopTrack(common.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID] = None
    url: pydantic.HttpUrl
    image: typing.List[common.Image]
    duration: int
    playcount: int
    artist: common.Entity
    streamable: common.Streamable
    attr: common.Rank = pydantic.Field(alias='@attr')


class Toptracks(common.BaseModel):
    track: typing.List[TopTrack]
    attr: common.AttrUser = pydantic.Field(alias='@attr')


'''user.getWeeklyAlbumChart'''


class WeeklyAlbum(common.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID] = None
    url: pydantic.HttpUrl
    playcount: int
    artist: common.Artist
    attr: common.Rank = pydantic.Field(alias='@attr')


class Weeklyalbumchart(common.BaseModel):
    album: typing.List[WeeklyAlbum]
    attr: common.AttrWeekly = pydantic.Field(alias='@attr')


'''user.getWeeklyArtistChart'''


class WeeklyArtist(common.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID] = None
    url: pydantic.HttpUrl
    playcount: int
    attr: common.Rank = pydantic.Field(alias='@attr')


class Weeklyartistchart(common.BaseModel):
    artist: typing.List[WeeklyArtist]
    attr: common.AttrWeekly = pydantic.Field(alias='@attr')


'''user.getWeeklyChartList'''


class WeeklyChart(common.BaseModel):
    chart: typing.Optional[str] = pydantic.Field(alias='#text', default=None)
    fr: int = pydantic.Field(alias='from')
    to: int


class Weeklychartlist(common.BaseModel):
    chart: typing.List[WeeklyChart]
    attr: Attr = pydantic.Field(alias='@attr')


'''user.getWeeklyTrackChart'''


class WeeklyTrack(common.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID] = None
    url: pydantic.HttpUrl
    image: typing.List[common.Image]
    playcount: int
    artist: common.Artist
    attr: common.Rank = pydantic.Field(alias='@attr')


class Weeklytrackchart(common.BaseModel):
    track: typing.List[WeeklyTrack]
    attr: common.AttrWeekly = pydantic.Field(alias='@attr')


'''user.getTrackScrobbles'''


class Trackscrobbles(common.BaseModel):
    track: typing.List[RecentTrack]
    attr: common.AttrUser = pydantic.Field(alias='@attr')
