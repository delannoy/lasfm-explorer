#!/usr/bin/env python3

import typing
import uuid

import pydantic

import models


class Attr(models.BaseModel):
    country: str
    page: int
    perPage: int
    totalPages: int
    total: int


'''geo.getTopArtists'''


class Artist(models.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID]
    url: pydantic.HttpUrl
    image: typing.List[models.Image]
    listeners: int
    streamable: bool


class Topartists(models.BaseModel):
    artist: typing.List[Artist]
    attr: Attr = pydantic.Field(alias='@attr')


'''geo.getTopTracks'''


class Track(models.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID]
    url: pydantic.HttpUrl
    image: typing.List[models.Image]
    duration: int
    listeners: int
    streamable: models.Streamable
    artist: models.Entity
    attr: models.Rank = pydantic.Field(alias='@attr')


class Tracks(models.BaseModel):
    track: typing.List[Track]
    attr: Attr = pydantic.Field(alias='@attr')
