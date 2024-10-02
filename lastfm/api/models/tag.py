#!/usr/bin/env python3

import typing
import uuid

import pydantic

from api.models import common


class Attr(common.BaseModel):
    tag: typing.Optional[str] = None


'''tag.getInfo'''


class Tag(common.BaseModel):
    name: str
    total: int
    reach: int
    wiki: common.Wiki


'''tag.getSimilar'''


class SimilarTag(common.BaseModel):
    name: str
    url: pydantic.HttpUrl
    streamable: bool


class Similartags(common.BaseModel):
    tag: typing.List[SimilarTag]
    attr: Attr = pydantic.Field(alias='@attr')


'''tag.getTopAlbums'''


class Album(common.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID] = None
    url: pydantic.HttpUrl
    image: typing.List[common.Image]
    artist: common.Entity
    attr: common.Rank = pydantic.Field(alias='@attr')


class Albums(common.BaseModel):
    album: typing.List[Album]
    tag: common.AttrTag = pydantic.Field(alias='@attr')


'''tag.getTopArtists'''


class Artist(common.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID] = None
    url: pydantic.HttpUrl
    image: typing.List[common.Image]
    streamable: bool
    attr: common.Rank = pydantic.Field(alias='@attr')


class Topartists(common.BaseModel):
    artist: typing.List[Artist]
    tag: common.AttrTag = pydantic.Field(alias='@attr')


'''tag.getTopTags'''


class AttrTopTag(common.BaseModel):
    offset: int
    num_res: int
    total: int


class TopTag(common.BaseModel):
    name: str
    count: int
    reach: int


class Toptags(common.BaseModel):
    tag: typing.List[TopTag]
    attr: AttrTopTag = pydantic.Field(alias='@attr')


'''tag.getTopTracks'''


class Track(common.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID] = None
    url: pydantic.HttpUrl
    image: typing.List[common.Image]
    duration: int
    artist: common.Entity
    streamable: common.Streamable
    attr: common.Rank = pydantic.Field(alias='@attr')


class Tracks(common.BaseModel):
    track: typing.List[Track]
    tag: common.AttrTag = pydantic.Field(alias='@attr')


'''tag.getWeeklyChartList'''


class Weekly(common.BaseModel):
    text: typing.Optional[str] = pydantic.Field(alias='#text', default=None)
    fr: int = pydantic.Field(alias='from')
    to: int


class Weeklychartlist(common.BaseModel):
    chart: typing.List[Weekly]
    attr: Attr = pydantic.Field(alias='@attr')
