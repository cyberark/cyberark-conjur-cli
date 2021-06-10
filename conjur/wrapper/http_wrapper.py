# -*- coding: utf-8 -*-

"""
Http module
This module aggregates all methods directly needed to interact with
HTTP-based endpoints in a generic way
"""

import base64
import logging
import re
from enum import Enum
from urllib.parse import quote
import requests
import urllib3

from conjur.errors import CertificateHostnameMismatchException
from conjur.api.endpoints import ConjurEndpoint


class HttpVerb(Enum):
    """
    Enumeration of all possible HTTP methods that we may use against
    the HTTP API endpoint
    """
    GET = 1
    POST = 2
    PUT = 3
    DELETE = 4
    PATCH = 5


# pylint: disable=too-many-locals
# ssl_verify can accept Boolean or String as per requests docs
# https://requests.readthedocs.io/en/master/api/#main-interface
def invoke_endpoint(http_verb: HttpVerb, endpoint: ConjurEndpoint, params: dict, *args,
                    check_errors: bool = True, ssl_verify: bool = True,
                    auth: tuple = None, api_token: str = None,
                    query: dict = None) -> requests.Response:
    """
    This method flexibly invokes HTTP calls from 'requests' module
    """
    urllib3.disable_warnings()
    orig_params = params or {}
    # Escape all params
    params = {}
    for key, value in orig_params.items():
        if key == 'url':
            params[key] = value
            continue
        params[key] = quote(value, safe='')

    url = endpoint.value.format(**params)

    headers = {}
    if api_token:
        encoded_token = base64.b64encode(api_token.encode()).decode('utf-8')
        headers['Authorization'] = 'Token token="{}"'.format(encoded_token)

    # By default, on each request the certificate will be verified. If there is
    # a failure in verification, the fallback solution will be passing in the
    # server pem received during initialization of the client
    # pylint: disable=not-callable
    try:
        response = invoke_request(http_verb,
                                  url, *args,
                                  query=query,
                                  ssl_verify=True,
                                  auth=auth,
                                  headers=headers)
    except requests.exceptions.SSLError:
        response = invoke_request(http_verb,
                                  url, *args,
                                  query=query,
                                  ssl_verify=ssl_verify,
                                  auth=auth,
                                  headers=headers)

    if check_errors:
        # takes the "requests" response object and expands the
        # raise_for_status method to return more helpful errors for debug logs
        try:
            response.raise_for_status()
        except requests.exceptions.HTTPError as http_error:
            if response.text:
                logging.debug(requests.exceptions.HTTPError(f"{http_error.response.status_code}"
                                                            f" {http_error.response.reason}"
                                                            f" {response.text}"))
            raise http_error
        except Exception as general_error:
            raise general_error

    return response


def invoke_request(http_verb: HttpVerb, url: str, *args, query: dict, ssl_verify: bool, auth: tuple,
                   headers: dict) -> requests.Response:
    """
    This method preforms the actual request and catches possible SSLErrors to
    perform more user-friendly messages
    """
    request_method = getattr(requests, http_verb.name.lower())

    try:
        return request_method(url, *args,
                              params=query,
                              verify=ssl_verify,
                              auth=auth,
                              headers=headers)

    except requests.exceptions.SSLError as ssl_error:
        host_mismatch_message = re.search("hostname '.+' doesn't match", str(ssl_error))
        if host_mismatch_message:
            raise CertificateHostnameMismatchException from ssl_error
        raise ssl_error

# Not coverage tested since this code should never be hit
# from checked-in code
def enable_http_logging():  # pragma: no cover
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

    # pylint: disable=unreachable,import-outside-toplevel
    # pylint: disable=import-outside-toplevel
    from http.client import HTTPConnection
    HTTPConnection.debuglevel = 1

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)

    logging.warning("WARN: Using HTTP logging!")
    requests_log = logging.getLogger("urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True
