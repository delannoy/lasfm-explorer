#!/usr/bin/env python3

import typing
import uuid

import pydantic

from api.models import common


class Attr(common.BaseModel):
    artist: str
    album: str


'''album.getInfo'''


class TrackTags(common.BaseModel):
    tag: typing.List[common.Tag]


class Track(common.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID]
    url: pydantic.HttpUrl
    artist: common.Entity
    duration: typing.Optional[int]
    streamable: common.Streamable
    attr: common.Rank = pydantic.Field(alias='@attr')


class Tracks(common.BaseModel):
    track: typing.List[Track]


class Album(common.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID]
    url: pydantic.HttpUrl
    image: typing.List[common.Image]
    artist: str
    tracks: typing.Optional[Tracks]
    tags: typing.Optional[TrackTags]
    listeners: int
    playcount: int
    userplaycount: int


'''album.getTags'''


class Tags(common.BaseModel):
    tag: typing.Optional[typing.List[common.Tag]]
    text: typing.Optional[str] = pydantic.Field(alias='#text')
    attr: Attr = pydantic.Field(alias='@attr')


'''album.getTopTags'''


class Toptags(common.BaseModel):
    tag: typing.List[common.TopTag]
    attr: Attr = pydantic.Field(alias='@attr')


'''album.search'''


class AlbumMatch(common.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID]
    url: pydantic.HttpUrl
    image: typing.List[common.Image]
    artist: str
    streamable: bool


class AlbumMatches(common.BaseModel):
    album: typing.List[AlbumMatch]


class Results(common.BaseModel):
    albummatches: AlbumMatches
    opensearch_Query: common.AttrOpensearchQuery = pydantic.Field(alias='opensearch:Query')
    opensearch_totalResults: str = pydantic.Field(alias='opensearch:totalResults')
    opensearch_startIndex: str = pydantic.Field(alias='opensearch:startIndex')
    opensearch_itemsPerPage: str = pydantic.Field(alias='opensearch:itemsPerPage')
    attr: common.AttrQuery = pydantic.Field(alias='@attr')
