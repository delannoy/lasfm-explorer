#!/usr/bin/env python3

import datetime
import typing
import uuid

import pydantic

import models


class Attr(models.BaseModel):
    artist: str


'''artist.getCorrection'''


class AttrCorrection(models.BaseModel):
    index: int


class ArtistCorrection(models.BaseModel):
    artist: models.Entity
    attr: AttrCorrection = pydantic.Field(alias='@attr')


class Corrections(models.BaseModel):
    correction: ArtistCorrection


'''artist.getInfo'''


class Link(models.BaseModel):
    text: typing.Optional[str] = pydantic.Field(alias='#text')
    rel: str
    href: pydantic.HttpUrl


class Links(models.BaseModel):
    link: Link


class Bio(models.BaseModel):
    links: Links
    published: datetime.datetime
    summary: str
    content: typing.Optional[str]
    _ = models.validateDateTime('published')


class Stats(models.BaseModel):
    listeners: int
    playcount: int
    userplaycount: int


class SimilarArtist(models.BaseModel):
    name: str
    url: pydantic.HttpUrl
    image: typing.List[models.Image]


class Similar(models.BaseModel):
    artist: typing.List[SimilarArtist]


class ArtistTags(models.BaseModel):
    tag: typing.List[models.Tag]


class Artist(models.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID]
    url: pydantic.HttpUrl
    image: typing.List[models.Image]
    bio: Bio
    stats: Stats
    similar: Similar
    tags: ArtistTags
    streamable: bool
    ontour: bool


'''artist.getSimilar'''


class SimilarArtist(models.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID]
    url: pydantic.HttpUrl
    image: typing.List[models.Image]
    match: float
    streamable: bool


class SimilarArtists(models.BaseModel):
    artist: typing.List[SimilarArtist]
    attr: Attr = pydantic.Field(alias='@attr')


'''artist.getTags'''


class Tags(models.BaseModel):
    tag: typing.Optional[typing.List[models.Tag]]
    text: typing.Optional[str] = pydantic.Field(alias='#text')
    attr: Attr = pydantic.Field(alias='@attr')


'''artist.getTopAlbums'''


class Album(models.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID]
    url: pydantic.HttpUrl
    image: typing.List[models.Image]
    artist: models.Entity
    playcount: int


class Topalbums(models.BaseModel):
    album: typing.List[Album]
    attr: models.AttrArtist = pydantic.Field(alias='@attr')


'''artist.getTopTags'''


class Toptags(models.BaseModel):
    tag: typing.List[models.TopTag]
    attr: Attr = pydantic.Field(alias='@attr')


'''artist.getTopTracks'''


class Track(models.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID]
    url: pydantic.HttpUrl
    image: typing.List[models.Image]
    artist: models.Entity
    playcount: int
    listeners: int
    streamable: bool
    attr: models.Rank = pydantic.Field(alias='@attr')


class Toptracks(models.BaseModel):
    '''artist.getTopTracks'''
    track: typing.List[Track]
    attr: models.AttrArtist = pydantic.Field(alias='@attr')


'''artist.search'''


class ArtistMatch(models.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID]
    url: pydantic.HttpUrl
    image: typing.List[models.Image]
    listeners: int
    streamable: bool


class ArtistMatches(models.BaseModel):
    artist: typing.List[ArtistMatch]


class Results(models.BaseModel):
    artistmatches: ArtistMatches
    opensearch_Query: models.AttrOpensearchQuery = pydantic.Field(alias='opensearch:Query')
    opensearch_totalResults: str = pydantic.Field(alias='opensearch:totalResults')
    opensearch_startIndex: str = pydantic.Field(alias='opensearch:startIndex')
    opensearch_itemsPerPage: str = pydantic.Field(alias='opensearch:itemsPerPage')
    attr: models.AttrQuery = pydantic.Field(alias='@attr')
