#!/usr/bin/env python3

import os
import urllib.request

import lxml.html
import pandas

import api.auth

headers = {'User-Agent': os.getenv('USERAGENT', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36')} # https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/User-Agent

def getEtree(url: str) -> lxml.html.HtmlElement:
    '''Get HTML request and return as etree element.'''
    request = urllib.request.Request(url=url, headers=headers)
    response = urllib.request.urlopen(url=request)
    return lxml.html.fromstring(html=response.read().decode('utf-8'))

def neighbors(user: str = api.auth.user) -> pandas.DataFrame:
    '''Parse lastFM neighbors page for {user}.'''
    etree = getEtree(url=f'https://www.last.fm/user/{user}/neighbours')
    users = [user.text for user in etree.cssselect(expr='a.user-list-link')]
    artists = [[artist.text for artist in user.cssselect(expr='a')] for user in etree.cssselect(expr='p.user-list-shared-artists')]
    return pandas.DataFrame({'user': users, 'artists_in_common': artists})
