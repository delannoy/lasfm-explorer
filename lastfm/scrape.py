#!/usr/bin/env python3

from __future__ import annotations
import dataclasses
import logging
import os

import httpx
import lxml.html
import pandas
import rich.console
import rich.table

import api.auth
import log

log.log.setLevel(logging.getLevelName('INFO'))

def neighbors(user: str = api.auth.user) -> pandas.DataFrame:
    '''Parse lastFM neighbors page for {user}.'''
    etree = lxml.html.fromstring(httpx.get(url=f'https://www.last.fm/user/{user}/neighbours').text)
    users = [user.text for user in etree.cssselect(expr='a.user-list-link')]
    artists = [[artist.text for artist in user.cssselect(expr='a')] for user in etree.cssselect(expr='p.user-list-shared-artists')]
    data = pandas.DataFrame({'user': users, 'artists_in_common': artists})
    rich.console.Console().print(Recommended.table(data=data, title='Neighbors'))


@dataclasses.dataclass
class Recommended:
    url: str = httpx.URL('https://www.last.fm/music/+recommended')

    def __post_init__(self):
        self.client = self.login()

    def login(self) -> httpx.Client:
        # [How to "log in" to a website using Python's Requests module?](https://stackoverflow.com/a/17633072)
        # [python-requests and django - CSRF verification failed. Request aborted](https://stackoverflow.com/a/20252654)
        url = httpx.URL('https://www.last.fm/login')
        client = httpx.Client()
        csrftoken = client.get(url=url).cookies.get('csrftoken')
        data = dict(csrfmiddlewaretoken=csrftoken, username_or_email=api.auth.user, password=os.getenv('LASTFM_PASSWORD'))
        user_agent = os.getenv('USERAGENT', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36')
        headers = httpx.Headers({'User-Agent': user_agent, 'Referer': str(url)})
        response = client.post(url=url, data=data, headers=headers)
        return client

    @staticmethod
    def table(data: pandas.DataFrame, title: str) -> rich.table.Table:
        '''Print `data`: pandas.DataFrame as a `rich.table`.''' # [Convert a pandas.DataFrame object into a rich.Table object for stylized printing in Python.](https://gist.github.com/avi-perl/83e77d069d97edbdde188a4f41a015c4)
        table = rich.table.Table(title=title, border_style='blue', header_style='bold', show_edge=False, row_styles=['dim', ''])
        [table.add_column(str(col), max_width=120, no_wrap=True) for col in data.columns]
        [table.add_row(*[str(x) for x in val]) for val in data.values]
        return table

    def albums(self, page: int = 1) -> pandas.DataFrame:
        etree = lxml.html.fromstring(self.client.get(url=f'{self.url}/albums?page={page}').text)
        buffer = etree.cssselect(expr='div.col-main div.link-block')
        albums = [e.cssselect('h3 a')[0].text for e in buffer]
        artists = [e.cssselect('p a')[0].text for e in buffer]
        listeners = [int(e.cssselect('div.music-recommended-albums-album-info p')[0].text.strip().replace(',', '')) for e in buffer]
        tracks = [int(e.cssselect('p.music-recommended-albums-album-info-item')[0].text.split(' ')[0]) if e.cssselect('p.music-recommended-albums-album-info-item') else 0 for e in buffer]
        similar = [[_.text for _ in e.cssselect('p.music-recommended-albums-album-context a')] for e in buffer]
        data = pandas.DataFrame(data={'albums': albums, 'artists': artists, 'listeners': listeners, 'tracks': tracks, 'similar': similar})
        rich.console.Console().print(self.table(data=data, title=f'{self.__class__.__name__} Albums'))

    def artists(self, page: int = 1) -> pandas.DataFrame:
        etree = lxml.html.fromstring(self.client.get(url=f'{self.url}/artists?page={page}').text)
        buffer = etree.cssselect(expr='div.col-main ul li.link-block')
        artists = [e.cssselect('h3 a')[0].text for e in buffer]
        tags = [[tag.text for tag in e.cssselect('li.tag a')] for e in buffer]
        listeners = [int(e.cssselect('p.music-recommended-artists-artist-stats')[0].text.strip().replace(',', '')) for e in buffer]
        bio = [e.cssselect('p.factbox-summary')[0].text if e.cssselect('p.factbox-summary') else '' for e in buffer]
        similar = [[_.text for _ in e.cssselect('p.music-recommended-artists-context a')] for e in buffer]
        data = pandas.DataFrame(data={'artists': artists, 'tags': tags, 'listeners': listeners, 'bio': bio, 'similar': similar})
        rich.console.Console().print(self.table(data=data, title=f'{self.__class__.__name__} Artists'))

    def rediscover(self, page: int = 1) -> pandas.DataFrame:
        etree = lxml.html.fromstring(self.client.get(url=f'{self.url}/rediscover?page={page}').text)
        buffer = etree.cssselect(expr='div.col-main li.link-block')
        artists = [e.cssselect('h3 a')[0].text for e in buffer]
        tags = [[tag.text for tag in e.cssselect('li.tag a')] for e in buffer]
        listeners = [int(e.cssselect('p.music-recommended-artists-artist-stats')[0].text.strip().replace(',', '')) for e in buffer]
        last_played = [e.cssselect('div.music-recommended-artists-context p')[0].text[12:] for e in buffer]
        listens = [int(e.cssselect('div.music-recommended-artists-context p')[1].text.split(' ')[0].replace(',', '')) for e in buffer]
        data = pandas.DataFrame(data={'artists': artists, 'tags': tags, 'listeners': listeners, 'last_played': last_played, 'listens': listens})
        rich.console.Console().print(self.table(data=data, title='Rediscover'))

    def tags(self, page: int = 1) -> pandas.DataFrame:
        etree = lxml.html.fromstring(self.client.get(url=f'{self.url}/tags?page={page}').text)
        buffer = etree.cssselect(expr='div.col-main div.link-block')
        tags = [e.cssselect('h3 a')[0].text for e in buffer]
        artists = [[_.text for _ in e.cssselect('p a')] for e in buffer]
        data = pandas.DataFrame(data={'tags': tags, 'artists': artists})
        rich.console.Console().print(self.table(data=data, title=f'{self.__class__.__name__} Tags'))

    def tracks(self, page: int = 1) -> pandas.DataFrame:
        etree = lxml.html.fromstring(self.client.get(url=f'{self.url}/tracks?page={page}').text)
        buffer = etree.cssselect(expr='div.col-main div.link-block')
        tracks = [e.cssselect('h3 a')[0].text for e in buffer]
        artists = [e.cssselect('p a')[0].text for e in buffer]
        listeners = [int(e.cssselect('p.recommended-tracks-item-listeners')[0].text.strip().split(' ')[0].replace(',', '')) for e in buffer]
        similar = [[_.text for _ in e.cssselect('p.recommended-tracks-item-context a')] for e in buffer]
        data = pandas.DataFrame(data={'tracks': tracks, 'artists': artists, 'listeners': listeners, 'similar': similar})
        rich.console.Console().print(self.table(data=data, title=f'{self.__class__.__name__} Tracks'))
