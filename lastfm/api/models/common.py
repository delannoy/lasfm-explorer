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
        return dateparser.parse(str(dt), settings=dict(TIMEZONE='UTC', RETURN_AS_TIMEZONE_AWARE=True))

    return pydantic.validator(field, pre=True, allow_reuse=True)(parseDateTime)

def validateEmptyField(field: typing.Any) -> classmethod:

    def nullString(val: typing.Any) -> typing.Any:
        '''Return `None` if `val` is an empty string or a literal "none", "n/a", "fixme" string'''
        if isinstance(val, str) and (val.lower() in ('none', 'n/a', 'fixme') or not val.strip()):
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


class UserType(enum.Enum):
    USER: str = 'user'
    SUBCRIBER: str = 'subscriber'


class BaseModel(pydantic.BaseModel, extra=pydantic.Extra.forbid):
    _ = validateEmptyField('*')


class AttrOpensearchQuery(BaseModel):
    text: typing.Optional[str] = pydantic.Field(alias='#text', default=None)
    role: str
    startPage: int
    searchTerms: typing.Optional[str] = None


class AttrQuery(BaseModel):
    query: typing.Optional[str] = pydantic.Field(alias='for', default=None)


class AttrArtist(BaseModel):
    artist: str
    page: int
    perPage: int
    totalPages: int
    total: int


class AttrTag(BaseModel):
    tag: str
    page: int
    perPage: int
    totalPages: int
    total: int


class AttrUser(BaseModel):
    user: str
    page: int
    perPage: int
    totalPages: int
    total: int


class AttrWeekly(BaseModel):
    user: str
    fr: int = pydantic.Field(alias='from')
    to: int


class Date(BaseModel):
    uts: int
    dateTime: datetime.datetime = pydantic.Field(alias='#text')
    _ = validateDateTime('dateTime')


class Entity(BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID] = None
    url: pydantic.HttpUrl


class Artist(BaseModel):
    name: str = pydantic.Field(alias='#text')
    mbid: typing.Optional[uuid.UUID] = None


class Album(BaseModel):
    name: typing.Optional[str] = pydantic.Field(alias='#text')
    mbid: typing.Optional[uuid.UUID] = None


class Image(BaseModel):
    size: typing.Optional[ImageSize] = None
    url: typing.Optional[pydantic.HttpUrl] = pydantic.Field(alias='#text', default=None)


# class Images(BaseModel):
#     image_small: typing.Optional[pydantic.HttpUrl]
#     image_medium: typing.Optional[pydantic.HttpUrl]
#     image_extralarge: typing.Optional[pydantic.HttpUrl]
#     image_mega: typing.Optional[pydantic.HttpUrl]
# 
#     @pydantic.root_validator(pre=True)
#     # [Flatten nested Pydantic model](https://stackoverflow.com/a/75289709)
#     def flatten_images(cls, values):
#         images = values.get('image')
#         if images is None:
#             return values
#     # {i.size: i.url for i in models.geo.Artist(**geo.getTopArtists(country=country1, limit=1).get('topartists').get('artist')[0]).image}


class Rank(BaseModel):
    rank: int


class Registered(BaseModel):
    unixtime: int
    dateTime: datetime.datetime = pydantic.Field(alias='#text')
    _ = validateDateTime('dateTime')


class Streamable(BaseModel):
    fulltrack: bool
    streamable: bool = pydantic.Field(alias='#text')


class Tag(BaseModel):
    name: str
    url: pydantic.HttpUrl


class TopTag(BaseModel):
    name: str
    url: pydantic.HttpUrl
    count: int


class Wiki(BaseModel):
    published: typing.Optional[datetime.datetime] = None
    summary: typing.Optional[str] = None
    content: typing.Optional[str] = None
    _ = validateDateTime('published')
