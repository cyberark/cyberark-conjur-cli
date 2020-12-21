# -*- coding: utf-8 -*-

"""
Endpoints module

This module contains any classes needed for the rest of the
module to locate the required endpoints for the HTTP API
"""

from enum import Enum


class ConjurEndpoint(Enum):
    """
    ConjurEndpoint enumerates all endpoints that are required for
    API interactions with the Conjur instance along with any
    required parameters for the paths
    """
    AUTHENTICATE = "{url}/authn/{account}/{login}/authenticate"
    LOGIN = "{url}/authn/{account}/login"
    INFO = "{url}/info"
    POLICIES = "{url}/policies/{account}/policy/{identifier}"
    BATCH_SECRETS = "{url}/secrets"
    SECRETS = "{url}/secrets/{account}/{kind}/{identifier}"
    RESOURCES = "{url}/resources/{account}"
    WHOAMI = "{url}/whoami"
