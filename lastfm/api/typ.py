#!/usr/bin/env python3

import typing
import uuid
import xml.etree.ElementTree

json = typing.Dict[str, typing.Any]
xml = xml.etree.ElementTree.Element
response = typing.Union[json, xml]

uuid = typing.Union[str, uuid.UUID]

def array(t: type = None) -> typing._GenericAlias:
    return typing.Union[typing.List[t], typing.Set[t], typing.Tuple[t]]
