# -*- coding: utf-8 -*-

"""
Constants module

This module holds all constants used across the codebase
"""

# Builtins
import os

DEFAULT_CONFIG_FILE = os.path.expanduser(os.path.join('~', '.conjurrc'))
DEFAULT_NETRC_FILE = os.path.expanduser(os.path.join('~', '.netrc'))
DEFAULT_CERTIFICATE_FILE=os.path.expanduser(os.path.join('~', "conjur-server.pem"))
