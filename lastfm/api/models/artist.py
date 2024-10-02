#!/usr/bin/env python3

import datetime
import typing
import uuid

import pydantic

from api.models import common


class Attr(common.BaseModel):
    artist: str


'''artist.getCorrection'''


class AttrCorrection(common.BaseModel):
    index: int


class ArtistCorrection(common.BaseModel):
    artist: common.Entity
    attr: AttrCorrection = pydantic.Field(alias='@attr')


class Corrections(common.BaseModel):
    correction: ArtistCorrection


'''artist.getInfo'''


class Link(common.BaseModel):
    text: typing.Optional[str] = pydantic.Field(alias='#text', default=None)
    rel: str
    href: pydantic.HttpUrl


class Links(common.BaseModel):
    link: Link


class Bio(common.BaseModel):
    links: Links
    published: datetime.datetime
    summary: str
    content: typing.Optional[str] = None
    _ = common.validateDateTime('published')


class Stats(common.BaseModel):
    listeners: int
    playcount: int
    userplaycount: typing.Optional[int] = None


class SimilarArtistInfo(common.BaseModel):
    name: typing.Optional[str] = None # ugh! https://www.last.fm/music/None
    url: pydantic.HttpUrl
    image: typing.List[common.Image]


class SimilarArtistsInfo(common.BaseModel):
    artist: typing.List[SimilarArtistInfo]


class ArtistTags(common.BaseModel):
    tag: typing.List[common.Tag]


class Artist(common.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID] = None
    url: pydantic.HttpUrl
    image: typing.List[common.Image]
    bio: Bio
    stats: Stats
    similar: SimilarArtistsInfo
    tags: ArtistTags
    streamable: bool
    ontour: bool


'''artist.getSimilar'''


class SimilarArtist(common.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID] = None
    url: pydantic.HttpUrl
    image: typing.List[common.Image]
    match: float
    streamable: bool


class Similarartists(common.BaseModel):
    artist: typing.List[SimilarArtist]
    attr: Attr = pydantic.Field(alias='@attr')


'''artist.getTags'''


class Tags(common.BaseModel):
    tag: typing.Optional[typing.List[common.Tag]] = None
    text: typing.Optional[str] = pydantic.Field(alias='#text', default=None)
    attr: Attr = pydantic.Field(alias='@attr')


'''artist.getTopAlbums'''


class Album(common.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID] = None
    url: pydantic.HttpUrl
    image: typing.List[common.Image]
    artist: common.Entity
    playcount: int


class Topalbums(common.BaseModel):
    album: typing.List[Album]
    attr: common.AttrArtist = pydantic.Field(alias='@attr')


'''artist.getTopTags'''


class Toptags(common.BaseModel):
    tag: typing.List[common.TopTag]
    attr: Attr = pydantic.Field(alias='@attr')


'''artist.getTopTracks'''


class Track(common.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID] = None
    url: pydantic.HttpUrl
    image: typing.List[common.Image]
    artist: common.Entity
    playcount: int
    listeners: int
    streamable: bool
    attr: common.Rank = pydantic.Field(alias='@attr')


class Toptracks(common.BaseModel):
    track: typing.List[Track]
    attr: common.AttrArtist = pydantic.Field(alias='@attr')


'''artist.search'''


class ArtistMatch(common.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID] = None
    url: pydantic.HttpUrl
    image: typing.List[common.Image]
    listeners: int
    streamable: bool


class ArtistMatches(common.BaseModel):
    artist: typing.List[ArtistMatch]


class Results(common.BaseModel):
    artistmatches: ArtistMatches
    opensearch_Query: common.AttrOpensearchQuery = pydantic.Field(alias='opensearch:Query')
    opensearch_totalResults: str = pydantic.Field(alias='opensearch:totalResults')
    opensearch_startIndex: str = pydantic.Field(alias='opensearch:startIndex')
    opensearch_itemsPerPage: str = pydantic.Field(alias='opensearch:itemsPerPage')
    attr: common.AttrQuery = pydantic.Field(alias='@attr')
