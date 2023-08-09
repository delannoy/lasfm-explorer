#!/usr/bin/env python3

from __future__ import annotations
import enum

'''[MusicBrainz API](https://musicbrainz.org/doc/MusicBrainz_API/)'''

# https://musicbrainz.org/doc/XML_Web_Service/Rate_Limiting
CONTACT = 'a@delannoy.cc'
VERSION = 0.2
CLIENT = f'delannoy-{VERSION}' # https://musicbrainz.org/doc/MusicBrainz_API#Authentication
USER_AGENT = f'delannoy/{VERSION} ({CONTACT})' # https://musicbrainz.org/doc/MusicBrainz_API/Rate_Limiting#Provide_meaningful_User-Agent_strings
SLEEP = 1.001 # https://musicbrainz.org/doc/MusicBrainz_API/Rate_Limiting#Source_IP_address


class CoreEntities(str, enum.Enum): # [String-based enum in Python](https://stackoverflow.com/a/58608362)
    '''https://musicbrainz.org/doc/MusicBrainz_API#Introduction'''
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


class NonCoreEntities(str, enum.Enum):
    '''https://musicbrainz.org/doc/MusicBrainz_API#Introduction'''
    COLLECTION = 'collection'
    RATING = 'rating'
    TAG = 'tag'


class LookupIdentifiers(str, enum.Enum):
    '''https://musicbrainz.org/doc/MusicBrainz_API#Introduction'''
    DISCID = 'discid'
    ISRC = 'isrc'
    ISWC = 'iswc'


class ReleaseType(str, enum.Enum):
    '''https://musicbrainz.org/doc/Release_Group/Type'''
    ALBUM = 'album'
    BROADCAST = 'broadcast'
    EP = 'ep'
    OTHER = 'other'
    SINGLE = 'single'
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


class ReleaseTypePrimary(str, enum.Enum):
    '''https://musicbrainz.org/doc/Release_Group/Type'''
    ALBUM = 'album'
    SINGLE = 'single'
    EP = 'ep'
    BROADCAST = 'broadcast'
    OTHER = 'other'


class ReleaseTypeSecondary(str, enum.Enum):
    '''https://musicbrainz.org/doc/Release_Group/Type'''
    COMPILATION = 'compilation'
    SOUNDTRACK = 'soundtrack'
    SPOKENWORD = 'spokenword'
    INTERVIEW = 'interview'
    AUDIOBOOK = 'audiobook'
    AUDIO_DRAMA = 'audio drama'
    LIVE = 'live'
    REMIX = 'remix'
    DJ_MIX = 'dj-mix'
    MIXTAPE_STREET = 'mixtape/street'
    DEMO = 'demo'
    FIELD_RECORDING = 'field recording'


class ReleaseStatus(str, enum.Enum):
    '''https://musicbrainz.org/doc/Release#Status'''
    OFFICIAL = 'official'
    PROMOTION = 'promotion'
    BOOTLEG = 'bootleg'
    PSEUDO_RELEASE = 'pseudo-release'
    WITHDRAWN = 'withdrawn'
    CANCELLED = 'cancelled'
