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
                    ssl_verify=True, auth=None, api_token=None, query=None):
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
    response = request_method(url, *args,
                              params=query,
                              verify=ssl_verify,
                              auth=auth,
                              headers=headers)

    if check_errors:
        response.raise_for_status()

    return response

# Not coverage tested since this code should never be hit
# from checked-in code
def enable_http_logging(): #pragma: no cover
    """
    This method enables verbose http logging, which may be useful
    for debugging problems with invocation code.

    WARNING: Do not check in code with this method called or you
             may leak secrets to stdout!
    """

    # This exception here is to allow code reviewers to explicitly
    # see if anyone is trying to enable this functionality in clients
    # that should never be checked in. This line should always be at
    # the beginning of the method.
    raise RuntimeError("If this line gets checked in uncommented or"
                       "is removed, the PR should not be approved")

    # pylint: disable=unreachable
    import logging
    from http.client import HTTPConnection
    HTTPConnection.debuglevel = 1

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)

    logging.warning("WARN: Using HTTP logging!")
    requests_log = logging.getLogger("urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True
