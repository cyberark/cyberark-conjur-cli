# -*- coding: utf-8 -*-

"""
Http module
This module aggregates all methods directly needed to interact with
HTTP-based endpoints in a generic way
"""

import base64
import logging
import re
import ssl
from enum import Enum
from typing import Union
from urllib.parse import quote
import asyncio
from aiohttp import BasicAuth, ClientError, ClientResponseError, ClientSSLError, ClientSession
import async_timeout
import urllib3

from conjur.errors import CertificateHostnameMismatchException, HttpSslError, HttpError,HttpStatusError
from conjur.api.endpoints import ConjurEndpoint
from conjur.wrapper.http_response import HttpResponse

REQUEST_TIMEOUT_SECONDS = 10


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


# pylint: disable=too-many-locals,consider-using-f-string,too-many-arguments
# ssl_verify can accept Boolean or String of the path to certificate file
def invoke_endpoint(http_verb: HttpVerb,
                    endpoint: ConjurEndpoint,
                    params: dict,
                    data: str = "",
                    check_errors: bool = True,
                    ssl_verify: Union[bool, str] = True,
                    auth: tuple = None,
                    api_token: str = None,
                    query: dict = None,
                    headers=None,
                    decode_token=True) -> HttpResponse:
    """
    This method flexibly invokes HTTP calls from 'aiohttp' module
    """
    if headers is None:
        headers = {}

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

    if api_token:
        if decode_token:  # host factory token does not require encoding
            api_token = base64.b64encode(api_token.encode()).decode('utf-8')

        headers['Authorization'] = f'Token token="{api_token}"'

    # By default, on each request the certificate will be verified. If there is
    # a failure in verification, the fallback solution will be passing in the
    # server pem received during initialization of the client
    # pylint: disable=not-callable

    try:
        response = asyncio.run(invoke_request(http_verb,
                                              url,
                                              data,
                                              query=query,
                                              ssl_verify=True,
                                              auth=auth,
                                              headers=headers))
    except HttpSslError:
        response = asyncio.run(invoke_request(http_verb,
                                              url,
                                              data,
                                              query=query,
                                              ssl_verify=ssl_verify,
                                              auth=auth,
                                              headers=headers))

    if check_errors:
        # takes the response object and expands the raise_for_status method
        # to return more helpful errors for debug logs
        try:
            response.raise_for_status()
        except ClientResponseError as http_error:
            if response.text:
                logging.debug(HttpError(f"{http_error.status} "
                                        f"{http_error.message} "
                                        f"{response.text}"))

            if http_error.status != 0:
                raise HttpStatusError(status=http_error.status,
                                      message=http_error.message,
                                      url=str(http_error.request_info.real_url),
                                      response=response.text) from http_error

            raise HttpError from http_error
        except Exception as general_error:
            raise HttpError from general_error

    return response


# pylint: disable=too-many-arguments
async def invoke_request(http_verb: HttpVerb,
                         url: str,
                         data: str,
                         query: dict,
                         ssl_verify: Union[bool, str],
                         auth: tuple,
                         headers: dict) -> HttpResponse:
    """
    This method preforms the actual request and catches possible SSLErrors to
    perform more user-friendly messages
    """
    async with ClientSession() as session:
        async with async_timeout.timeout(REQUEST_TIMEOUT_SECONDS):
            ssl_context = __create_ssl_context(ssl_verify)

            try:
                async with session.request(http_verb.name,
                                           url,
                                           data=data,
                                           params=query,
                                           ssl=ssl_context,
                                           auth=BasicAuth(*auth) if auth else None,
                                           headers=headers) as response:
                    return await HttpResponse.from_client_response(response)

            except ClientSSLError as ssl_error:
                host_mismatch_message = re.search("hostname '.+' doesn't match", str(ssl_error))
                if host_mismatch_message:
                    raise CertificateHostnameMismatchException from ssl_error
                raise HttpSslError(message=str(ssl_error)) from ssl_error
            except ClientError as request_error:
                raise HttpError() from request_error


def __create_ssl_context(ssl_verify: Union[bool, str]) -> Union[bool, ssl.SSLContext]:
    if not ssl_verify:
        return False

    if ssl_verify is True:
        ssl_context = ssl.create_default_context()
    else:
        ssl_context = ssl.create_default_context(cafile=ssl_verify)

    ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
    # pylint: disable=no-member
    ssl_context.verify_flags |= ssl.OP_NO_TICKET

    return ssl_context


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
