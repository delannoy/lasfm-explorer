#!/usr/bin/env python3

import uuid

from api.models import common

class Token(common.BaseModel):
    token: str

class Session(common.BaseModel):
    name: str
    key: uuid.UUID
    subscriber: bool
