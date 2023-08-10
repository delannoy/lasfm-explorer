#!/usr/bin/env python3

from __future__ import annotations
import enum
import uuid

import awkward

import api
import request

'''[Browse requests are a direct lookup of all the entities directly linked to another entity ("directly linked" meaning it does not include entities linked by a relationship)](https://musicbrainz.org/doc/MusicBrainz_API#Browse)'''


class LinkedEntity:
    '''https://musicbrainz.org/doc/MusicBrainz_API#Linked_entities'''

    @classmethod
    def get(cls, attr: str):
        return getattr(cls, attr)

    @classmethod
    def enums(cls) -> list[str]:
        return [attr for attr, typ in vars(cls).items() if isinstance(typ, enum.EnumMeta)]

    class Area(str, enum.Enum):
        COLLECTION = 'collection'

    class Artist(str, enum.Enum):
        AREA = 'area'
        COLLECTION = 'collection'
        RECORDING = 'recording'
        RELEASE = 'release'
        RELEASE_GROUP = 'release-group'
        WORK = 'work'

    class Collection(str, enum.Enum):
        AREA = 'area'
        ARTIST = 'artist'
        EDITOR = 'editor'
        EVENT = 'event'
        LABEL = 'label'
        PLACE = 'place'
        RECORDING = 'recording'
        RELEASE = 'release'
        RELEASE_GROUP = 'release-group'
        WORK = 'work'

    class Event(str, enum.Enum):
        AREA = 'area'
        ARTIST = 'artist'
        COLLECTION = 'collection'
        PLACE = 'place'

    class Instrument(str, enum.Enum):
        COLLECTION = 'collection'

    class Label(str, enum.Enum):
        AREA = 'area'
        COLLECTION = 'collection'
        RELEASE = 'release'

    class Place(str, enum.Enum):
        AREA = 'area'
        COLLECTION = 'collection'

    class Recording(str, enum.Enum):
        ARTIST = 'artist'
        COLLECTION = 'collection'
        RELEASE = 'release'
        WORK = 'work'

    class Release(str, enum.Enum):
        AREA = 'area'
        ARTIST = 'artist'
        COLLECTION = 'collection'
        LABEL = 'label'
        TRACK = 'track'
        TRACK_ARTIST = 'track_artist'
        RECORDING = 'recording'
        RELEASE_GROUP = 'release-group'

    class Release_group(str, enum.Enum):
        ARTIST = 'artist'
        COLLECTION = 'collection'
        RELEASE = 'release'

    class Series(str, enum.Enum):
        COLLECTION = 'collection'

    class Work(str, enum.Enum):
        ARTIST = 'artist'
        COLLECTION = 'collection'

    class Url(str, enum.Enum):
        RESOURCE = 'resource'


class Inc:

    @classmethod
    def get(cls, attr: str):
        return getattr(cls, attr)

    @classmethod
    def enums(cls) -> list[str]:
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

    class Collection(str, enum.Enum):
        USER_COLLECTIONS = 'user-collections'

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

    class Release(str, enum.Enum):
        LABELS = 'labels'
        RECORDINGS = 'recordings'
        RELEASE_GROUPS = 'release-groups'
        ALIASES = 'aliases'
        ANNOTATION = 'annotation'
        GENRES = 'genres'
        RATINGS = 'ratings'
        TAGS = 'tags'
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


def browse(entity: str, linked_entity: dict[str, uuid.UUID] = None, inc: list[str] = None, type: list[api.ReleaseType] = None, status: list[api.ReleaseStatus] = None, offset: int = 0, limit: int = 25, **kwargs) -> awkward.Record:
    linked_entity = linked_entity if linked_entity else kwargs
    inc = str.join('+', inc) if inc else None
    type = str.join('|', type) if type else None
    status = str.join('|', status) if status else None
    return request.get(endpoint=f'/{entity}', inc=inc, type=type, status=status, offset=offset, limit=limit, **linked_entity)

def area(linked_entity: dict[LinkedEntity.Area, uuid.UUID] = None, inc: list[Inc.Area] = None, offset: int = 0, limit: int = 25, **kwargs) -> awkward.Record:
    return browse(entity='area', linked_entity=linked_entity, inc=inc, offset=offset, limit=limit, **kwargs)

def artist(linked_entity: dict[LinkedEntity.Artist, uuid.UUID] = None, inc: list[Inc.Artist] = None, offset: int = 0, limit: int = 25, **kwargs) -> awkward.Record:
    return browse(entity='artist', linked_entity=linked_entity, inc=inc, offset=offset, limit=limit, **kwargs)

def collection(linked_entity: dict[LinkedEntity.Collection, uuid.UUID|str] = None, inc: list[Inc.Collection] = None, offset: int = 0, limit: int = 25, **kwargs) -> awkward.Record:
    return browse(entity='collection', linked_entity=linked_entity, inc=inc, offset=offset, limit=limit, **kwargs)

def event(linked_entity: dict[LinkedEntity.Event, uuid.UUID] = None, inc: list[Inc.Event] = None, offset: int = 0, limit: int = 25, **kwargs) -> awkward.Record:
    return browse(entity='event', linked_entity=linked_entity, inc=inc, offset=offset, limit=limit, **kwargs)

def instrument(linked_entity: dict[LinkedEntity.Instrument, uuid.UUID] = None, inc: list[Inc.Instrument] = None, offset: int = 0, limit: int = 25, **kwargs) -> awkward.Record:
    return browse(entity='instrument', linked_entity=linked_entity, inc=inc, offset=offset, limit=limit, **kwargs)

def label(linked_entity: dict[LinkedEntity.Label, uuid.UUID] = None, inc: list[Inc.Label] = None, offset: int = 0, limit: int = 25, **kwargs) -> awkward.Record:
    return browse(entity='label', linked_entity=linked_entity, inc=inc, offset=offset, limit=limit, **kwargs)

def place(linked_entity: dict[LinkedEntity.Place, uuid.UUID] = None, inc: list[Inc.Place] = None, offset: int = 0, limit: int = 25, **kwargs) -> awkward.Record:
    return browse(entity='place', linked_entity=linked_entity, inc=inc, offset=offset, limit=limit, **kwargs)

def recording(linked_entity: dict[LinkedEntity.Recording, uuid.UUID] = None, inc: list[Inc.Recording] = None, offset: int = 0, limit: int = 25, **kwargs) -> awkward.Record:
    return browse(entity='recording', linked_entity=linked_entity, inc=inc, offset=offset, limit=limit, **kwargs)

def release(linked_entity: dict[LinkedEntity.Release, uuid.UUID] = None, inc: list[Inc.Release] = None, type: list[api.ReleaseType] = None, status: list[api.ReleaseStatus] = None, offset: int = 0, limit: int = 25, **kwargs) -> awkward.Record:
    return browse(entity='release', linked_entity=linked_entity, inc=inc, type=type, status=status, offset=offset, limit=limit, **kwargs)

def release_group(linked_entity: dict[LinkedEntity.Release_group, uuid.UUID] = None, inc: list[Inc.Release_group] = None, type: list[api.ReleaseType] = None, offset: int = 0, limit: int = 25, **kwargs) -> awkward.Record:
    return browse(entity='release-group', linked_entity=linked_entity, inc=inc, type=type, offset=offset, limit=limit, **kwargs)

def series(linked_entity: dict[LinkedEntity.Series, uuid.UUID] = None, inc: list[Inc.Series] = None, offset: int = 0, limit: int = 25, **kwargs) -> awkward.Record:
    return browse(entity='series', linked_entity=linked_entity, inc=inc, offset=offset, limit=limit, **kwargs)

def work(linked_entity: dict[LinkedEntity.Work, uuid.UUID] = None, inc: list[Inc.Work] = None, offset: int = 0, limit: int = 25, **kwargs) -> awkward.Record:
    return browse(entity='work', linked_entity=linked_entity, inc=inc, offset=offset, limit=limit, **kwargs)

def url(linked_entity: dict[LinkedEntity.Url, str] = None, inc: list[Inc.Url] = None, offset: int = 0, limit: int = 25, **kwargs) -> awkward.Record:
    return browse(entity='url', linked_entity=linked_entity, inc=inc, offset=offset, limit=limit, **kwargs)
