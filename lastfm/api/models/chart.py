#!/usr/bin/env python3

import typing
import uuid

import pydantic

from api.models import common


class Attr(common.BaseModel):
    page: int
    perPage: int
    totalPages: int
    total: int


'''chart.getTopArtists'''


class Artist(common.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID]
    url: pydantic.HttpUrl
    image: typing.List[common.Image]
    playcount: int
    listeners: int
    streamable: bool


class Artists(common.BaseModel):
    artist: typing.List[Artist]
    attr: Attr = pydantic.Field(alias='@attr')


'''chart.getTopTags'''


class Tag(common.BaseModel):
    name: str
    url: pydantic.HttpUrl
    taggings: int
    reach: int
    streamable: bool
    wiki: common.Wiki


class Tags(common.BaseModel):
    tag: typing.List[Tag]
    attr: Attr = pydantic.Field(alias='@attr')


'''chart.getTopTracks'''


class Track(common.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID]
    url: pydantic.HttpUrl
    image: typing.List[common.Image]
    duration: int
    playcount: int
    listeners: int
    streamable: common.Streamable
    artist: common.Entity


class Tracks(common.BaseModel):
    track: typing.List[Track]
    attr: Attr = pydantic.Field(alias='@attr')
