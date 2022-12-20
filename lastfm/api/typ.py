#!/usr/bin/env python3

import typing
import uuid
import xml.etree.ElementTree

import pydantic

json = typing.Dict[str, typing.Any]
xml = xml.etree.ElementTree.Element
response = typing.Union[json, xml]

lang = pydantic.typing.Annotated[str, pydantic.Field(min_length=3, max_length=3)]
tags = pydantic.typing.Annotated[typing.List[str], pydantic.Field(max_items=10)]


class UUID(uuid.UUID):

    def __str__(self):
        return uuid.UUID(self.hex).hex

    def __repr__(self):
        return f'{self.__module__}.{self.__class__.__name__}({uuid.UUID.__str__(self)!r})'
