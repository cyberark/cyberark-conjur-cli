import base64
from enum import auto, Enum

import requests


class HttpVerb(Enum):
    GET = auto()
    POST = auto()
    PUT = auto()
    DELETE = auto()


def invoke_endpoint(http_verb, endpoint, params, *args, check_errors=True,
                    ssl_verify=True, auth=None, api_token=None):

    params = params or {}

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
