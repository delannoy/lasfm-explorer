#!/usr/bin/env python3

from __future__ import annotations
import uuid

import awkward

import request

'''You can perform a lookup of an entity when you have the MBID for that entity'''
# https://musicbrainz.org/doc/MusicBrainz_API#Lookups

def genreAll(limit: int = None, offset: int = 0, fmt: str = None) -> awkward.Record:
    return request.get(endpoint='/genre/all', limit=limit, offset=offset)

def lookup(entity: str, mbid: uuid.UUID, inc: list[str] = None, type: list[str] = None, status: list[str] = None) -> awkward.Record:
    inc = str.join('+', inc) if inc else None
    type = str.join('|', type) if type else None
    status = str.join('|', status) if status else None
    return request.get(endpoint=f'/{entity}/{mbid}', inc=inc, type=type, status=status)

def area(mbid: uuid.UUID, inc: list[str] = None) -> awkward.Record:
    return lookup(entity='area', mbid=mbid, inc=inc)

def artist(mbid: uuid.UUID, inc: list[str] = None, type: list[str] = None, status: list[str] = None) -> awkward.Record:
    return lookup(entity='artist', mbid=mbid, inc=inc, type=type, status=status)

def collection(mbid: uuid.UUID, inc: list[str] = None) -> awkward.Record:
    return lookup(entity='collection', mbid=mbid, inc=inc)

def event(mbid: uuid.UUID, inc: list[str] = None) -> awkward.Record:
    return lookup(entity='event', mbid=mbid, inc=inc)

def genre(mbid: uuid.UUID, inc: list[str] = None) -> awkward.Record:
    return lookup(entity='genre', mbid=mbid, inc=inc)

def instrument(mbid: uuid.UUID, inc: list[str] = None) -> awkward.Record:
    return lookup(entity='instrument', mbid=mbid, inc=inc)

def label(mbid: uuid.UUID, inc: list[str] = None, type: list[str] = None, status: list[str] = None) -> awkward.Record:
    return lookup(entity='label', mbid=mbid, inc=inc, type=type, status=status)

def place(mbid: uuid.UUID, inc: list[str] = None) -> awkward.Record:
    return lookup(entity='place', mbid=mbid, inc=inc)

def recording(mbid: uuid.UUID, inc: list[str] = None, type: list[str] = None, status: list[str] = None) -> awkward.Record:
    return lookup(entity='recording', mbid=mbid, inc=inc, type=type, status=status)

def release(mbid: uuid.UUID, inc: list[str] = None, type: list[str] = None) -> awkward.Record:
    return lookup(entity='release', mbid=mbid, inc=inc, type=type)

def release_group(mbid: uuid.UUID, inc: list[str] = None, type: list[str] = None, status: list[str] = None) -> awkward.Record:
    return lookup(entity='release-group', mbid=mbid, inc=inc, type=type, status=status)

def series(mbid: uuid.UUID, inc: list[str] = None) -> awkward.Record:
    return lookup(entity='series', mbid=mbid, inc=inc)

def url(mbid: uuid.UUID = None, inc: list[str] = None) -> awkward.Record:
    return lookup(entity='url', mbid=mbid, inc=inc)

def work(mbid: uuid.UUID, inc: list[str] = None) -> awkward.Record:
    return lookup(entity='work', mbid=mbid, inc=inc)

# [Non-MBID Lookups](https://musicbrainz.org/doc/MusicBrainz_API#Non-MBID_Lookups)

def discid(discid: str, inc: list[str] = None, toc: list[int] = None, cdstubs: bool = True, media_format: str = 'CD') -> awkward.Record:
    return request.get(endpoint=f'/discid/{discid}', inc=str.join('+', inc), toc=str.join('+', toc), cdstubs='no' if not cdstubs else '', **{'media-format': media_format})

def isrc(isrc: str, inc: list[str] = None) -> awkward.Record:
    return request.get(endpoint=f'/isrc/{isrc}', inc=str.join('+', inc))

def iswc(iswc: str, inc: list[str] = None) -> awkward.Record:
    return request.get(endpoint=f'/iswc/{iswc}', inc=str.join('+', inc))
