#!/usr/bin/env python3

import typing
import uuid

import pydantic

import api.errors
from api.models import common


class Attr(common.BaseModel):
    artist: str
    track: str


'''track.getCorrection'''


class AttrCorrection(common.BaseModel):
    index: int
    artistcorrected: bool
    trackcorrected: bool


class TrackCorrection(common.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID]
    url: pydantic.HttpUrl
    artist: common.Entity


class Correction(common.BaseModel):
    track: TrackCorrection
    attr: AttrCorrection = pydantic.Field(alias='@attr')


class Corrections(common.BaseModel):
    correction: Correction


'''track.getInfo'''


class AttrPosition(common.BaseModel):
    position: int


class Album(common.BaseModel):
    title: str
    artist: str
    mbid: typing.Optional[uuid.UUID]
    url: pydantic.HttpUrl
    image: typing.List[common.Image]
    attr: AttrPosition = pydantic.Field(alias='@attr')


class Tag(common.BaseModel):
    tag: typing.List[common.Tag]


class Track(common.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID]
    url: pydantic.HttpUrl
    duration: int
    listeners: int
    playcount: int
    userplaycount: int
    userloved: bool
    artist: common.Entity
    album: Album
    toptags: Tag
    streamable: common.Streamable
    wiki: typing.Optional[common.Wiki]


'''track.getSimilar'''


class AttrTrack(common.BaseModel):
    artist: str


class SimilarTrack(common.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID]
    url: pydantic.HttpUrl
    image: typing.List[common.Image]
    duration: typing.Optional[int]
    playcount: int
    artist: common.Entity
    match: float
    streamable: common.Streamable


class Similartracks(common.BaseModel):
    track: typing.List[SimilarTrack]
    attr: AttrTrack = pydantic.Field(alias='@attr')


'''track.getTags'''


class Tags(common.BaseModel):
    tag: typing.Optional[typing.List[common.Tag]]
    text: typing.Optional[str] = pydantic.Field(alias='#text')
    attr: Attr = pydantic.Field(alias='@attr')


'''track.getTopTags'''


class Toptags(common.BaseModel):
    tag: typing.List[common.TopTag]
    attr: Attr = pydantic.Field(alias='@attr')


'''track.scrobble'''


class AttrScrobble(common.BaseModel):
    ignored: int
    accepted: int

class IgnoredMessage(common.BaseModel):
    code: api.errors.ScrobbleErrors
    text: typing.Optional[str] = pydantic.Field(alias='#text')


class Entity(common.BaseModel):
    name: typing.Optional[str] = pydantic.Field(alias='#text')
    corrected: bool


class Scrobble(common.BaseModel):
    artist: Entity
    albumArtist: Entity
    album: Entity
    track: Entity
    ignoredMessage: IgnoredMessage
    timestamp: int


class Scrobbles(common.BaseModel):
    scrobble: typing.List[Scrobble]
    attr: AttrScrobble = pydantic.Field(alias='@attr')


'''track.search'''


class TrackMatch(common.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID]
    url: pydantic.HttpUrl
    image: typing.List[common.Image]
    artist: str
    listeners: int
    streamable: typing.Optional[bool]


class TrackMatches(common.BaseModel):
    track: typing.List[TrackMatch]


class Results(common.BaseModel):
    trackmatches: TrackMatches
    opensearch_Query: common.AttrOpensearchQuery = pydantic.Field(alias='opensearch:Query')
    opensearch_totalResults: str = pydantic.Field(alias='opensearch:totalResults')
    opensearch_startIndex: str = pydantic.Field(alias='opensearch:startIndex')
    opensearch_itemsPerPage: str = pydantic.Field(alias='opensearch:itemsPerPage')
    attr: common.AttrQuery = pydantic.Field(alias='@attr')


'''track.updateNowPlaying'''


class Nowplaying(common.BaseModel):
    artist: Entity
    albumArtist: Entity
    album: Entity
    track: Entity
    ignoredMessage: IgnoredMessage
