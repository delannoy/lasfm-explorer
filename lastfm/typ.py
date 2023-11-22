#!/usr/bin/env python3

import datetime
import typing
import uuid
import xml.etree.ElementTree

import dateparser
import pydantic


class Bool:

    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return f'{self.__module__}.{self.__class__.__name__}({self.value!r})'

    def __str__(self):
        return str(int(bool(self.value)))

    @classmethod
    def __get_validators__(cls):
        # https://docs.pydantic.dev/usage/types/#custom-data-types
        yield cls.validate

    @classmethod
    def validate(cls, v) -> int:
        return int(pydantic.validators.bool_validator(v))


class UnixTimestamp:

    def parseDateTime(dt: str, tz: str = 'UTC') -> datetime.datetime:
        return dateparser.parse(dt) if dateparser.parse(dt).tzinfo else dateparser.parse(f'{dt} {tz}')

    def unixtimestamp(dt: datetime.datetime) -> int:
        return int(dt.timestamp())

    @classmethod
    def __get_validators__(cls):
        # https://docs.pydantic.dev/usage/types/#custom-data-types
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if isinstance(v, str):
            return cls.unixtimestamp(cls.parseDateTime(v))
        elif isinstance(v, datetime.datetime):
            return cls.unixtimestamp(v)
        elif isinstance(v, float):
            return int(v)
        else:
            return v


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


json = typing.Dict[str, typing.Any]
xml = xml.etree.ElementTree.Element
response = typing.Union[json, xml]

# typevar = typing.TypeVar('typevar')
# array = typing.Union[typing.List[typevar], typing.Set[typevar], typing.Tuple[typevar]]

lang = pydantic.typing.Annotated[str, pydantic.Field(min_length=3, max_length=3)]

tags = pydantic.typing.Annotated[typing.List[str], pydantic.Field(max_items=10)]

artist = pydantic.typing.Annotated[typing.List[str], pydantic.Field(max_items=50)]
track = pydantic.typing.Annotated[typing.List[str], pydantic.Field(max_items=50)]
timestamp = pydantic.typing.Annotated[typing.List[UnixTimestamp], pydantic.Field(max_items=50)]
album = pydantic.typing.Annotated[typing.List[str], pydantic.Field(max_items=50)]
mbid = pydantic.typing.Annotated[typing.List[uuid.UUID], pydantic.Field(max_items=50)]
trackNumber = pydantic.typing.Annotated[typing.List[int], pydantic.Field(max_items=50)]
albumArtist = pydantic.typing.Annotated[typing.List[str], pydantic.Field(max_items=50)]
duration = pydantic.typing.Annotated[typing.List[int], pydantic.Field(max_items=50)]
context = pydantic.typing.Annotated[typing.List[str], pydantic.Field(max_items=50)]
streamId = pydantic.typing.Annotated[typing.List[str], pydantic.Field(max_items=50)]
chosenByUser = pydantic.typing.Annotated[typing.List[bool], pydantic.Field(max_items=50)]
