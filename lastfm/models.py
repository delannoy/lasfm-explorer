#!/usr/bin/env python3

from __future__ import annotations
import datetime
import enum
import typing
import uuid

import dateparser
import pydantic

def validateDateTime(field: str) -> classmethod:
    '''Reusable validator for datetime strings based on `dateparser.parse`.'''
    def parseDateTime(dt: str) -> datetime.datetime:
        return dateparser.parse(str(dt), settings=dict(TIMEZONE='utc', RETURN_AS_TIMEZONE_AWARE=True))
    return pydantic.field_validator(field, mode='before')(parseDateTime)


class BaseModel(pydantic.BaseModel, extra='forbid'):
    '''Base class which forbids extra fields and coerces empty or literal "none" strings into `None`.'''

    @pydantic.field_validator('*', mode='before')
    @classmethod
    def nullString(cls, val: typing.Any) -> typing.Any:
        '''Return `None` if `val` is an empty string or a literal "none", "n/a", "fixme" string'''
        return None if isinstance(val, str) and (not val.strip() or val.lower() in ('none', 'n/a', 'fixme')) else val


class ImageSize(str, enum.Enum):
    SMALL = 'small'
    MEDIUM = 'medium'
    LARGE = 'large'
    EXTRALARGE = 'extralarge'
    MEGA = 'mega'


class Entity(BaseModel):
    name: str
    mbid: typing.Optional[uuid.UUID] = None
    url: pydantic.HttpUrl


class Error(BaseModel):
    message: str
    error: int
    links: typing.Optional[typing.List] = None


class Image(BaseModel):
    size: typing.Optional[ImageSize] = None
    url: typing.Optional[pydantic.HttpUrl] = pydantic.Field(alias='#text', default=None)


class Query(BaseModel):
    query: typing.Optional[str] = pydantic.Field(alias='for', default=None) # '@attr' seems to be always empty (https://lastfm-docs.github.io/api-docs/track/search/#examples)


class OpensearchQuery(BaseModel):
    text: typing.Optional[str] = pydantic.Field(alias='#text', default=None)
    role: str
    startPage: int
    searchTerms: typing.Optional[str] = None


class Rank(BaseModel):
    rank: int


class Streamable(BaseModel):
    fulltrack: bool
    streamable: bool = pydantic.Field(alias='#text')


class Tag(BaseModel):
    name: str
    url: pydantic.HttpUrl


class Tags(BaseModel):
    tag: typing.List[Tag]


class TopTag(BaseModel):
    name: str
    url: pydantic.HttpUrl
    count: int


class Wiki(BaseModel):
    summary: typing.Optional[str] = None
    published: typing.Optional[datetime.datetime] = None
    content: typing.Optional[str] = None
    _ = validateDateTime('published')


class album:

    class Name(BaseModel):
        artist: str
        album: str

    '''album.getInfo'''

    class Track(BaseModel):
        name: str
        mbid: typing.Optional[uuid.UUID] = None
        url: pydantic.HttpUrl
        artist: Entity
        duration: typing.Optional[int] = None
        streamable: Streamable
        attr: Rank = pydantic.Field(alias='@attr')

    class Tracks(BaseModel):
        track: typing.List[album.Track]

    class Album(BaseModel):
        name: str
        mbid: typing.Optional[uuid.UUID] = None
        url: pydantic.HttpUrl
        image: typing.List[Image]
        artist: str
        tracks: typing.Optional[album.Tracks] = None
        tags: typing.Optional[Tags] = None
        listeners: int
        playcount: int
        userplaycount: typing.Optional[int] = None
        wiki: typing.Optional[Wiki] = None

    '''album.getTags'''

    class Tags(BaseModel):
        tag: typing.Optional[typing.List[Tag]] = None
        text: typing.Optional[str] = pydantic.Field(alias='#text', default=None)
        attr: album.Name = pydantic.Field(alias='@attr')

    '''album.getTopTags'''

    class Toptags(BaseModel):
        tag: typing.List[TopTag]
        attr: album.Name = pydantic.Field(alias='@attr')

    '''album.search'''

    class Match(BaseModel):
        name: typing.Optional[str] = None
        mbid: typing.Optional[uuid.UUID] = None
        url: pydantic.HttpUrl
        image: typing.List[Image]
        artist: str
        streamable: bool

    class Matches(BaseModel):
        album: typing.List[album.Match]

    class Results(BaseModel):
        albummatches: album.Matches
        opensearch_Query: OpensearchQuery = pydantic.Field(alias='opensearch:Query')
        opensearch_totalResults: int = pydantic.Field(alias='opensearch:totalResults')
        opensearch_startIndex: int = pydantic.Field(alias='opensearch:startIndex')
        opensearch_itemsPerPage: int = pydantic.Field(alias='opensearch:itemsPerPage')
        attr: Query = pydantic.Field(alias='@attr')


class artist:

    class Name(BaseModel):
        artist: str

    class Pagination(BaseModel):
        artist: str
        page: int
        perPage: int
        totalPages: int
        total: int

    '''artist.getCorrection'''

    class Index(BaseModel):
        index: int

    class Correction(BaseModel):
        artist: Entity
        attr: artist.Index = pydantic.Field(alias='@attr')

    class Corrections(BaseModel):
        correction: artist.Correction

    '''artist.getInfo'''

    class Link(BaseModel):
        text: typing.Optional[str] = pydantic.Field(alias='#text', default=None)
        rel: str
        href: pydantic.HttpUrl

    class Links(BaseModel):
        link: artist.Link

    class Bio(BaseModel):
        links: artist.Links
        published: datetime.datetime
        summary: str
        content: typing.Optional[str] = None
        _ = validateDateTime('published')

    class Stats(BaseModel):
        listeners: int
        playcount: int
        userplaycount: typing.Optional[int] = None

    class SimilarArtist(BaseModel):
        name: typing.Optional[str] = None # ugh! https://www.last.fm/music/None
        url: pydantic.HttpUrl
        image: typing.List[Image]

    class SimilarArtists(BaseModel):
        artist: typing.List[artist.SimilarArtist]

    class Artist(BaseModel):
        name: str
        mbid: typing.Optional[uuid.UUID] = None
        url: pydantic.HttpUrl
        image: typing.List[Image]
        bio: artist.Bio
        stats: artist.Stats
        similar: artist.SimilarArtists
        tags: Tags
        streamable: bool
        ontour: bool

    '''artist.getSimilar'''

    class Similar(BaseModel):
        name: str
        mbid: typing.Optional[uuid.UUID] = None
        url: pydantic.HttpUrl
        image: typing.List[Image]
        match: float
        streamable: bool

    class Similarartists(BaseModel):
        artist: typing.List[artist.Similar]
        attr: artist.Name = pydantic.Field(alias='@attr')

    '''artist.getTags'''

    class Tags(BaseModel):
        tag: typing.Optional[typing.List[Tag]] = None
        text: typing.Optional[str] = pydantic.Field(alias='#text', default=None)
        attr: artist.Name = pydantic.Field(alias='@attr')

    '''artist.getTopAlbums'''

    class Album(BaseModel):
        name: typing.Optional[str] = None
        mbid: typing.Optional[uuid.UUID] = None
        url: pydantic.HttpUrl
        image: typing.List[Image]
        artist: Entity
        playcount: int

    class Topalbums(BaseModel):
        album: typing.List[artist.Album]
        attr: artist.Pagination = pydantic.Field(alias='@attr')

    '''artist.getTopTags'''

    class Toptags(BaseModel):
        tag: typing.List[TopTag]
        attr: artist.Name = pydantic.Field(alias='@attr')

    '''artist.getTopTracks'''

    class Track(BaseModel):
        name: str
        mbid: typing.Optional[uuid.UUID] = None
        url: pydantic.HttpUrl
        image: typing.List[Image]
        artist: Entity
        playcount: int
        listeners: int
        streamable: bool
        attr: Rank = pydantic.Field(alias='@attr')

    class Toptracks(BaseModel):
        track: typing.List[artist.Track]
        attr: artist.Pagination = pydantic.Field(alias='@attr')

    '''artist.search'''

    class Match(BaseModel):
        name: str
        mbid: typing.Optional[uuid.UUID] = None
        url: pydantic.HttpUrl
        image: typing.List[Image]
        listeners: int
        streamable: bool

    class Matches(BaseModel):
        artist: typing.List[artist.Match]

    class Results(BaseModel):
        artistmatches: artist.Matches
        opensearch_Query: OpensearchQuery = pydantic.Field(alias='opensearch:Query')
        opensearch_totalResults: int = pydantic.Field(alias='opensearch:totalResults')
        opensearch_startIndex: int = pydantic.Field(alias='opensearch:startIndex')
        opensearch_itemsPerPage: int = pydantic.Field(alias='opensearch:itemsPerPage')
        attr: Query = pydantic.Field(alias='@attr')


class auth:

    class Token(BaseModel):
        token: str

    class Session(BaseModel):
        name: str
        key: str
        subscriber: bool


class chart:

    class Pagination(BaseModel):
        page: int
        perPage: int
        totalPages: int
        total: int

    '''chart.getTopArtists'''

    class Artist(BaseModel):
        name: str
        mbid: typing.Optional[uuid.UUID] = None
        url: pydantic.HttpUrl
        image: typing.List[Image]
        playcount: int
        listeners: int
        streamable: bool

    class Artists(BaseModel):
        artist: typing.List[chart.Artist]
        attr: chart.Pagination = pydantic.Field(alias='@attr')

    '''chart.getTopTags'''

    class Tag(BaseModel):
        name: str
        url: pydantic.HttpUrl
        taggings: int
        reach: int
        streamable: bool
        wiki: Wiki

    class Tags(BaseModel):
        tag: typing.List[chart.Tag]
        attr: chart.Pagination = pydantic.Field(alias='@attr')

    '''chart.getTopTracks'''

    class Track(BaseModel):
        name: str
        mbid: typing.Optional[uuid.UUID] = None
        url: pydantic.HttpUrl
        image: typing.List[Image]
        artist: Entity
        duration: int
        playcount: int
        listeners: int
        streamable: Streamable

    class Tracks(BaseModel):
        track: typing.List[chart.Track]
        attr: chart.Pagination = pydantic.Field(alias='@attr')


class geo:

    class Pagination(BaseModel):
        country: str
        page: int
        perPage: int
        totalPages: int
        total: int

    '''geo.getTopArtists'''

    class Artist(BaseModel):
        name: str
        mbid: typing.Optional[uuid.UUID] = None
        url: pydantic.HttpUrl
        image: typing.List[Image]
        listeners: int
        streamable: bool

    class Topartists(BaseModel):
        artist: typing.List[geo.Artist]
        attr: geo.Pagination = pydantic.Field(alias='@attr')

    '''geo.getTopTracks'''

    class Track(BaseModel):
        name: str
        mbid: typing.Optional[uuid.UUID] = None
        url: pydantic.HttpUrl
        image: typing.List[Image]
        duration: int
        listeners: int
        streamable: Streamable
        artist: Entity
        attr: Rank = pydantic.Field(alias='@attr')

    class Tracks(BaseModel):
        track: typing.List[geo.Track]
        attr: geo.Pagination = pydantic.Field(alias='@attr')


class library:

    '''library.getArtists'''

    class Artist(BaseModel):
        name: str
        mbid: typing.Optional[uuid.UUID] = None
        url: pydantic.HttpUrl
        image: typing.List[Image]
        playcount: int
        tagcount: int
        streamable: bool

    class Artists(BaseModel):
        artist: typing.List[library.Artist]
        attr: user.Pagination = pydantic.Field(alias='@attr')


class tag:

    class Name(BaseModel):
        tag: typing.Optional[str] = None

    class Pagination(BaseModel):
        tag: str
        page: int
        perPage: int
        totalPages: int
        total: int

    '''tag.getInfo'''

    class Tag(BaseModel):
        name: str
        total: int
        reach: int
        wiki: Wiki

    '''tag.getSimilar'''

    class SimilarTag(BaseModel):
        name: str
        url: pydantic.HttpUrl
        streamable: bool

    class Similartags(BaseModel):
        tag: typing.List[tag.SimilarTag]
        attr: tag.Name = pydantic.Field(alias='@attr')

    '''tag.getTopAlbums'''

    class Album(BaseModel):
        name: str
        mbid: typing.Optional[uuid.UUID] = None
        url: pydantic.HttpUrl
        image: typing.List[Image]
        artist: Entity
        attr: Rank = pydantic.Field(alias='@attr')

    class Albums(BaseModel):
        album: typing.List[tag.Album]
        attr: tag.Pagination = pydantic.Field(alias='@attr')

    '''tag.getTopArtists'''

    class Artist(BaseModel):
        name: str
        mbid: typing.Optional[uuid.UUID] = None
        url: pydantic.HttpUrl
        image: typing.List[Image]
        streamable: bool
        attr: Rank = pydantic.Field(alias='@attr')

    class Topartists(BaseModel):
        artist: typing.List[tag.Artist]
        attr: tag.Pagination = pydantic.Field(alias='@attr')

    '''tag.getTopTags'''

    class TopAttr(BaseModel):
        offset: int
        num_res: int
        total: int

    class TopTag(BaseModel):
        name: str
        count: int
        reach: int

    class Toptags(BaseModel):
        tag: typing.List[tag.TopTag]
        attr: tag.TopAttr = pydantic.Field(alias='@attr')

    '''tag.getTopTracks'''

    class Track(BaseModel):
        name: str
        mbid: typing.Optional[uuid.UUID] = None
        url: pydantic.HttpUrl
        image: typing.List[Image]
        duration: int
        artist: Entity
        streamable: Streamable
        attr: Rank = pydantic.Field(alias='@attr')

    class Tracks(BaseModel):
        track: typing.List[tag.Track]
        attr: tag.Pagination = pydantic.Field(alias='@attr')

    '''tag.getWeeklyChartList'''

    class Weekly(BaseModel):
        text: typing.Optional[str] = pydantic.Field(alias='#text', default=None)
        fr: int = pydantic.Field(alias='from')
        to: int

    class Weeklychartlist(BaseModel):
        chart: typing.List[tag.Weekly]
        attr: tag.Name = pydantic.Field(alias='@attr')


class track:


    class ScrobbleErrors(enum.IntEnum):
        '''https://www.last.fm/api/show/track.scrobble'''

        def __new__(cls, value: int, doc: str = ''):
            '''override Enum.__new__ to take a doc argument'''
            # [How can I attach documentation to members of a python enum?](https://stackoverflow.com/a/50473952)
            self = int.__new__(cls, value)
            self._value_ = value
            self.__doc__ = doc
            return self

        OK = (0, '')
        ARTIST_IGNORED = (1, "Artist was ignored")
        TRACK_IGNORED = (2, "Track was ignored")
        OLD_TIMESTAMP = (3, "Timestamp was too old")
        NEW_TIMESTAMP = (4, "Timestamp was too new")
        LIMIT_EXCEEDED = (5, "Daily scrobble limit exceeded")


    class Attr(BaseModel):
        artist: str
        track: str

    '''track.getCorrection'''

    class CorrectionAttr(BaseModel):
        index: int
        artistcorrected: bool
        trackcorrected: bool

    class TrackCorrection(BaseModel):
        name: typing.Optional[str] = None
        mbid: typing.Optional[uuid.UUID] = None
        url: pydantic.HttpUrl
        artist: Entity

    class Correction(BaseModel):
        track: track.TrackCorrection
        attr: track.CorrectionAttr = pydantic.Field(alias='@attr')

    class Corrections(BaseModel):
        correction: track.Correction

    '''track.getInfo'''

    class Position(BaseModel):
        position: int

    class Album(BaseModel):
        title: str
        artist: str
        mbid: typing.Optional[uuid.UUID] = None
        url: pydantic.HttpUrl
        image: typing.List[Image]
        attr: track.Position = pydantic.Field(alias='@attr')

    class Track(BaseModel):
        name: str
        mbid: typing.Optional[uuid.UUID] = None
        url: pydantic.HttpUrl
        duration: int
        listeners: int
        playcount: int
        userplaycount: typing.Optional[int] = None
        userloved: typing.Optional[bool] = None
        artist: Entity
        album: typing.Optional[track.Album] = None
        toptags: Tags
        streamable: Streamable
        wiki: typing.Optional[Wiki] = None

    '''track.getSimilar'''

    class Artist(BaseModel):
        artist: str

    class SimilarTrack(BaseModel):
        name: str
        mbid: typing.Optional[uuid.UUID] = None
        url: pydantic.HttpUrl
        image: typing.List[Image]
        duration: typing.Optional[int] = None
        playcount: int
        artist: Entity
        match: float
        streamable: Streamable

    class Similartracks(BaseModel):
        track: typing.List[track.SimilarTrack]
        attr: track.Artist = pydantic.Field(alias='@attr')

    '''track.getTags'''

    class Tags(BaseModel):
        tag: typing.Optional[typing.List[Tag]] = None
        text: typing.Optional[str] = pydantic.Field(alias='#text', default=None)
        attr: track.Attr = pydantic.Field(alias='@attr')

    '''track.getTopTags'''

    class Toptags(BaseModel):
        tag: typing.List[TopTag]
        attr: track.Attr = pydantic.Field(alias='@attr')

    '''track.scrobble'''

    class ScrobbleAttr(BaseModel):
        ignored: int
        accepted: int

    class IgnoredMessage(BaseModel):
        code: track.ScrobbleErrors
        text: typing.Optional[str] = pydantic.Field(alias='#text', default=None)

    class Entity(BaseModel):
        name: typing.Optional[str] = pydantic.Field(alias='#text', default=None)
        corrected: bool

    class Scrobble(BaseModel):
        artist: track.Entity
        albumArtist: track.Entity
        album: track.Entity
        track: track.Entity
        ignoredMessage: track.IgnoredMessage
        timestamp: int

    class Scrobbles(BaseModel):
        scrobble: typing.List[track.Scrobble]
        attr: track.ScrobbleAttr = pydantic.Field(alias='@attr')

    '''track.search'''

    class Match(BaseModel):
        name: str
        mbid: typing.Optional[uuid.UUID] = None
        url: pydantic.HttpUrl
        image: typing.List[Image]
        artist: str
        listeners: int
        streamable: typing.Optional[bool] = None

    class Matches(BaseModel):
        track: typing.List[track.Match] 

    class Results(BaseModel):
        trackmatches: track.Matches
        opensearch_Query: OpensearchQuery = pydantic.Field(alias='opensearch:Query')
        opensearch_totalResults: int = pydantic.Field(alias='opensearch:totalResults')
        opensearch_startIndex: int = pydantic.Field(alias='opensearch:startIndex')
        opensearch_itemsPerPage: int = pydantic.Field(alias='opensearch:itemsPerPage')
        attr: Query = pydantic.Field(alias='@attr') # '@attr' seems to be always empty (https://lastfm-docs.github.io/api-docs/track/search/#examples)

    '''track.updateNowPlaying'''

    class Nowplaying(BaseModel):
        artist: track.Entity
        albumArtist: track.Entity
        album: track.Entity
        track: track.Entity
        ignoredMessage: track.IgnoredMessage


class user:


    class Type(str, enum.Enum):
        ALUM: str = 'alum'
        SUBCRIBER: str = 'subscriber'
        USER: str = 'user'

    class Attr(BaseModel):
        user: str
        fr: int = pydantic.Field(alias='from')
        to: int

    class Artist(BaseModel):
        name: str = pydantic.Field(alias='#text')
        mbid: typing.Optional[uuid.UUID] = None

    class Album(BaseModel):
        name: typing.Optional[str] = pydantic.Field(alias='#text')
        mbid: typing.Optional[uuid.UUID] = None

    class Date(BaseModel):
        uts: int
        dateTime: datetime.datetime = pydantic.Field(alias='#text')
        _ = validateDateTime('dateTime')

    class Pagination(BaseModel):
        user: str
        page: int
        perPage: int
        totalPages: int
        total: int

    class Name(BaseModel):
        user: str

    class Registered(BaseModel):
        unixtime: int
        dateTime: datetime.datetime = pydantic.Field(alias='#text')
        _ = validateDateTime('dateTime')


    '''user.getFriends'''

    class Friend(BaseModel):
        name: str
        realname: typing.Optional[str] = None
        url: pydantic.HttpUrl
        image: typing.List[Image]
        country: typing.Optional[str] = None
        registered: user.Registered
        usertype: user.Type = pydantic.Field(alias='type')
        subscriber: bool
        bootstrap: bool
        playcount: int
        playlists: int

    class Friends(BaseModel):
        user: typing.List[user.Friend]
        attr: user.Pagination = pydantic.Field(alias='@attr')

    '''user.getInfo'''

    class User(BaseModel):
        name: str
        realname: typing.Optional[str] = None
        url: pydantic.HttpUrl
        image: typing.List[Image]
        country: typing.Optional[str] = None
        gender: str
        age: int
        registered: user.Registered
        usertype: user.Type = pydantic.Field(alias='type')
        subscriber: bool
        bootstrap: bool
        playcount: int
        artist_count: int
        track_count: int
        album_count: int
        playlists: int

    '''user.getLovedTracks'''

    class LovedTrack(BaseModel):
        name: str
        mbid: typing.Optional[uuid.UUID] = None
        url: pydantic.HttpUrl
        image: typing.List[Image]
        artist: Entity
        streamable: Streamable
        date: user.Date

    class Lovedtracks(BaseModel):
        track: typing.List[user.LovedTrack]
        attr: user.Pagination = pydantic.Field(alias='@attr')

    '''user.getPersonalTags'''

    class TagPagination(BaseModel):
        user: str
        tag: str
        page: int
        perPage: int
        totalPages: int
        total: int

    class Tag(BaseModel):
        name: str
        mbid: typing.Optional[uuid.UUID] = None
        url: pydantic.HttpUrl
        image: typing.List[Image]
        streamable: typing.Optional[typing.Union[bool, Streamable]] = None
        duration: typing.Optional[int] = None
        artist: typing.Optional[Entity] = None

    class Tags(BaseModel):
        artist: typing.List[user.Tag] = None
        album: typing.List[user.Tag] = None
        track: typing.List[user.Tag] = None

    class Taggings(BaseModel):
        artists: typing.Optional[user.Tags] = None
        albums: typing.Optional[user.Tags] = None
        tracks: typing.Optional[user.Tags] = None
        attr: user.TagPagination = pydantic.Field(alias='@attr')

    '''user.getRecentTracks'''

    class NowPlaying(BaseModel):
        nowplaying: typing.Optional[bool] = None

    class RecentTrack(BaseModel):
        name: str
        mbid: typing.Optional[uuid.UUID] = None
        url: pydantic.HttpUrl
        image: typing.List[Image]
        date: typing.Optional[user.Date] = None
        artist: user.Artist
        album: user.Album
        streamable: bool
        attr: typing.Optional[user.NowPlaying] = pydantic.Field(alias='@attr', default=None)

    class ArtistExtended(BaseModel):
        name: str
        mbid: None # artist mbid is always missing with the `extended` option
        url: pydantic.HttpUrl
        image: typing.List[Image]

    class RecentTrackExtended(BaseModel):
        name: str
        mbid: typing.Optional[uuid.UUID] = None
        url: pydantic.HttpUrl
        image: typing.List[Image]
        date: typing.Optional[user.Date] = None
        artist: user.ArtistExtended
        album: user.Album
        streamable: bool
        loved: bool
        attr: typing.Optional[user.NowPlaying] = pydantic.Field(alias='@attr', default=None)

    class Recenttracks(BaseModel):
        track: typing.List[typing.Union[user.RecentTrack, user.RecentTrackExtended]]
        attr: user.Pagination = pydantic.Field(alias='@attr')

    '''user.getTopAlbums'''

    class TopAlbum(BaseModel):
        name: str
        mbid: typing.Optional[uuid.UUID] = None
        url: pydantic.HttpUrl
        image: typing.List[Image]
        artist: Entity
        playcount: int
        attr: Rank = pydantic.Field(alias='@attr')

    class Topalbums(BaseModel):
        album: typing.List[user.TopAlbum]
        attr: user.Pagination = pydantic.Field(alias='@attr')

    '''user.getTopArtists'''

    class TopArtist(BaseModel):
        name: str
        mbid: typing.Optional[uuid.UUID] = None
        url: pydantic.HttpUrl
        image: typing.List[Image]
        playcount: int
        streamable: bool
        attr: Rank = pydantic.Field(alias='@attr')

    class Topartists(BaseModel):
        artist: typing.List[user.TopArtist]
        attr: user.Pagination = pydantic.Field(alias='@attr')

    '''user.getTopTags'''

    class TopTag(BaseModel):
        name: str
        count: int
        url: pydantic.HttpUrl

    class Toptags(BaseModel):
        tag: typing.List[user.TopTag]
        attr: user.Name = pydantic.Field(alias='@attr')

    '''user.getTopTracks'''

    class TopTrack(BaseModel):
        name: str
        mbid: typing.Optional[uuid.UUID] = None
        url: pydantic.HttpUrl
        image: typing.List[Image]
        duration: int
        playcount: int
        artist: Entity
        streamable: Streamable
        attr: Rank = pydantic.Field(alias='@attr')

    class Toptracks(BaseModel):
        track: typing.List[user.TopTrack]
        attr: user.Pagination = pydantic.Field(alias='@attr')

    '''user.getWeeklyAlbumChart'''

    class WeeklyAlbum(BaseModel):
        name: str
        mbid: typing.Optional[uuid.UUID] = None
        url: pydantic.HttpUrl
        playcount: int
        artist: user.Artist
        attr: Rank = pydantic.Field(alias='@attr')

    class Weeklyalbumchart(BaseModel):
        album: typing.List[user.WeeklyAlbum]
        attr: user.Attr = pydantic.Field(alias='@attr')

    '''user.getWeeklyArtistChart'''

    class WeeklyArtist(BaseModel):
        name: str
        mbid: typing.Optional[uuid.UUID] = None
        url: pydantic.HttpUrl
        playcount: int
        attr: Rank = pydantic.Field(alias='@attr')

    class Weeklyartistchart(BaseModel):
        artist: typing.List[user.WeeklyArtist]
        attr: user.Attr = pydantic.Field(alias='@attr')

    '''user.getWeeklyChartList'''

    class WeeklyChart(BaseModel):
        chart: typing.Optional[str] = pydantic.Field(alias='#text', default=None)
        fr: int = pydantic.Field(alias='from')
        to: int

    class Weeklychartlist(BaseModel):
        chart: typing.List[user.WeeklyChart]
        attr: user.Name = pydantic.Field(alias='@attr')

    '''user.getWeeklyTrackChart'''

    class WeeklyTrack(BaseModel):
        name: str
        mbid: typing.Optional[uuid.UUID] = None
        url: pydantic.HttpUrl
        image: typing.List[Image]
        playcount: int
        artist: user.Artist
        attr: Rank = pydantic.Field(alias='@attr')

    class Weeklytrackchart(BaseModel):
        track: typing.List[user.WeeklyTrack]
        attr: user.Attr = pydantic.Field(alias='@attr')

    '''user.getTrackScrobbles'''

    class Trackscrobbles(BaseModel):
        track: typing.List[user.RecentTrack]
        attr: user.Pagination = pydantic.Field(alias='@attr')
