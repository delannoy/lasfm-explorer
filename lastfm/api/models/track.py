#!/usr/bin/env python3

import enum
import typing
import uuid

import pydantic

import models


class Attr(models.BaseModel):
    artist: str
    track: str


'''track.getCorrection'''


class AttrCorrection(models.BaseModel):
    index: int
    artistcorrected: bool
    trackcorrected: bool


class TrackCorrection(models.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID]
    url: pydantic.HttpUrl
    artist: models.Entity


class Correction(models.BaseModel):
    track: TrackCorrection
    attr: AttrCorrection = pydantic.Field(alias='@attr')


class Corrections(models.BaseModel):
    correction: Correction


'''track.getInfo'''


class AttrPosition(models.BaseModel):
    position: int


class Album(models.BaseModel):
    title: str
    artist: str
    mbid: typing.Optional[uuid.UUID]
    url: pydantic.HttpUrl
    image: typing.List[models.Image]
    attr: AttrPosition = pydantic.Field(alias='@attr')


class Tag(models.BaseModel):
    tag: typing.List[models.Tag]


class Track(models.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID]
    url: pydantic.HttpUrl
    duration: int
    listeners: int
    playcount: int
    userplaycount: int
    userloved: bool
    artist: models.Entity
    album: Album
    toptags: Tag
    streamable: models.Streamable
    wiki: typing.Optional[models.Wiki]


'''track.getSimilar'''


class AttrTrack(models.BaseModel):
    artist: str


class SimilarTrack(models.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID]
    url: pydantic.HttpUrl
    image: typing.List[models.Image]
    duration: typing.Optional[int]
    playcount: int
    artist: models.Entity
    match: float
    streamable: models.Streamable


class Similartracks(models.BaseModel):
    track: typing.List[SimilarTrack]
    attr: AttrTrack = pydantic.Field(alias='@attr')


'''track.getTags'''


class Tags(models.BaseModel):
    tag: typing.Optional[typing.List[models.Tag]]
    text: typing.Optional[str] = pydantic.Field(alias='#text')
    attr: Attr = pydantic.Field(alias='@attr')


'''track.getTopTags'''


class Toptags(models.BaseModel):
    tag: typing.List[models.TopTag]
    attr: Attr = pydantic.Field(alias='@attr')


'''track.scrobble'''


class AttrScrobble(models.BaseModel):
    ignored: int
    accepted: int

import errors
class IgnoredMessage(models.BaseModel):
    code: errors.ScrobbleErrors
    text: typing.Optional[str] = pydantic.Field(alias='#text')


class Entity(models.BaseModel):
    name: typing.Optional[str] = pydantic.Field(alias='#text')
    corrected: bool


class Scrobble(models.BaseModel):
    artist: Entity
    albumArtist: Entity
    album: Entity
    track: Entity
    ignoredMessage: IgnoredMessage
    timestamp: int


class Scrobbles(models.BaseModel):
    scrobble: typing.List[Scrobble]
    attr: AttrScrobble = pydantic.Field(alias='@attr')


'''track.search'''


class TrackMatch(models.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID]
    url: pydantic.HttpUrl
    image: typing.List[models.Image]
    artist: str
    listeners: int
    streamable: typing.Optional[bool]


class TrackMatches(models.BaseModel):
    track: typing.List[TrackMatch]


class Results(models.BaseModel):
    trackmatches: TrackMatches
    opensearch_Query: models.AttrOpensearchQuery = pydantic.Field(alias='opensearch:Query')
    opensearch_totalResults: str = pydantic.Field(alias='opensearch:totalResults')
    opensearch_startIndex: str = pydantic.Field(alias='opensearch:startIndex')
    opensearch_itemsPerPage: str = pydantic.Field(alias='opensearch:itemsPerPage')
    attr: models.AttrQuery = pydantic.Field(alias='@attr')


'''track.updateNowPlaying'''


class Nowplaying(models.BaseModel):
    artist: Entity
    albumArtist: Entity
    album: Entity
    track: Entity
    ignoredMessage: IgnoredMessage
