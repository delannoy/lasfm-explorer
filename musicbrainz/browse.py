#!/usr/bin/env python3

from __future__ import annotations
import uuid

import awkward

import api
import request

'''Browse requests are a direct lookup of all the entities directly linked to another entity ("directly linked" meaning it does not include entities linked by a relationship)'''
# https://musicbrainz.org/doc/MusicBrainz_API#Browse

def browse(entity: str, linked_entity: dict[str, uuid.UUID] = None, inc: list[str] = None, type: list[str] = None, status: list[str] = None, offset: int = 0, limit: int = 25, **kwargs) -> awkward.Record:
    linked_entity = linked_entity if linked_entity else kwargs
    inc = str.join('+', inc) if inc else None
    type = str.join('|', type) if type else None
    status = str.join('|', status) if status else None
    return request.get(endpoint=f'/{entity}', inc=inc, type=type, status=status, offset=offset, limit=limit, **linked_entity)

def area(linked_entity: dict[str, uuid.UUID] = None, inc: list[str] = None, offset: int = 0, limit: int = 25, **kwargs) -> awkward.Record:
    return browse(entity='area', linked_entity=linked_entity, inc=inc, offset=offset, limit=limit, **kwargs)

def artist(linked_entity: dict[str, uuid.UUID] = None, inc: list[str] = None, offset: int = 0, limit: int = 25, **kwargs) -> awkward.Record:
    return browse(entity='artist', linked_entity=linked_entity, inc=inc, offset=offset, limit=limit, **kwargs)

def collection(linked_entity: dict[str, uuid.UUID] = None, inc: list[str] = None, offset: int = 0, limit: int = 25, **kwargs) -> awkward.Record:
    return browse(entity='collection', linked_entity=linked_entity, inc=inc, offset=offset, limit=limit, **kwargs)

def event(linked_entity: dict[str, uuid.UUID] = None, inc: list[str] = None, offset: int = 0, limit: int = 25, **kwargs) -> awkward.Record:
    return browse(entity='event', linked_entity=linked_entity, inc=inc, offset=offset, limit=limit, **kwargs)

def instrument(linked_entity: dict[str, uuid.UUID] = None, inc: list[str] = None, offset: int = 0, limit: int = 25, **kwargs) -> awkward.Record:
    return browse(entity='instrument', linked_entity=linked_entity, inc=inc, offset=offset, limit=limit, **kwargs)

def label(linked_entity: dict[str, uuid.UUID] = None, inc: list[str] = None, offset: int = 0, limit: int = 25, **kwargs) -> awkward.Record:
    return browse(entity='label', linked_entity=linked_entity, inc=inc, offset=offset, limit=limit, **kwargs)

def place(linked_entity: dict[str, uuid.UUID] = None, inc: list[str] = None, offset: int = 0, limit: int = 25, **kwargs) -> awkward.Record:
    return browse(entity='place', linked_entity=linked_entity, inc=inc, offset=offset, limit=limit, **kwargs)

def recording(linked_entity: dict[str, uuid.UUID] = None, inc: list[str] = None, offset: int = 0, limit: int = 25, **kwargs) -> awkward.Record:
    return browse(entity='recording', linked_entity=linked_entity, inc=inc, offset=offset, limit=limit, **kwargs)

def release(linked_entity: dict[str, uuid.UUID] = None, inc: list[str] = None, type: list[str] = None, status: list[str] = None, offset: int = 0, limit: int = 25, **kwargs) -> awkward.Record:
    return browse(entity='release', linked_entity=linked_entity, inc=inc, offset=offset, limit=limit, **kwargs)

def release_group(linked_entity: dict[str, uuid.UUID] = None, inc: list[str] = None, type: list[str] = None, offset: int = 0, limit: int = 25, **kwargs) -> awkward.Record:
    return browse(entity='release-group', linked_entity=linked_entity, inc=inc, offset=offset, limit=limit, **kwargs)

def series(linked_entity: dict[str, uuid.UUID] = None, inc: list[str] = None, offset: int = 0, limit: int = 25, **kwargs) -> awkward.Record:
    return browse(entity='series', linked_entity=linked_entity, inc=inc, offset=offset, limit=limit, **kwargs)

def work(linked_entity: dict[str, uuid.UUID] = None, inc: list[str] = None, offset: int = 0, limit: int = 25, **kwargs) -> awkward.Record:
    return browse(entity='work', linked_entity=linked_entity, inc=inc, offset=offset, limit=limit, **kwargs)

def url(linked_entity: dict[str, uuid.UUID] = None, inc: list[str] = None, offset: int = 0, limit: int = 25, **kwargs) -> awkward.Record:
    return browse(entity='url', linked_entity=linked_entity, inc=inc, offset=offset, limit=limit, **kwargs)
