#!/usr/bin/env python3

import typing
import uuid

import pydantic

from api.models import common


class Attr(common.BaseModel):
    country: str
    page: int
    perPage: int
    totalPages: int
    total: int


'''geo.getTopArtists'''


class Artist(common.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID]
    url: pydantic.HttpUrl
    image: typing.List[common.Image]
    listeners: int
    streamable: bool


class Topartists(common.BaseModel):
    artist: typing.List[Artist]
    attr: Attr = pydantic.Field(alias='@attr')


'''geo.getTopTracks'''


class Track(common.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID]
    url: pydantic.HttpUrl
    image: typing.List[common.Image]
    duration: int
    listeners: int
    streamable: common.Streamable
    artist: common.Entity
    attr: common.Rank = pydantic.Field(alias='@attr')


class Tracks(common.BaseModel):
    track: typing.List[Track]
    attr: Attr = pydantic.Field(alias='@attr')
