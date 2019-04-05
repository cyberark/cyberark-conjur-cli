import base64
import logging
from enum import auto, Enum
from urllib.parse import quote

import requests


class HttpVerb(Enum):
    GET = auto()
    POST = auto()
    PUT = auto()
    DELETE = auto()


def invoke_endpoint(http_verb, endpoint, params, *args, check_errors=True,
                    ssl_verify=True, auth=None, api_token=None):

    orig_params = params or {}

    # Escape all params
    params = {}
    for key, value in orig_params.items():
        if key == 'url':
            params[key] = value
            continue
        params[key] = quote(value)

    url = endpoint.value.format(**params)

    headers={}
    if api_token and len(api_token) > 0:
        encoded_token = base64.b64encode(api_token.encode()).decode('utf-8')
        headers['Authorization'] = 'Token token="{}"'.format(encoded_token)

    request_method = getattr(requests, http_verb.name.lower())

    response = request_method(url, *args, verify=ssl_verify, auth=auth, headers=headers)

    if check_errors:
        response.raise_for_status()

    return response

def enable_http_logging(self):
    logging.warn("WARN: Using HTTP logging!")
    import logging
    from http.client import HTTPConnection

    HTTPConnection.debuglevel = 1

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True
