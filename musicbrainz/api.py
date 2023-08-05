#!/usr/bin/env python3

import enum

'''[MusicBrainz API](https://musicbrainz.org/doc/MusicBrainz_API/)'''

# [https://musicbrainz.org/doc/XML_Web_Service/Rate_Limiting]
CONTACT = 'a@delannoy.cc'
VERSION = 0.2
CLIENT = f'delannoy-{VERSION}' # https://musicbrainz.org/doc/MusicBrainz_API#Authentication
USER_AGENT = f'delannoy/{VERSION} ({CONTACT})' # https://musicbrainz.org/doc/MusicBrainz_API/Rate_Limiting#Provide_meaningful_User-Agent_strings
SLEEP = 1.001 # https://musicbrainz.org/doc/MusicBrainz_API/Rate_Limiting#Source_IP_address


class CoreEntities(enum.Enum):
    AREA = 'area'
    ARTIST = 'artist'
    EVENT = 'event'
    GENRE = 'genre'
    INSTRUMENT = 'instrument'
    LABEL = 'label'
    PLACE = 'place'
    RECORDING = 'recording'
    RELEASE = 'release'
    RELEASE_GROUP = 'release-group'
    SERIES = 'series'
    URL = 'url'
    WORK = 'work'


class NonCoreEntities(enum.Enum):
    COLLECTION = 'collection'
    RATING = 'rating'
    TAG = 'tag'


class LookupIdentifiers(enum.Enum):
    DISCID = 'discid'
    ISRC = 'isrc'
    ISWC = 'iswc'


class ReleaseTypesPrimary(enum.Enum):
    # https://musicbrainz.org/doc/Release_Group/Type
    ALBUM = 'album'
    BROADCAST = 'broadcast'
    EP = 'ep'
    OTHER = 'other'
    SINGLE = 'single'


class ReleaseTypesSecondary(enum.Enum):
    # https://musicbrainz.org/doc/Release_Group/Type
    AUDIO_DRAMA = 'audio drama'
    AUDIOBOOK = 'audiobook'
    COMPILATION = 'compilation'
    DEMO = 'demo'
    DJ_MIX = 'dj-mix'
    INTERVIEW = 'interview'
    LIVE = 'live'
    MIXTAPE_STREET = 'mixtape/street'
    REMIX = 'remix'
    SOUNDTRACK = 'soundtrack'
    SPOKENWORD = 'spokenword'


class ReleaseStatuses(enum.Enum):
    # https://musicbrainz.org/doc/Release#Status
    BOOTLEG = 'bootleg'
    CANCELLED = 'cancelled'
    OFFICIAL = 'official'
    PROMOTION = 'promotion'
    PSEUDO_RELEASE = 'pseudo-release'


# https://musicbrainz.org/doc/Release_Group/Type
RELEASE_TYPES_PRIMARY = ['album', 'broadcast', 'ep', 'other', 'single']
RELEASE_TYPES_SECONDARY = ['audio drama', 'audiobook', 'compilation', 'demo', 'dj-mix', 'interview', 'live', 'mixtape/street', 'remix', 'soundtrack', 'spokenword']
RELEASE_TYPES = RELEASE_TYPES_PRIMARY + RELEASE_TYPES_SECONDARY

# https://musicbrainz.org/doc/Release#Status
RELEASE_STATUSES = ['bootleg', 'cancelled', 'official', 'promotion', 'pseudo-release', 'withdrawn']
