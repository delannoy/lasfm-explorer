#!/usr/bin/env python3

import typing
import uuid

import pydantic

import models


class Attr(models.BaseModel):
    artist: str
    album: str


'''album.getInfo'''


class TrackTags(models.BaseModel):
    tag: typing.List[models.Tag]


class Track(models.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID]
    url: pydantic.HttpUrl
    artist: models.Entity
    duration: typing.Optional[int]
    streamable: models.Streamable
    attr: models.Rank = pydantic.Field(alias='@attr')


class Tracks(models.BaseModel):
    track: typing.List[Track]


class Album(models.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID]
    url: pydantic.HttpUrl
    image: typing.List[models.Image]
    artist: str
    tracks: typing.Optional[Tracks]
    tags: typing.Optional[TrackTags]
    listeners: int
    playcount: int
    userplaycount: int


'''album.getTags'''


class Tags(models.BaseModel):
    tag: typing.Optional[typing.List[models.Tag]]
    text: typing.Optional[str] = pydantic.Field(alias='#text')
    attr: Attr = pydantic.Field(alias='@attr')


'''album.getTopTags'''


class Toptags(models.BaseModel):
    tag: typing.List[models.TopTag]
    attr: Attr = pydantic.Field(alias='@attr')


'''album.search'''


class AlbumMatch(models.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID]
    url: pydantic.HttpUrl
    image: typing.List[models.Image]
    artist: str
    streamable: bool


class AlbumMatches(models.BaseModel):
    album: typing.List[AlbumMatch]


class Results(models.BaseModel):
    albummatches: AlbumMatches
    opensearch_Query: models.AttrOpensearchQuery = pydantic.Field(alias='opensearch:Query')
    opensearch_totalResults: str = pydantic.Field(alias='opensearch:totalResults')
    opensearch_startIndex: str = pydantic.Field(alias='opensearch:startIndex')
    opensearch_itemsPerPage: str = pydantic.Field(alias='opensearch:itemsPerPage')
    attr: models.AttrQuery = pydantic.Field(alias='@attr')
