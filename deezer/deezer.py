#!/usr/bin/env python3

from __future__ import annotations
import json
import urllib

def relatedArtists(artistID: int = 2814) -> dict[str, int]:
    '''[Artist / Related](https://developers.deezer.com/api/artist/related)'''
    response = urllib.request.urlopen('https://api.deezer.com/artist/2814/related').read().decode('utf-8')
    return {artist.get('name'): artist.get('id') for artist in json.loads(response).get('data')}

def releaseDate(albumID: int = 53318422) -> str:
    '''[Album](https://developers.deezer.com/api/album)'''
    response = urllib.request.urlopen(f'https://api.deezer.com/album/{albumID}').read().decode('utf-8')
    return json.loads(response).get('release_date')
