#!/usr/bin/env python3

from __future__ import annotations
import enum
import uuid

import awkward

import api
import request

'''You can perform a lookup of an entity when you have the MBID for that entity'''
# https://musicbrainz.org/doc/MusicBrainz_API#Lookups


class CollectionType(str, enum.Enum):
    AREAS = 'areas'
    ARTISTS = 'artists'
    EVENTS = 'events'
    INSTRUMENTS = 'instruments'
    LABELS = 'labels'
    PLACES = 'places'
    RECORDINGS = 'recordings'
    RELEASES = 'releases'
    RELEASE_GROUPS = 'release-groups'
    SERIES = 'series'
    WORKS = 'works'


class Inc:

    @classmethod
    def get(cls, attr):
        return getattr(cls, attr)

    @classmethod
    def enums(cls):
        return [attr for attr, typ in vars(cls).items() if isinstance(typ, enum.EnumMeta)]

    class Area(str, enum.Enum):
        ALIASES = 'aliases'
        ANNOTATION = 'annotation'
        GENRES = 'genres'
        RATINGS = 'ratings'
        TAGS = 'tags'
        USER_GENRES = 'user-genres'
        USER_RATINGS = 'user-ratings'
        USER_TAGS = 'user-tags'
        AREA_RELS = 'area-rels'
        ARTIST_RELS = 'artist-rels'
        EVENT_RELS = 'event-rels'
        INSTRUMENT_RELS = 'instrument-rels'
        LABEL_RELS = 'label-rels'
        PLACE_RELS = 'place-rels'
        RECORDING_RELS = 'recording-rels'
        RELEASE_RELS = 'release-rels'
        RELEASE_GROUP_RELS = 'release-group-rels'
        SERIES_RELS = 'series-rels'
        URL_RELS = 'url-rels'
        WORK_RELS = 'work-rels'
        ARTIST_CREDITS = 'artist-credits' # requires `release-rels`, `recording-rels`, or `release-group-rels`

    class Artist(str, enum.Enum):
        RECORDINGS = 'recordings'
        RELEASE_GROUPS = 'release-groups'
        RELEASES = 'releases'
        WORKS = 'works'
        ALIASES = 'aliases'
        ANNOTATION = 'annotation'
        GENRES = 'genres'
        RATINGS = 'ratings'
        TAGS = 'tags'
        USER_GENRES = 'user-genres'
        USER_RATINGS = 'user-ratings'
        USER_TAGS = 'user-tags'
        AREA_RELS = 'area-rels'
        ARTIST_RELS = 'artist-rels'
        EVENT_RELS = 'event-rels'
        INSTRUMENT_RELS = 'instrument-rels'
        LABEL_RELS = 'label-rels'
        PLACE_RELS = 'place-rels'
        RECORDING_RELS = 'recording-rels'
        RELEASE_RELS = 'release-rels'
        RELEASE_GROUP_RELS = 'release-group-rels'
        SERIES_RELS = 'series-rels'
        URL_RELS = 'url-rels'
        WORK_RELS = 'work-rels'
        ARTIST_CREDITS = 'artist-credits' # requires `recordings`, `release-groups`, `works`, `release-rels`, `recording-rels`, `release-group-rels`, or `releases`
        DISCIDS = 'discids' # requires `releases`
        ISCRCS = 'isrcs' # requires `recordings`
        MEDIA = 'media' # requires `releases`
        VARIOUS_ARTISTS = 'various-artists' # requires `releases`

    class Collection(str, enum.Enum):
        ARTISTS = 'artists'
        LABELS = 'labels'
        RECORDINGS = 'recordings'
        RELEASE_GROUPS = 'release-groups'
        RELEASES = 'releases'
        WORKS = 'works'
        TAGS = 'tags'
        ARTIST_CREDITS = 'artist-credits' # requires `recordings`, `release-groups`, `works`, or `releases`
        DISCIDS = 'discids' # requires `releases`
        ISCRCS = 'isrcs' # requires `recordings`
        MEDIA = 'media' # requires `releases`

    class Event(str, enum.Enum):
        ALIASES = 'aliases'
        ANNOTATION = 'annotation'
        GENRES = 'genres'
        RATINGS = 'ratings'
        TAGS = 'tags'
        USER_GENRES = 'user-genres'
        USER_RATINGS = 'user-ratings'
        USER_TAGS = 'user-tags'
        AREA_RELS = 'area-rels'
        ARTIST_RELS = 'artist-rels'
        EVENT_RELS = 'event-rels'
        INSTRUMENT_RELS = 'instrument-rels'
        LABEL_RELS = 'label-rels'
        PLACE_RELS = 'place-rels'
        RECORDING_RELS = 'recording-rels'
        RELEASE_RELS = 'release-rels'
        RELEASE_GROUP_RELS = 'release-group-rels'
        SERIES_RELS = 'series-rels'
        URL_RELS = 'url-rels'
        WORK_RELS = 'work-rels'
        ARTIST_CREDITS = 'artist-credits' # requires `release-rels`, `recording-rels`, or `release-group-rels`

    class Instrument(str, enum.Enum):
        ALIASES = 'aliases'
        ANNOTATION = 'annotation'
        GENRES = 'genres'
        TAGS = 'tags'
        USER_GENRES = 'user-genres'
        USER_TAGS = 'user-tags'
        AREA_RELS = 'area-rels'
        ARTIST_RELS = 'artist-rels'
        EVENT_RELS = 'event-rels'
        INSTRUMENT_RELS = 'instrument-rels'
        LABEL_RELS = 'label-rels'
        PLACE_RELS = 'place-rels'
        RECORDING_RELS = 'recording-rels'
        RELEASE_RELS = 'release-rels'
        RELEASE_GROUP_RELS = 'release-group-rels'
        SERIES_RELS = 'series-rels'
        URL_RELS = 'url-rels'
        WORK_RELS = 'work-rels'
        ARTIST_CREDITS = 'artist-credits' # requires `release-rels`, `recording-rels`, or `release-group-rels`

    class Label(str, enum.Enum):
        RELEASES = 'releases'
        ALIASES = 'aliases'
        ANNOTATION = 'annotation'
        GENRES = 'genres'
        RATINGS = 'ratings'
        TAGS = 'tags'
        USER_GENRES = 'user-genres'
        USER_RATINGS = 'user-ratings'
        USER_TAGS = 'user-tags'
        AREA_RELS = 'area-rels'
        ARTIST_RELS = 'artist-rels'
        EVENT_RELS = 'event-rels'
        INSTRUMENT_RELS = 'instrument-rels'
        LABEL_RELS = 'label-rels'
        PLACE_RELS = 'place-rels'
        RECORDING_RELS = 'recording-rels'
        RELEASE_RELS = 'release-rels'
        RELEASE_GROUP_RELS = 'release-group-rels'
        SERIES_RELS = 'series-rels'
        URL_RELS = 'url-rels'
        WORK_RELS = 'work-rels'
        ARTIST_CREDITS = 'artist-credits'  # requires `release-rels`, `recording-rels`, `release-group-rels`, or `releases`
        DISCIDS = 'discids' # requires `releases`
        MEDIA = 'media' # requires `releases`

    class Place(str, enum.Enum):
        ALIASES = 'aliases'
        ANNOTATION = 'annotation'
        GENRES = 'genres'
        RATINGS = 'ratings'
        TAGS = 'tags'
        USER_GENRES = 'user-genres'
        USER_RATINGS = 'user-ratings'
        USER_TAGS = 'user-tags'
        AREA_RELS = 'area-rels'
        ARTIST_RELS = 'artist-rels'
        EVENT_RELS = 'event-rels'
        INSTRUMENT_RELS = 'instrument-rels'
        LABEL_RELS = 'label-rels'
        PLACE_RELS = 'place-rels'
        RECORDING_RELS = 'recording-rels'
        RELEASE_RELS = 'release-rels'
        RELEASE_GROUP_RELS = 'release-group-rels'
        SERIES_RELS = 'series-rels'
        URL_RELS = 'url-rels'
        WORK_RELS = 'work-rels'
        ARTIST_CREDITS = 'artist-credits' # requires `release-rels`, `recording-rels`, or `release-group-rels`

    class Recording(str, enum.Enum):
        ARTISTS = 'artists'
        RELEASE_GROUPS = 'release-groups'
        RELEASES = 'releases'
        ALIASES = 'aliases'
        ANNOTATION = 'annotation'
        GENRES = 'genres'
        RATINGS = 'ratings'
        TAGS = 'tags'
        USER_GENRES = 'user-genres'
        USER_RATINGS = 'user-ratings'
        USER_TAGS = 'user-tags'
        ARTIST_CREDITS = 'artist-credits'
        ISRCS = 'isrcs'
        AREA_RELS = 'area-rels'
        ARTIST_RELS = 'artist-rels'
        EVENT_RELS = 'event-rels'
        INSTRUMENT_RELS = 'instrument-rels'
        LABEL_RELS = 'label-rels'
        PLACE_RELS = 'place-rels'
        RECORDING_RELS = 'recording-rels'
        RELEASE_RELS = 'release-rels'
        RELEASE_GROUP_RELS = 'release-group-rels'
        SERIES_RELS = 'series-rels'
        URL_RELS = 'url-rels'
        WORK_RELS = 'work-rels'
        WORK_LEVEL_RELS = 'work-level-rels'
        DISCIDS = 'discids' # requires `releases`
        MEDIA = 'media' # requires `releases`

    class Release(str, enum.Enum):
        ARTISTS = 'artists'
        COLLECTIONS = 'collections'
        LABELS = 'labels'
        RECORDINGS = 'recordings'
        RELEASE_GROUPS = 'release-groups'
        ALIASES = 'aliases'
        ANNOTATION = 'annotation'
        GENRES = 'genres'
        RATINGS = 'ratings'
        TAGS = 'tags'
        USER_COLLECTIONS = 'user-collections'
        USER_GENRES = 'user-genres'
        USER_RATINGS = 'user-ratings'
        USER_TAGS = 'user-tags'
        ARTIST_CREDITS = 'artist-credits'
        DISCIDS = 'discids'
        MEDIA = 'media'
        AREA_RELS = 'area-rels'
        ARTIST_RELS = 'artist-rels'
        EVENT_RELS = 'event-rels'
        INSTRUMENT_RELS = 'instrument-rels'
        LABEL_RELS = 'label-rels'
        PLACE_RELS = 'place-rels'
        RECORDING_RELS = 'recording-rels'
        RELEASE_RELS = 'release-rels'
        RELEASE_GROUP_RELS = 'release-group-rels'
        SERIES_RELS = 'series-rels'
        URL_RELS = 'url-rels'
        WORK_RELS = 'work-rels'
        RECORDING_LEVEL_RELS = 'recording-level-rels'
        RELEASE_GROUP_LEVEL_RELS = 'release-group-level-rels'
        WORK_LEVEL_RELS = 'work-level-rels'
        ISRCS = 'isrcs' # requires `recordings`

    class Release_group(str, enum.Enum):
        ARTISTS = 'artists'
        RELEASES = 'releases'
        ALIASES = 'aliases'
        ANNOTATION = 'annotation'
        GENRES = 'genres'
        RATINGS = 'ratings'
        TAGS = 'tags'
        USER_GENRES = 'user-genres'
        USER_RATINGS = 'user-ratings'
        USER_TAGS = 'user-tags'
        ARTIST_CREDITS = 'artist-credits'
        AREA_RELS = 'area-rels'
        ARTIST_RELS = 'artist-rels'
        EVENT_RELS = 'event-rels'
        INSTRUMENT_RELS = 'instrument-rels'
        LABEL_RELS = 'label-rels'
        PLACE_RELS = 'place-rels'
        RECORDING_RELS = 'recording-rels'
        RELEASE_RELS = 'release-rels'
        RELEASE_GROUP_RELS = 'release-group-rels'
        SERIES_RELS = 'series-rels'
        URL_RELS = 'url-rels'
        WORK_RELS = 'work-rels'
        DISCIDS = 'discids' # requires `releases`
        MEDIA = 'media' # requires `releases`

    class Series(str, enum.Enum):
        ALIASES = 'aliases'
        ANNOTATION = 'annotation'
        GENRES = 'genres'
        TAGS = 'tags'
        USER_GENRES = 'user-genres'
        USER_TAGS = 'user-tags'
        AREA_RELS = 'area-rels'
        ARTIST_RELS = 'artist-rels'
        EVENT_RELS = 'event-rels'
        INSTRUMENT_RELS = 'instrument-rels'
        LABEL_RELS = 'label-rels'
        PLACE_RELS = 'place-rels'
        RECORDING_RELS = 'recording-rels'
        RELEASE_RELS = 'release-rels'
        RELEASE_GROUP_RELS = 'release-group-rels'
        SERIES_RELS = 'series-rels'
        URL_RELS = 'url-rels'
        WORK_RELS = 'work-rels'
        ARTIST_CREDITS = 'artist-credits' # requires `release-rels`, `recording-rels`, or `release-group-rels`

    class Url(str, enum.Enum):
        AREA_RELS = 'area-rels'
        ARTIST_RELS = 'artist-rels'
        EVENT_RELS = 'event-rels'
        INSTRUMENT_RELS = 'instrument-rels'
        LABEL_RELS = 'label-rels'
        PLACE_RELS = 'place-rels'
        RECORDING_RELS = 'recording-rels'
        RELEASE_RELS = 'release-rels'
        RELEASE_GROUP_RELS = 'release-group-rels'
        SERIES_RELS = 'series-rels'
        URL_RELS = 'url-rels'
        WORK_RELS = 'work-rels'
        ARTIST_CREDITS = 'artist-credits' # requires `release-rels`, `recording-rels`, or `release-group-rels`

    class Work(str, enum.Enum):
        ALIASES = 'aliases'
        ANNOTATION = 'annotation'
        GENRES = 'genres'
        RATINGS = 'ratings'
        TAGS = 'tags'
        USER_GENRES = 'user-genres'
        USER_RATINGS = 'user-ratings'
        USER_TAGS = 'user-tags'
        AREA_RELS = 'area-rels'
        ARTIST_RELS = 'artist-rels'
        EVENT_RELS = 'event-rels'
        INSTRUMENT_RELS = 'instrument-rels'
        LABEL_RELS = 'label-rels'
        PLACE_RELS = 'place-rels'
        RECORDING_RELS = 'recording-rels'
        RELEASE_RELS = 'release-rels'
        RELEASE_GROUP_RELS = 'release-group-rels'
        SERIES_RELS = 'series-rels'
        URL_RELS = 'url-rels'
        WORK_RELS = 'work-rels'
        ARTIST_CREDITS = 'artist-credits' # requires `release-rels`, `recording-rels`, or `release-group-rels`

    class Discid(str, enum.Enum):
        ARTISTS = 'artists'
        LABELS = 'labels'
        RECORDINGS = 'recordings'
        RELEASE_GROUPS = 'release-groups'
        ALIASES = 'aliases'
        GENRES = 'genres'
        TAGS = 'tags'
        USER_GENRES = 'user-genres'
        USER_TAGS = 'user-tags'
        ARTIST_CREDITS = 'artist-credits'
        ISRCS = 'isrcs'
        AREA_RELS = 'area-rels'
        ARTIST_RELS = 'artist-rels'
        EVENT_RELS = 'event-rels'
        INSTRUMENT_RELS = 'instrument-rels'
        LABEL_RELS = 'label-rels'
        PLACE_RELS = 'place-rels'
        RECORDING_RELS = 'recording-rels'
        RELEASE_RELS = 'release-rels'
        RELEASE_GROUP_RELS = 'release-group-rels'
        SERIES_RELS = 'series-rels'
        URL_RELS = 'url-rels'
        WORK_RELS = 'work-rels'

    class Isrc(str, enum.Enum):
        ARTISTS = 'artists'
        RELEASES = 'releases'
        ALIASES = 'aliases'
        RATINGS = 'ratings'
        TAGS = 'tags'
        USER_RATINGS = 'user-ratings'
        USER_TAGS = 'user-tags'
        ARTIST_CREDITS = 'artist-credits'
        ISRCS = 'isrcs'
        AREA_RELS = 'area-rels'
        ARTIST_RELS = 'artist-rels'
        EVENT_RELS = 'event-rels'
        INSTRUMENT_RELS = 'instrument-rels'
        LABEL_RELS = 'label-rels'
        PLACE_RELS = 'place-rels'
        RECORDING_RELS = 'recording-rels'
        RELEASE_RELS = 'release-rels'
        RELEASE_GROUP_RELS = 'release-group-rels'
        SERIES_RELS = 'series-rels'
        URL_RELS = 'url-rels'
        WORK_RELS = 'work-rels'
        DISCIDS = 'discids' # requires `releases`
        MEDIA = 'media' # requires `releases`

    class Iswc(str, enum.Enum):
        ARTISTS = 'artists'
        ALIASES = 'aliases'
        RATINGS = 'ratings'
        TAGS = 'tags'
        USER_RATINGS = 'user-ratings'
        USER_TAGS = 'user-tags'
        ARTIST_CREDITS = 'artist-credits'
        AREA_RELS = 'area-rels'
        ARTIST_RELS = 'artist-rels'
        EVENT_RELS = 'event-rels'
        INSTRUMENT_RELS = 'instrument-rels'
        LABEL_RELS = 'label-rels'
        PLACE_RELS = 'place-rels'
        RECORDING_RELS = 'recording-rels'
        RELEASE_RELS = 'release-rels'
        RELEASE_GROUP_RELS = 'release-group-rels'
        SERIES_RELS = 'series-rels'
        URL_RELS = 'url-rels'
        WORK_RELS = 'work-rels'


def genreAll(limit: int = None, offset: int = 0, fmt: str = None) -> awkward.Record:
    return request.get(endpoint='/genre/all', limit=limit, offset=offset)

def lookup(entity: str, mbid: uuid.UUID, inc: list[str] = None, collection_type: CollectionType = '', type: list[api.ReleaseType] = None, status: list[api.ReleaseStatus] = None) -> awkward.Record:
    endpoint = f'/{entity}/{mbid}' if (not collection_type) else f'/{entity}/{mbid}/{collection_type}'
    inc = str.join('+', inc) if inc else None
    type = str.join('|', type) if type else None
    status = str.join('|', status) if status else None
    return request.get(endpoint=endpoint, inc=inc, type=type, status=status)

def area(mbid: uuid.UUID, inc: list[Inc.Area] = None) -> awkward.Record:
    return lookup(entity='area', mbid=mbid, inc=inc)

def artist(mbid: uuid.UUID, inc: list[Inc.Artist] = None, type: list[api.ReleaseType] = None, status: list[api.ReleaseStatus] = None) -> awkward.Record:
    return lookup(entity='artist', mbid=mbid, inc=inc, type=type, status=status)

def collection(mbid: uuid.UUID, collection_type: CollectionType = '', inc: list[Inc.Collection] = None) -> awkward.Record:
    return lookup(entity='collection', collection_type=collection_type, mbid=mbid, inc=inc)

def event(mbid: uuid.UUID, inc: list[Inc.Event] = None) -> awkward.Record:
    return lookup(entity='event', mbid=mbid, inc=inc)

def genre(mbid: uuid.UUID) -> awkward.Record:
    return lookup(entity='genre', mbid=mbid)

def instrument(mbid: uuid.UUID, inc: list[Inc.Instrument] = None) -> awkward.Record:
    return lookup(entity='instrument', mbid=mbid, inc=inc)

def label(mbid: uuid.UUID, inc: list[Inc.Label] = None, type: list[api.ReleaseType] = None, status: list[api.ReleaseStatus] = None) -> awkward.Record:
    return lookup(entity='label', mbid=mbid, inc=inc, type=type, status=status)

def place(mbid: uuid.UUID, inc: list[Inc.Place] = None) -> awkward.Record:
    return lookup(entity='place', mbid=mbid, inc=inc)

def recording(mbid: uuid.UUID, inc: list[Inc.Recording] = None, type: list[api.ReleaseType] = None, status: list[api.ReleaseStatus] = None) -> awkward.Record:
    return lookup(entity='recording', mbid=mbid, inc=inc, type=type, status=status)

def release(mbid: uuid.UUID, inc: list[Inc.Release] = None, type: list[api.ReleaseType] = None) -> awkward.Record:
    return lookup(entity='release', mbid=mbid, inc=inc, type=type)

def release_group(mbid: uuid.UUID, inc: list[Inc.Release_group] = None, type: list[api.ReleaseType] = None, status: list[api.ReleaseStatus] = None) -> awkward.Record:
    return lookup(entity='release-group', mbid=mbid, inc=inc, type=type, status=status)

def series(mbid: uuid.UUID, inc: list[Inc.Series] = None) -> awkward.Record:
    return lookup(entity='series', mbid=mbid, inc=inc)

def url(mbid: uuid.UUID = None, inc: list[Inc.Url] = None) -> awkward.Record:
    return lookup(entity='url', mbid=mbid, inc=inc)

def work(mbid: uuid.UUID, inc: list[Inc.Work] = None) -> awkward.Record:
    return lookup(entity='work', mbid=mbid, inc=inc)

# [Non-MBID Lookups](https://musicbrainz.org/doc/MusicBrainz_API#Non-MBID_Lookups)

def discid(discid: str, inc: list[Inc.Discid] = None, toc: list[int] = None, cdstubs: bool = True, media_format: str = 'CD') -> awkward.Record:
    inc = str.join('+', inc) if inc else None
    toc = str.join('+', toc) if toc else None
    cdstubs = 'no' if cdstubs is False else None
    return request.get(endpoint=f'/discid/{discid}', inc=inc, toc=toc, cdstubs=cdstubs, **{'media-format': media_format})

def isrc(isrc: str, inc: list[Inc.Isrc] = None) -> awkward.Record:
    inc = str.join('+', inc) if inc else None
    return request.get(endpoint=f'/isrc/{isrc}', inc=inc)

def iswc(iswc: str, inc: list[Inc.Iswc] = None) -> awkward.Record:
    inc = str.join('+', inc) if inc else None
    return request.get(endpoint=f'/iswc/{iswc}', inc=inc)
