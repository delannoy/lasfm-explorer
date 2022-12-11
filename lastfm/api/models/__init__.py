#!/usr/bin/env python3

import datetime
import enum
import typing
import uuid

import dateparser
import pydantic

def validateDateTime(field: str) -> classmethod:
    # https://github.com/pydantic/pydantic/issues/940#issuecomment-569765091

    def parseDateTime(dt: str) -> datetime.datetime:
        return dateparser.parse(str(dt), settings={'TIMEZONE': 'UTC'}) # [Python 3.9 PytzUsageWarning](https://github.com/scrapinghub/dateparser/issues/1013#issuecomment-1109403189)

    return pydantic.validator(field, pre=True, allow_reuse=True)(parseDateTime)

def validateEmptyField(field: typing.Any) -> classmethod:

    def nullString(val: typing.Any) -> typing.Any:
        '''Return `None` if `val` a literal "none" str or an empty str'''
        if isinstance(val, str) and (val.lower() == 'none' or not val.strip()):
            return None
        else:
            return val

    return pydantic.validator(field, pre=True, allow_reuse=True)(nullString)


class ImageSize(str, enum.Enum):
    SMALL = 'small'
    MEDIUM = 'medium'
    LARGE = 'large'
    EXTRALARGE = 'extralarge'
    MEGA = 'mega'


class BaseModel(pydantic.BaseModel, extra=pydantic.Extra.forbid):
    _ = validateEmptyField('*')


class AttrUser(BaseModel):
    user: str
    page: int
    perPage: int
    totalPages: int
    total: int


class Entity(BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID]
    url: pydantic.HttpUrl


class Image(BaseModel):
    size: typing.Optional[ImageSize]
    url: typing.Optional[pydantic.HttpUrl] = pydantic.Field(alias='#text')


class Rank(BaseModel):
    rank: int


class Streamable(BaseModel):
    fulltrack: bool
    streamable: bool = pydantic.Field(alias='#text')
