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
    BATCH_SECRETS = "{url}/secrets"
    LOGIN = "{url}/authn/{account}/login"
    POLICIES = "{url}/policies/{account}/policy/{identifier}"
    RESOURCES = "{url}/resources/{account}"
    SECRETS = "{url}/secrets/{account}/{kind}/{identifier}"
    WHOAMI = "{url}/whoami"
