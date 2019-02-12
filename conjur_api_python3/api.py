import base64

from datetime import datetime, timedelta
from enum import auto, Enum
from urllib.parse import quote

import requests

class HttpVerb(Enum):
    GET = auto()
    POST = auto()

class ConjurEndpoint(Enum):
    AUTHENTICATE = "{url}/authn/{account}/{login}/authenticate"
    LOGIN = "{url}/authn/{account}/login"
    SECRETS = "{url}/secrets/{account}/{kind}/{identifier}"

class Api(object):
    # Tokens should only be reused for 5 minutes (max lifetime is 8 minutes)
    API_TOKEN_DURATION = 5

    KIND_VARIABLE='variable'

    _api_token = None
    _api_token_expires_on = None

    def __init__(self, url, ca_bundle=None, account='default', ssl_verify=True, debug=False):
        if not url or not account:
            # TODO: Use custom error
            raise RuntimeError("Missing parameters in Api creation!")

        self._url = url
        self._ca_bundle = ca_bundle
        self._account = account

        self._ssl_verify = ssl_verify
        if ca_bundle:
            self._ssl_verify=ca_bundle

        self._default_params = {
            'url': url,
            'account': quote(account)
        }

        if not ssl_verify:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        if debug:
            import logging
            from http.client import HTTPConnection

            HTTPConnection.debuglevel = 1

            logging.basicConfig()
            logging.getLogger().setLevel(logging.DEBUG)
            requests_log = logging.getLogger("urllib3")
            requests_log.setLevel(logging.DEBUG)
            requests_log.propagate = True

    @property
    def api_token(self):
        if not self._api_token or datetime.now() > self._api_token_expires_on:
            print("API token missing or expired. Fetching new one...")
            self._api_token_expires_on = datetime.now() + timedelta(minutes=self.API_TOKEN_DURATION)
            self._api_token = self.authenticate()
            return self._api_token

        print("Using cached API token...")
        return self._api_token

    @property
    def api_key(self):
        return self._api_key

    @api_key.setter
    def api_key(self, value):
        self._api_key = value

    @property
    def login_id(self):
        return self._login_id

    @login_id.setter
    def login_id(self, value):
        self._login_id = value

    def login(self, login_id=None, password=None):
        """
        TODO
        """

        if not self._url or not login_id or not password:
            # TODO: Use custom error
            raise RuntimeError("Missing parameters in login invocation!")

        print("Logging in to {}...".format(self._url))
        self.api_key = self._invoke_endpoint(HttpVerb.GET, ConjurEndpoint.LOGIN,
                None, auth=(login_id, password)).text
        self.login_id = login_id

        return self.api_key

    def authenticate(self):
        """
        TODO
        """

        if not self._url or not self.login_id or not self.api_key:
            # TODO: Use custom error
            raise RuntimeError("Missing parameters in authentication invocation!")

        print("Authenticating to {}...".format(self._url))
        return self._invoke_endpoint(HttpVerb.POST, ConjurEndpoint.AUTHENTICATE,
                { 'login': quote(self.login_id) }, self.api_key).text

    def set_variable(self, variable_id, value):
        params = {
            'kind': self.KIND_VARIABLE,
            'identifier': quote(variable_id)
        }

        return self._invoke_endpoint(HttpVerb.POST, ConjurEndpoint.SECRETS, params,
                                     value, api_token=self.api_token).text

    def get_variable(self, variable_id):
        params = {
            'kind': self.KIND_VARIABLE,
            'identifier': quote(variable_id)
        }

        return self._invoke_endpoint(HttpVerb.GET, ConjurEndpoint.SECRETS, params,
                                     api_token=self.api_token).content

    def _invoke_endpoint(self, verb_id, endpoint_id, params, *args,
            check_errors=True, auth=None, api_token=None):

        params = params or {}

        url = ConjurEndpoint(endpoint_id).value.format(**self._default_params, **params)

        headers={}
        if api_token and len(api_token) > 0:
            encoded_token = base64.b64encode(api_token.encode()).decode('utf-8')
            headers['Authorization'] = 'Token token="{}"'.format(encoded_token)

        verb = HttpVerb(verb_id).name.lower()
        request_method = getattr(requests, verb)

        response = request_method(url, *args, verify=self._ssl_verify, auth=auth, headers=headers)
        if check_errors and response.status_code >= 300:
            # TODO: Use custom errors
            raise RuntimeError("Request failed: {}: {}".format(response.status_code,
                                                               response.text))

        return response
