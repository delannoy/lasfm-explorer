#!/usr/bin/env python3

import uuid

# https://www.last.fm/api/account/create
# https://www.last.fm/api/accounts
api_key = uuid.UUID('APIKEY').hex
api_secret = uuid.UUID('APISECRET').hex

# https://www.last.fm/api/show/auth.getSession
sk = 'SK'

user = 'USER'
