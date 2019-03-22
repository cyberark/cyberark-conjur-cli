import logging

from datetime import datetime, timedelta
from urllib.parse import quote

from .endpoints import ConjurEndpoint
from .http import HttpVerb, invoke_endpoint

class Api(object):
    # Tokens should only be reused for 5 minutes (max lifetime is 8 minutes)
    API_TOKEN_DURATION = 5

    KIND_VARIABLE='variable'

    _api_token = None
    _api_token_expires_on = None

    def __init__(self,
                 account='default',
                 api_key=None,
                 ca_bundle=None,
                 http_debug=False,
                 login_id=None,
                 plugins=[],
                 ssl_verify=True,
                 url=None):

        self._url = url
        self._ca_bundle = ca_bundle
        self._account = account

        self._ssl_verify = ssl_verify
        if ca_bundle:
            self._ssl_verify = ca_bundle

        self.api_key = api_key
        self.login_id = login_id

        self._default_params = {
            'url': url,
            'account': quote(account)
        }

        if not ssl_verify:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # WARNING: ONLY FOR DEBUGGING - DO NOT CHECK IN LINE BELOW UNCOMMENTED
        # if http_debug: enable_http_logging()

    @property
    def api_token(self):
        if not self._api_token or datetime.now() > self._api_token_expires_on:
            logging.info("API token missing or expired. Fetching new one...")
            self._api_token_expires_on = datetime.now() + timedelta(minutes=self.API_TOKEN_DURATION)
            self._api_token = self.authenticate()
            return self._api_token

        logging.info("Using cached API token...")
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

        logging.info("Logging in to %s...", self._url)
        self.api_key = invoke_endpoint(HttpVerb.GET, ConjurEndpoint.LOGIN,
                                       self._default_params, auth=(login_id, password),
                                       ssl_verify=self._ssl_verify).text
        self.login_id = login_id

        return self.api_key

    def authenticate(self):
        """
        TODO
        """

        if not self._url or not self.login_id or not self.api_key:
            # TODO: Use custom error
            raise RuntimeError("Missing parameters in authentication invocation!")

        params={'login': quote(self.login_id)}
        params.update(self._default_params)

        logging.info("Authenticating to %s...", self._url)
        return invoke_endpoint(HttpVerb.POST, ConjurEndpoint.AUTHENTICATE, params,
                               self.api_key, ssl_verify=self._ssl_verify).text

    def set_variable(self, variable_id, value):
        params = {
            'kind': self.KIND_VARIABLE,
            'identifier': quote(variable_id)
        }
        params.update(self._default_params)

        return invoke_endpoint(HttpVerb.POST, ConjurEndpoint.SECRETS, params,
                               value, api_token=self.api_token,
                               ssl_verify=self._ssl_verify).text

    def get_variable(self, variable_id):
        params = {
            'kind': self.KIND_VARIABLE,
            'identifier': quote(variable_id)
        }
        params.update(self._default_params)

        return invoke_endpoint(HttpVerb.GET, ConjurEndpoint.SECRETS, params,
                               api_token=self.api_token, ssl_verify=self._ssl_verify).content
