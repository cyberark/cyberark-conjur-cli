import logging

from datetime import datetime, timedelta

from .endpoints import ConjurEndpoint
from .http import HttpVerb, invoke_endpoint


class Api(object):
    # Tokens should only be reused for 5 minutes (max lifetime is 8 minutes)
    API_TOKEN_DURATION = 5

    KIND_VARIABLE = 'variable'

    _api_token = None

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
        if not self._account or len(self._account) == 0:
            raise RuntimeError("Account cannot be empty!")

        self._ssl_verify = ssl_verify
        if ca_bundle:
            self._ssl_verify = ca_bundle

        self.api_key = api_key
        self.login_id = login_id

        self.api_token_expiration = None

        self._default_params = {
            'url': url,
            'account': account
        }

        if not ssl_verify:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # WARNING: ONLY FOR DEBUGGING - DO NOT CHECK IN LINE BELOW UNCOMMENTED
        # if http_debug: enable_http_logging()

        # Sanity checks
        if not self._url:
            raise Exception("ERROR: API instantiation parameter 'url' cannot be empty!")

    @property
    def api_token(self):
        if not self._api_token or datetime.now() > self.api_token_expiration:
            logging.info("API token missing or expired. Fetching new one...")
            self.api_token_expiration = datetime.now() + timedelta(minutes=self.API_TOKEN_DURATION)
            self._api_token = self.authenticate()
            return self._api_token

        logging.info("Using cached API token...")
        return self._api_token

    def login(self, login_id=None, password=None):
        """
        This method uses the basic auth login id (username) and password
        to retrieve an api key from the server that can be later used to
        retrieve short-lived api tokens.
        """

        if not login_id or not password:
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
        Authenticate uses the api_key to fetch a short-lived api token that
        for a limited time will allow you to interact fully with the Conjur
        vault.
        """

        if not self.login_id or not self.api_key:
            # TODO: Use custom error
            raise RuntimeError("Missing parameters in authentication invocation!")

        params={'login': self.login_id}
        params.update(self._default_params)

        logging.info("Authenticating to %s...", self._url)
        return invoke_endpoint(HttpVerb.POST, ConjurEndpoint.AUTHENTICATE, params,
                               self.api_key, ssl_verify=self._ssl_verify).text

    def get_variable(self, variable_id):
        """
        This method is used to fetch a secret's (aka "variable") value from
        Conjur vault.
        """

        params = {
            'kind': self.KIND_VARIABLE,
            'identifier': variable_id,
        }
        params.update(self._default_params)

        return invoke_endpoint(HttpVerb.GET, ConjurEndpoint.SECRETS, params,
                               api_token=self.api_token, ssl_verify=self._ssl_verify).content

    def set_variable(self, variable_id, value):
        """
        This method is used to set a secret (aka "variable") to a value of
        your choosing.
        """

        params = {
            'kind': self.KIND_VARIABLE,
            'identifier': variable_id,
        }
        params.update(self._default_params)

        return invoke_endpoint(HttpVerb.POST, ConjurEndpoint.SECRETS, params,
                               value, api_token=self.api_token,
                               ssl_verify=self._ssl_verify).text
