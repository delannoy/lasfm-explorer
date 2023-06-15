#!/usr/bin/env python3

import enum

import pydantic

import param
import request
import typ
import api.auth


class Period(enum.Enum):
    OVERALL = 'overall'
    SEVEN_DAYS= '7day'
    ONE_WEEK = '7day'
    THIRTY_DAYS = '1month'
    ONE_MONTH = '1month'
    THREE_MONTHS = '3month'
    SIX_MONTHS = '6month'
    TWELVE_MONTHS = '12month'
    ONE_YEAR = '12month'


class TaggingType(enum.Enum):
    ARTIST = 'artist'
    ALBUM = 'album'
    TRACK = 'track'


@param.required
@pydantic.validate_arguments
def getFriends(method: str, api_key: typ.UUID, user: str = api.auth.user, recenttracks: int = 0, limit: int = 50, page: int = 1) -> typ.response:
    '''Get a list of the user's friends on Last.fm.
        user         : Required : The last.fm username to fetch the friends of.
        recenttracks : Optional : Whether or not to include information about friends' recent listening in the response.
        limit        : Optional : The number of results to fetch per page. Defaults to 50.
        page         : Optional : The page number to fetch. Defaults to first page.
        api_key      : Required : A Last.fm API key.
    '''
    return request.get(url=param.url, headers=param.headers, params=param.params(locals()))

@param.required
@pydantic.validate_arguments
def getInfo(method: str, api_key: typ.UUID, user: str = api.auth.user) -> typ.response:
    '''Get information about a user profile.
        user    : Optional : The user to fetch info for. Defaults to the authenticated user.
        api_key : Required : A Last.fm API key.
    '''
    return request.get(url=param.url, headers=param.headers, params=param.params(locals()))

@param.required
@pydantic.validate_arguments
def getLovedTracks(method: str, api_key: typ.UUID, user: str = api.auth.user, limit: int = 50, page: int = 1) -> typ.response:
    '''Get the last 50 tracks loved by a user.
        user    : Required : The user name to fetch the loved tracks for.
        limit   : Optional : The number of results to fetch per page. Defaults to 50.
        page    : Optional : The page number to fetch. Defaults to first page.
        api_key : Required : A Last.fm API key.
    '''
    return request.get(url=param.url, headers=param.headers, params=param.params(locals()))

@param.required
@pydantic.validate_arguments(config=dict(use_enum_values=True))
def getPersonalTags(method: str, api_key: typ.UUID, tag: str, taggingtype: TaggingType, user: str = api.auth.user, limit: int = 50, page: int = 1) -> typ.response:
    '''Get the user's personal tags
        user        : Required : The user who performed the taggings.
        tag         : Required : The tag you're interested in.
        taggingtype : Required : The type of items which have been tagged [artist|album|track]
        limit       : Optional : The number of results to fetch per page. Defaults to 50.
        page        : Optional : The page number to fetch. Defaults to first page.
        api_key     : Required : A Last.fm API key.
    '''
    return request.get(url=param.url, headers=param.headers, params=param.params(locals()))

@param.required
@pydantic.validate_arguments
def getRecentTracks(method: str, api_key: typ.UUID, user: str = api.auth.user, FROM: typ.UnixTimestamp = None, to: typ.UnixTimestamp = None, limit: int = 50, page: int = 1, extended: int = 0) -> typ.response:
    '''Get a list of the recent tracks listened to by this user. Also includes the currently playing track with the nowplaying="true" attribute if the user is currently listening.
        user     : Required : The last.fm username to fetch the recent tracks of.
        from     : Optional : Beginning timestamp of a range - only display scrobbles after this time, in UNIX timestamp format (integer number of seconds since 00 : 00 : 00, January 1st 1970 UTC). This must be in the UTC time zone.
        to       : Optional : End timestamp of a range - only display scrobbles before this time, in UNIX timestamp format (integer number of seconds since 00 : 00 : 00, January 1st 1970 UTC). This must be in the UTC time zone.
        limit    : Optional : The number of results to fetch per page. Defaults to 50. Maximum is ~~200~~ 1000.
        page     : Optional : The page number to fetch. Defaults to first page.
        extended : Optional : Includes extended data in each artist, and whether or not the user has loved each track [0|1]
        api_key  : Required : A Last.fm API key.
    '''
    return request.get(url=param.url, headers=param.headers, params=param.params(locals()))

@param.required
@pydantic.validate_arguments(config=dict(use_enum_values=True))
def getTopAlbums(method: str, api_key: typ.UUID, user: str = api.auth.user, period: Period = None, limit: int = 50, page: int = 1) -> typ.response:
    '''Get the top albums listened to by a user. You can stipulate a time period. Sends the overall chart by default.
        user    : Required : The user name to fetch top albums for.
        period  : Optional : overall | 7day | 1month | 3month | 6month | 12month - The time period over which to retrieve top albums for.
        limit   : Optional : The number of results to fetch per page. Defaults to 50.
        page    : Optional : The page number to fetch. Defaults to first page.
        api_key : Required : A Last.fm API key.
    '''
    return request.get(url=param.url, headers=param.headers, params=param.params(locals()))

@param.required
@pydantic.validate_arguments(config=dict(use_enum_values=True))
def getTopArtists(method: str, api_key: typ.UUID, user: str = api.auth.user, period: Period = None, limit: int = 50, page: int = 1) -> typ.response:
    '''Get the top artists listened to by a user. You can stipulate a time period. Sends the overall chart by default.
        user    : Required : The user name to fetch top artists for.
        period  : Optional : overall | 7day | 1month | 3month | 6month | 12month - The time period over which to retrieve top artists for.
        limit   : Optional : The number of results to fetch per page. Defaults to 50.
        page    : Optional : The page number to fetch. Defaults to first page.
        api_key : Required : A Last.fm API key.
    '''
    return request.get(url=param.url, headers=param.headers, params=param.params(locals()))

@param.required
@pydantic.validate_arguments
def getTopTags(method: str, api_key: typ.UUID, user: str = api.auth.user, limit: int = 50) -> typ.response:
    '''Get the top tags used by this user.
        user    : Required : The user name
        limit   : Optional : Limit the number of tags returned
        api_key : Required : A Last.fm API key.
    '''
    return request.get(url=param.url, headers=param.headers, params=param.params(locals()))

@param.required
@pydantic.validate_arguments(config=dict(use_enum_values=True))
def getTopTracks(method: str, api_key: typ.UUID, user: str = api.auth.user, period: Period = None, limit: int = 50, page: int = 1) -> typ.response:
    '''Get the top tracks listened to by a user. You can stipulate a time period. Sends the overall chart by default.
        user    : Required : The user name to fetch top tracks for.
        period  : Optional : overall | 7day | 1month | 3month | 6month | 12month - The time period over which to retrieve top tracks for.
        limit   : Optional : The number of results to fetch per page. Defaults to 50.
        page    : Optional : The page number to fetch. Defaults to first page.
        api_key : Required : A Last.fm API key.
    '''
    return request.get(url=param.url, headers=param.headers, params=param.params(locals()))

@param.required
@pydantic.validate_arguments
def getWeeklyAlbumChart(method: str, api_key: typ.UUID, user: str = api.auth.user, FROM: typ.UnixTimestamp = None, to: typ.UnixTimestamp = None) -> typ.response:
    '''Get an album chart for a user profile, for a given date range. If no date range is supplied, it will return the most recent album chart for this user.
        user    : Required : The last.fm username to fetch the charts of.
        from    : Optional : The date at which the chart should start from. See User.getChartsList for more.
        to      : Optional : The date at which the chart should end on. See User.getChartsList for more.
        api_key : Required : A Last.fm API key.
    '''
    return request.get(url=param.url, headers=param.headers, params=param.params(locals()))

@param.required
@pydantic.validate_arguments
def getWeeklyArtistChart(method: str, api_key: typ.UUID, user: str = api.auth.user, FROM: typ.UnixTimestamp = None, to: typ.UnixTimestamp = None) -> typ.response:
    '''Get an artist chart for a user profile, for a given date range. If no date range is supplied, it will return the most recent artist chart for this user.
        user    : Required : The last.fm username to fetch the charts of.
        from    : Optional : The date at which the chart should start from. See User.getChartsList for more.
        to      : Optional : The date at which the chart should end on. See User.getChartsList for more.
        api_key : Required : A Last.fm API key.
    '''
    return request.get(url=param.url, headers=param.headers, params=param.params(locals()))

@param.required
@pydantic.validate_arguments
def getWeeklyTrackChart(method: str, api_key: typ.UUID, user: str = api.auth.user, FROM: typ.UnixTimestamp = None, to: typ.UnixTimestamp = None) -> typ.response:
    '''Get a track chart for a user profile, for a given date range. If no date range is supplied, it will return the most recent track chart for this user.
        user    : Required : The last.fm username to fetch the charts of.
        from    : Optional : The date at which the chart should start from. See User.getChartsList for more.
        to      : Optional : The date at which the chart should end on. See User.getChartsList for more.
        api_key : Required : A Last.fm API key.
    '''
    return request.get(url=param.url, headers=param.headers, params=param.params(locals()))

@param.required
@pydantic.validate_arguments
def getWeeklyChartList(method: str, api_key: typ.UUID, user: str = api.auth.user) -> typ.response:
    '''Get a list of available charts for this user, expressed as date ranges which can be sent to the chart services.
        user    : Required : The last.fm username to fetch the charts list for.
        api_key : Required : A Last.fm API key.
    '''
    return request.get(url=param.url, headers=param.headers, params=param.params(locals()))

@param.required
@pydantic.validate_arguments
def getTrackScrobbles(method: str, api_key: typ.UUID, artist: str, track: str, user: str = api.auth.user, limit: int = 50, page: int = 1) -> typ.response:
    '''[... there is a new method user.getTrackScrobbles which is just like user.getArtistTracks, except also takes a "track" parameter.](https://github.com/pylast/pylast/issues/298)'''
    return request.get(url=param.url, headers=param.headers, params=param.params(locals()))
