#!/usr/bin/env python3

import typing
import uuid

import pydantic

import models


class Attr(models.BaseModel):
    tag: typing.Optional[str]


'''tag.getInfo'''


class Tag(models.BaseModel):
    name: str
    total: int
    reach: int
    wiki: models.Wiki


'''tag.getSimilar'''


class SimilarTag(models.BaseModel):
    name: str
    url: pydantic.HttpUrl
    streamable: bool


class Similartags(models.BaseModel):
    tag: typing.List[SimilarTag]
    attr: Attr = pydantic.Field(alias='@attr')


'''tag.getTopAlbums'''


class Album(models.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID]
    url: pydantic.HttpUrl
    image: typing.List[models.Image]
    artist: models.Entity
    attr: models.Rank = pydantic.Field(alias='@attr')


class Albums(models.BaseModel):
    album: typing.List[Album]
    tag: models.AttrTag = pydantic.Field(alias='@attr')


'''tag.getTopArtists'''


class Artist(models.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID]
    url: pydantic.HttpUrl
    image: typing.List[models.Image]
    streamable: bool
    attr: models.Rank = pydantic.Field(alias='@attr')


class Topartists(models.BaseModel):
    artist: typing.List[Artist]
    tag: models.AttrTag = pydantic.Field(alias='@attr')


'''tag.getTopTags'''


class AttrTopTag(models.BaseModel):
    offset: int
    num_res: int
    total: int


class TopTag(models.BaseModel):
    name: str
    count: int
    reach: int


class Toptags(models.BaseModel):
    tag: typing.List[TopTag]
    attr: AttrTopTag = pydantic.Field(alias='@attr')


'''tag.getTopTracks'''


class Track(models.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID]
    url: pydantic.HttpUrl
    image: typing.List[models.Image]
    duration: int
    artist: models.Entity
    streamable: models.Streamable
    attr: models.Rank = pydantic.Field(alias='@attr')


class Tracks(models.BaseModel):
    track: typing.List[Track]
    tag: models.AttrTag = pydantic.Field(alias='@attr')


'''tag.getWeeklyChartList'''


class Weekly(models.BaseModel):
    text: typing.Optional[str] = pydantic.Field(alias='#text')
    fr: int = pydantic.Field(alias='from')
    to: int


class Weeklychartlist(models.BaseModel):
    chart: typing.List[Weekly]
    attr: Attr = pydantic.Field(alias='@attr')
