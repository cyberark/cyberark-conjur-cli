# -*- coding: utf-8 -*-

"""
Http module

This module aggregates all methods directly needed to interact with
HTTP-based endpoints in a generic way
"""

import base64
from enum import auto, Enum
from urllib.parse import quote

import requests


class HttpVerb(Enum):
    """
    Enumeration of all possible HTTP methods that we may use against
    the HTTP API endpoint
    """
    GET = auto()
    POST = auto()
    PUT = auto()
    DELETE = auto()


#pylint: disable=too-many-locals
def invoke_endpoint(http_verb, endpoint, params, *args, check_errors=True,
                    ssl_verify=True, auth=None, api_token=None):
    """
    This method flexibly invokes HTTP calls from 'requests' module
    """

    orig_params = params or {}

    # Escape all params
    params = {}
    for key, value in orig_params.items():
        if key == 'url':
            params[key] = value
            continue
        params[key] = quote(value)

    url = endpoint.value.format(**params)

    headers = {}
    if api_token:
        encoded_token = base64.b64encode(api_token.encode()).decode('utf-8')
        headers['Authorization'] = 'Token token="{}"'.format(encoded_token)

    request_method = getattr(requests, http_verb.name.lower())

    #pylint: disable=not-callable
    response = request_method(url, *args, verify=ssl_verify, auth=auth, headers=headers)

    if check_errors:
        response.raise_for_status()

    return response

def enable_http_logging():
    """
    This method enables verbose http logging, which may be useful
    for debugging problems with invocation code.

    WARNING: Do not check in code with this method called or you
             may leak secrets to stdout!
    """
    import logging
    from http.client import HTTPConnection
    HTTPConnection.debuglevel = 1

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)

    logging.warning("WARN: Using HTTP logging!")
    requests_log = logging.getLogger("urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True
