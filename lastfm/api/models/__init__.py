#!/usr/bin/env python3

import enum
import typing

import pydantic

def validateEmptyString(field: str) -> classmethod:

    def nullEmptyString(val: str) -> typing.Optional[str]:
        '''Return `None` if `val` a literal "none" str or an empty str'''
        if isinstance(val, str) and (val.lower() == 'none' or not val.strip()):
            return None
        else:
            return val

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
