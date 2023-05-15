#!/usr/bin/env python3

import typing
import uuid

import pydantic

from api.models import common


'''library.getArtists'''


class Artist(common.BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID]
    url: pydantic.HttpUrl
    image: typing.List[common.Image]
    playcount: int
    tagcount: int
    streamable: bool


class Artists(common.BaseModel):
    artist: typing.List[Artist]
    attr: common.AttrUser = pydantic.Field(alias='@attr')
