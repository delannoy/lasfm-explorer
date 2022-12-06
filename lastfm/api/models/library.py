#!/usr/bin/env python3

import typing
import uuid

import pydantic

import models


'''library.getArtists'''


class Artist(models.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID]
    url: pydantic.HttpUrl
    image: typing.List[models.Image]
    playcount: int
    tagcount: int
    streamable: bool


class Artists(models.BaseModel):
    artist: typing.List[Artist]
    attr: models.AttrUser = pydantic.Field(alias='@attr')
