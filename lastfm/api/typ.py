#!/usr/bin/env python3

import typing
import uuid
import xml.etree.ElementTree

import pydantic

json = typing.Dict[str, typing.Any]
xml = xml.etree.ElementTree.Element
response = typing.Union[json, xml]

# typevar = typing.TypeVar('typevar')
# array = typing.Union[typing.List[typevar], typing.Set[typevar], typing.Tuple[typevar]]

lang = pydantic.typing.Annotated[str, pydantic.Field(min_length=3, max_length=3)]
tags = pydantic.typing.Annotated[typing.List[str], pydantic.Field(max_items=10)]
# tags = pydantic.typing.Annotated[array[str], pydantic.Field(max_items=10)]


class UUID(uuid.UUID):

    def __str__(self):
        return uuid.UUID(self.hex).hex

    def __repr__(self):
        return f'{self.__module__}.{self.__class__.__name__}({uuid.UUID.__str__(self)!r})'

    @classmethod
    def __get_validators__(cls):
        # https://docs.pydantic.dev/usage/types/#custom-data-types
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, str):
            return cls(v)
        else:
            return v
