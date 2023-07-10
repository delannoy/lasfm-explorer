#!/usr/bin/env python3

import pandas

def relatedArtists(artistID: int = 2814) -> pandas.DataFrame:
    # [Artist / Related](https://developers.deezer.com/api/artist/related)
    return pandas.json_normalize(pandas.read_json(f'https://api.deezer.com/artist/{artistID}/related').data)
