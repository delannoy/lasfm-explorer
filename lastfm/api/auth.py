#!/usr/bin/env python3

import uuid

import typ

user: str = 'USER'

# https://www.last.fm/api/account/create
# https://www.last.fm/api/accounts
api_key: typ.uuid = uuid.UUID('APIKEY').hex
