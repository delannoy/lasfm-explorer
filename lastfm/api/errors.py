#!/usr/bin/env python3

import enum


class Errors(enum.IntEnum):
    '''https://www.last.fm/api/errorcodes'''

    def __new__(cls, value: int, doc: str = ''):
        '''override Enum.__new__ to take a doc argument'''
        # [How can I attach documentation to members of a python enum?](https://stackoverflow.com/a/50473952)
        self = int.__new__(cls, value)
        self._value_ = value
        self.__doc__ = doc
        return self

    INVALID_SERVICE = (2, "Invalid service - This service does not exist")
    INVALID_METHOD = (3, "Invalid Method - No method with that name in this package")
    AUTHENTICATION_FAILED = (4, "Authentication Failed - You do not have permissions to access the service")
    INVALID_FORMAT = (5, "Invalid format - This service doesn't exist in that format")
    INVALID_PARAMETERS = (6, "Invalid parameters - Your request is missing a required parameter")
    INVALID_RESOURCE = (7, "Invalid resource specified")
    OPERATION_FAILED = (8, "Operation failed - Something else went wrong")
    INVALID_SESSION_KEY = (9, "Invalid session key - Please re-authenticate")
    INVALID_API_KEY = (10, "Invalid API key - You must be granted a valid key by last.fm")
    SERVICE_OFFLINE = (11, "Service Offline - This service is temporarily offline. Try again later.")
    SUBSCRIBERS_ONLY = (12, "Subscribers Only - This station is only available to paid last.fm subscribers")
    INVALID_METHOD_SIGNATURE = (13, "Invalid method signature supplied")
    UNAUTHORIZED_TOKEN = (14, "Unauthorized Token - This token has not been authorized")
    EXPIRED_TOKEN = (15, "This item is not available for streaming.")
    TEMPORARY_ERROR = (16, "The service is temporarily unavailable, please try again.")
    LOGIN_REQUIRED = (17, "Login: User requires to be logged in")
    TRIAL_EXPIRED = (18, "Trial Expired - This user has no free radio plays left. Subscription required.")
    NOT_ENOUGH_CONTENT = (20, "Not Enough Content - There is not enough content to play this station")
    NOT_ENOUGH_MEMBERS = (21, "Not Enough Members - This group does not have enough members for radio")
    NOT_ENOUGH_FANS = (22, "Not Enough Fans - This artist does not have enough fans for for radio")
    NOT_ENOUGH_NEIGHBOURS = (23, "Not Enough Neighbours - There are not enough neighbours for radio")
    NO_PEAK_RADIO = (24, "No Peak Radio - This user is not allowed to listen to radio during peak usage")
    RADIO_NOT_FOUND = (25, "Radio Not Found - Radio station not found")
    SUSPENDED_API_KEY = (26, "API Key Suspended - This application is not allowed to make requests to the web services")
    DEPRECATED  = (27, "Deprecated - This type of request is no longer supported")
    RATE_LIMIT_EXCEEDED = (29, "Rate Limit Exceded - Your IP has made too many requests in a short period, exceeding our API guidelines")


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
