#!/usr/bin/env python3

import datetime
import typing
import uuid

import pydantic

import models


class Attr(models.BaseModel):
    user: str


'''user.getFriends'''


class Friend(models.BaseModel):
    name: str
    realname: typing.Optional[str]
    url: pydantic.HttpUrl
    image: typing.List[models.Image]
    country: typing.Optional[str]
    registered: models.Registered
    usertype: models.UserType = pydantic.Field(alias='type')
    subscriber: bool
    bootstrap: bool
    playcount: int
    playlists: int


class Friends(models.BaseModel):
    user: typing.List[Friend]
    attr: models.AttrUser = pydantic.Field(alias='@attr')


'''user.getInfo'''


class User(models.BaseModel):
    name: str
    realname: typing.Optional[str]
    url: pydantic.HttpUrl
    image: typing.List[models.Image]
    country: typing.Optional[str]
    gender: str
    age: int
    registered: models.Registered
    usertype: models.UserType = pydantic.Field(alias='type')
    subscriber: bool
    bootstrap: bool
    playcount: int
    artist_count: int
    track_count: int
    album_count: int
    playlists: int


'''user.getLovedTracks'''


class Lovedtrack(models.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID]
    url: pydantic.HttpUrl
    image: typing.List[models.Image]
    artist: models.Entity
    streamable: models.Streamable
    date: models.Date


class Lovedtracks(models.BaseModel):
    track: typing.List[Lovedtrack]
    attr: models.AttrUser = pydantic.Field(alias='@attr')


'''user.getPersonalTags'''


class AttrTaggings(models.BaseModel):
    user: str
    tag: str
    page: int
    perPage: int
    totalPages: int
    total: int


class PersonalTag(models.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID]
    url: pydantic.HttpUrl
    image: typing.List[models.Image]
    streamable: bool


class PersonalTags(models.BaseModel):
    artist: typing.Optional[typing.List[PersonalTag]]
    album: typing.Optional[typing.List[PersonalTag]]
    track: typing.Optional[typing.List[PersonalTag]]


class Taggings(models.BaseModel):
    artists: typing.Optional[PersonalTags]
    albums: typing.Optional[PersonalTags]
    tracks: typing.Optional[PersonalTags]
    attr: AttrTaggings = pydantic.Field(alias='@attr')


'''user.getRecentTracks'''


class AttrNowPlaying(models.BaseModel):
    nowplaying: bool


class RecentTrack(models.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID]
    url: pydantic.HttpUrl
    image: typing.List[models.Image]
    date: typing.Optional[models.Date]
    artist: models.Artist
    album: models.Album
    streamable: bool
    attr: typing.Optional[AttrNowPlaying] = pydantic.Field(alias='@attr')


class Recenttracks(models.BaseModel):
    track: typing.List[RecentTrack]
    attr: models.AttrUser = pydantic.Field(alias='@attr')


'''user.getTopAlbums'''


class TopAlbum(models.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID]
    url: pydantic.HttpUrl
    image: typing.List[models.Image]
    artist: models.Entity
    playcount: int
    attr: models.Rank = pydantic.Field(alias='@attr')


class Topalbums(models.BaseModel):
    album: typing.List[TopAlbum]
    attr: models.AttrUser = pydantic.Field(alias='@attr')


'''user.getTopArtists'''


class TopArtist(models.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID]
    url: pydantic.HttpUrl
    image: typing.List[models.Image]
    playcount: int
    streamable: bool
    attr: models.Rank = pydantic.Field(alias='@attr')


class Topartists(models.BaseModel):
    artist: typing.List[TopArtist]
    attr: models.AttrUser = pydantic.Field(alias='@attr')


'''user.getTopTags'''


class TopTag(models.BaseModel):
    name: str
    count: int
    url: pydantic.HttpUrl


class Toptags(models.BaseModel):
    tag: typing.List[TopTag]
    attr: Attr = pydantic.Field(alias='@attr')


'''user.getTopTracks'''


class TopTrack(models.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID]
    url: pydantic.HttpUrl
    image: typing.List[models.Image]
    duration: int
    playcount: int
    artist: models.Entity
    streamable: models.Streamable
    attr: models.Rank = pydantic.Field(alias='@attr')


class Toptracks(models.BaseModel):
    track: typing.List[TopTrack]
    attr: models.AttrUser = pydantic.Field(alias='@attr')


'''user.getWeeklyAlbumChart'''


class WeeklyAlbum(models.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID]
    url: pydantic.HttpUrl
    playcount: int
    artist: models.Artist
    attr: models.Rank = pydantic.Field(alias='@attr')


class Weeklyalbumchart(models.BaseModel):
    album: typing.List[WeeklyAlbum]
    attr: models.AttrWeekly = pydantic.Field(alias='@attr')


'''user.getWeeklyArtistChart'''


class WeeklyArtist(models.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID]
    url: pydantic.HttpUrl
    playcount: int
    attr: models.Rank = pydantic.Field(alias='@attr')


class Weeklyartistchart(models.BaseModel):
    artist: typing.List[WeeklyArtist]
    attr: models.AttrWeekly = pydantic.Field(alias='@attr')


'''user.getWeeklyChartList'''


class WeeklyChart(models.BaseModel):
    chart: typing.Optional[str] = pydantic.Field(alias='#text')
    fr: int = pydantic.Field(alias='from')
    to: int


class Weeklychartlist(models.BaseModel):
    chart: typing.List[WeeklyChart]
    attr: Attr = pydantic.Field(alias='@attr')


'''user.getWeeklyTrackChart'''


class WeeklyTrack(models.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID]
    url: pydantic.HttpUrl
    image: typing.List[models.Image]
    playcount: int
    artist: models.Artist
    attr: models.Rank = pydantic.Field(alias='@attr')


class Weeklytrackchart(models.BaseModel):
    track: typing.List[WeeklyTrack]
    attr: models.AttrWeekly = pydantic.Field(alias='@attr')


class Trackscrobbles(models.BaseModel):
    track: typing.List[RecentTrack]
    attr: models.AttrUser = pydantic.Field(alias='@attr')
