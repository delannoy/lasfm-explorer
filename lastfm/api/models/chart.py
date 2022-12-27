#!/usr/bin/env python3

import datetime
import typing
import uuid

import pydantic

import models


class Attr(models.BaseModel):
    page: int
    perPage: int
    totalPages: int
    total: int


'''chart.getTopArtists'''


class Artist(models.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID]
    url: pydantic.HttpUrl
    image: typing.List[models.Image]
    playcount: int
    listeners: int
    streamable: bool


class Artists(models.BaseModel):
    artist: typing.List[Artist]
    attr: Attr = pydantic.Field(alias='@attr')


'''chart.getTopTags'''


class Tag(models.BaseModel):
    name: str
    url: pydantic.HttpUrl
    taggings: int
    reach: int
    streamable: bool
    wiki: models.Wiki


class Tags(models.BaseModel):
    tag: typing.List[Tag]
    attr: Attr = pydantic.Field(alias='@attr')


'''chart.getTopTracks'''


class Track(models.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID]
    url: pydantic.HttpUrl
    image: typing.List[models.Image]
    duration: int
    playcount: int
    listeners: int
    streamable: models.Streamable
    artist: models.Entity


class Tracks(models.BaseModel):
    track: typing.List[Track]
    attr: Attr = pydantic.Field(alias='@attr')
