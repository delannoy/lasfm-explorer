#!/usr/bin/env python3

import logging

import rich.logging

log_level = logging.DEBUG

# [Logging Handler](https://rich.readthedocs.io/en/stable/logging.html)
handler = rich.logging.RichHandler(rich_tracebacks=True, log_time_format="[%Y-%m-%d %H:%M:%S]") # [rich.logging](https://rich.readthedocs.io/en/stable/reference/logging.html)
logging.basicConfig(level=log_level, format='%(message)s', handlers=[handler])
log = logging.getLogger()
