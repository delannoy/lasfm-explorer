#!/usr/bin/env python3

import enum
import typing

import pydantic

def validateEmptyString(field: str) -> classmethod:

    def nullEmptyString(val: str) -> typing.Optional[str]:
        if not isinstance(val, str):
            return val
        if val.lower() == 'none':
            return None
        return val if val.strip() else None

    return pydantic.validator(field, pre=True, allow_reuse=True)(nullEmptyString)


class ImageSize(str, enum.Enum):
    SMALL = 'small'
    MEDIUM = 'medium'
    LARGE = 'large'
    EXTRALARGE = 'extralarge'
    MEGA = 'mega'


class BaseModel(pydantic.BaseModel, extra=pydantic.Extra.forbid):

    _ = validateEmptyString('*')


class AttrUser(BaseModel):
    user: str
    page: int
    perPage: int
    totalPages: int
    total: int


class Image(BaseModel):
    size: typing.Optional[ImageSize]
    url: typing.Optional[pydantic.HttpUrl] = pydantic.Field(alias='#text')
