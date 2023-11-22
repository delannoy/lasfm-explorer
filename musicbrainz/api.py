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


class Release:

    class Format(str, enum.Enum):
        '''https://musicbrainz.org/doc/Release/Format'''
        CD = 'cd'
        COPY_CONTROL_CD = 'copy control cd'
        DATA_CD = 'data cd'
        DTS_CD = 'dts cd'
        ENHANCED_CD = 'enhanced cd'
        HDCD = 'hdcd'
        CD_R = 'cd-r'
        CD_8CM = '8cm cd'
        BLU_SPEC_CD = 'blu-spec cd'
        SHM_CD = 'shm-cd'
        HQCD = 'hqcd'
        VINYL = 'vinyl'
        VINYL_7IN = '7" vinyl'
        VINYL_10IN = '10" vinyl'
        VINYL_12IN = '12" vinyl'
        FLEXI_DISC = 'flexi-disc'
        FLEXI_DISC_7IN = '7" flexi-disc'
        DIGITAL_MEDIA = 'digital media'
        CASSETTE = 'cassette'
        MICROCASSETTE = 'microcassette'
        DVD = 'dvd'
        DVD_AUDIO = 'dvd-audio'
        DVD_VIDEO = 'dvd-video'
        SACD = 'sacd'
        HYBRID_SACD = 'hybrid sacd'
        HYBRID_SACD_CD_LAYER = 'hybrid sacd (cd layer)'
        HYBRID_SACD_SACD_LAYER = 'hybrid sacd (sacd layer)'
        SHM_SACD = 'shm-sacd'
        DUALDISC = 'dualdisc'
        DUALDISC_CD_SIDE = 'dualdisc (cd side)'
        DUALDISC_DVD_VIDEO_SIDE = 'dualdisc (dvd-video side)'
        DUALDISC_DVD_AUDIO_SIDE = 'dualdisc (dvd-audio side)'
        MINIDISC = 'minidisc'
        BLU_RAY = 'blu-ray'
        BLU_RAY_R = 'blu-ray-r'
        HD_DVD = 'hd-dvd'
        VCD = 'vcd'
        SVCD = 'svcd'
        CDV = 'cdv'
        UMD = 'umd'
        SHELLAC = 'shellac'
        SHELLAC_7IN = '7" shellac'
        SHELLAC_10IN = '10" shellac'
        SHELLAC_12IN = '12" shellac'
        SD_CARD = 'sd card'
        SLOTMUSIC = 'slotmusic'
        OTHER = 'other'
        BETAMAX = 'betamax'
        CARTRIDGE = 'cartridge'
        HIPAC = 'hipac'
        PLAYTAPE = 'playtape'
        CED = 'ced'
        DAT = 'dat'
        DCC = 'dcc'
        DVDPLUS = 'dvdplus'
        DVDPLUS_CD_SIDE = 'dvdplus (cd side)'
        DVDPLUS_DVD_VIDEO_SIDE = 'dvdplus (dvd-video side)'
        DVDPLUS_DVD_AUDIO_SIDE = 'dvdplus (dvd-audio side)'
        EDISON_DIAMOND_DISC = 'edison diamond disc'
        FLOPPY_DISK = 'floppy disk'
        FLOPPY_DISK_3_5IN = '3.5" floppy disk'
        FLOPPY_DISK_5_25IN = '5.25" floppy disk'
        ZIP_DISK = 'zip disk'
        LASERDISC = 'laserdisc'
        LASERDISC_8IN = '8" laserdisc'
        LASERDISC_12IN = '12" laserdisc'
        MUSIC_CARD = 'music card'
        PATHE_DISC = 'pathé disc'
        PIANO_ROLL = 'piano roll'
        PLAYBUTTON = 'playbutton'
        REEL_TO_REEL = 'reel-to-reel'
        TEFIFON = 'tefifon'
        USB_FLASH_DRIVE = 'usb flash drive'
        VHD = 'vhd'
        VHS = 'vhs'
        VINYLDISC = 'vinyldisc'
        WAX_CYLINDER = 'wax cylinder'
        WIRE_RECORDING = 'wire recording'
        MULTITRACKS_RECORDING_4_TRACKS_8_TRACKS = '4 tracks/8 tracks/multitracks recording'
        ELCASET = 'elcaset'
        GRAMOPHONE_RECORD = 'gramophone record'

    class Status(str, enum.Enum):
        '''https://musicbrainz.org/doc/Release#Status'''
        OFFICIAL = 'official'
        PROMOTION = 'promotion'
        BOOTLEG = 'bootleg'
        PSEUDO_RELEASE = 'pseudo-release'
        WITHDRAWN = 'withdrawn'
        CANCELLED = 'cancelled'

    class Type(str, enum.Enum):
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



class Type:

    class Area(str, enum.Enum):
        '''https://musicbrainz.org/doc/Area#Type'''
        COUNTRY = 'country'
        SUBDIVISION = 'subdivision'
        COUNTY = 'county'
        MUNICIPALITY = 'municipality'
        CITY = 'city'
        DISTRICT = 'district'
        ISLAND = 'island'

    class Artist(str, enum.Enum):
        '''https://musicbrainz.org/doc/Artist#Type'''
        PERSON = 'person'
        GROUP = 'group'
        ORCHESTRA = 'orchestra'
        CHOIR = 'choir'
        CHARACTER = 'character'
        OTHER = 'other'

    class Event(str, enum.Enum):
        '''https://musicbrainz.org/doc/Event#Type'''
        CONCERT = 'concert'
        FESTIVAL = 'festival'
        STAGE_PERFORMANCE = 'stage performance'
        AWARD_CEREMONY = 'award ceremony'
        LAUNCH_EVENT = 'launch event'
        CONVENTION_EXPO = 'convention/expo'
        MASTERCLASS_CLINIC = 'masterclass/clinic'

    class Instrument(str, enum.Enum):
        '''https://musicbrainz.org/doc/Instrument#Type'''
        WIND_INSTRUMENT = 'wind instrument'
        STRING_INSTRUMENT = 'string instrument'
        PERCUSSION_INSTRUMENT = 'percussion instrument'
        ELECTRONIC_INSTRUMENT = 'electronic instrument'
        FAMILY = 'family'
        ENSEMBLE = 'ensemble'
        OTHER_INSTRUMENT = 'other instrument'

    class Label(str, enum.Enum):
        '''https://musicbrainz.org/doc/Label/Type'''
        IMPRINT = 'imprint'
        ORIGINAL_PRODUCTION = 'original production'
        BOOTLEG_PRODUCTION = 'bootleg production'
        REISSUE_PRODUCTION = 'reissue production'
        DISTRIBUTOR = 'distributor'
        HOLDING = 'holding'
        RIGHTS_SOCIETY = 'rights society'

    class Place(str, enum.Enum):
        '''https://musicbrainz.org/doc/Place#Type'''
        STUDIO = 'studio'
        VENUE = 'venue'
        STADIUM = 'stadium'
        INDOOR_ARENA = 'indoor arena'
        RELIGIOUS_BUILDING = 'religious building'
        EDUCATIONAL_INSTITUTION = 'educational institution'
        PRESSING_PLANT = 'pressing plant'
        OTHER = 'other'

    class Release:

        class Primary(str, enum.Enum):
            '''https://musicbrainz.org/doc/Release_Group/Type#Primary_types'''
            ALBUM = 'album'
            SINGLE = 'single'
            EP = 'ep'
            BROADCAST = 'broadcast'
            OTHER = 'other'

        class Secondary(str, enum.Enum):
            '''https://musicbrainz.org/doc/Release_Group/Type#Secondary_types'''
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

    class Series(str, enum.Enum):
        '''https://musicbrainz.org/doc/Series#Type'''
        RELEASE_GROUP_SERIES = 'release group series'
        RELEASE_SERIES = 'release series'
        RECORDING_SERIES = 'recording series'
        WORK_SERIES = 'work series'
        CATALOGUE = 'catalogue'
        ARTIST_SERIES = 'artist series'
        ARTIST_AWARD = 'artist award'
        EVENT_SERIES = 'event series'
        TOUR = 'tour'
        FESTIVAL = 'festival'
        RUN = 'run'
        RESIDENCY = 'residency'
