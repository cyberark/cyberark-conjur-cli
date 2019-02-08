import base64
from urllib.parse import quote

import requests
from requests.auth import HTTPBasicAuth

# Debug logging
if False:
    import logging
    from http.client import HTTPConnection

    HTTPConnection.debuglevel = 1

    logging.basicConfig()
    logging.getLogger().setLevel(logging.DEBUG)
    requests_log = logging.getLogger("urllib3")
    requests_log.setLevel(logging.DEBUG)
    requests_log.propagate = True

class Api(object):
    KIND_VARIABLE='variable'

    def __init__(self, url=None, server_cert=None, account='default', ssl_verify=True):
        if not url or not account:
            # TODO: Use custom error
            raise RuntimeError("Missing parameters in Api creation!")

        self._url = url
        self._server_cert = server_cert
        self._account = account
        self._ssl_verify = ssl_verify

        if not ssl_verify:
            import urllib3
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def login(self, login_id=None, password=None):
        """
        TODO
        """

        if not self._url or not login_id or not password:
            # TODO: Use custom error
            raise RuntimeError("Missing parameters in login invocation!")

        url = "{url}/authn/{account}/login".format(url=self._url,
                                                   account=quote(self._account))
        print("Authenticating to {}...".format(url))
        return self._get(url, auth=HTTPBasicAuth(login_id, password)).text

    def authenticate(self, login_id=None, api_key=None):
        """
        TODO
        """

        if not self._url or not login_id or not api_key:
            # TODO: Use custom error
            raise RuntimeError("Missing parameters in authentication invocation!")

        url = "{url}/authn/{account}/{login}/authenticate".format(url=self._url,
                                                                  account=quote(self._account),
                                                                  login=quote(login_id))
        print("Authenticating to {}...".format(url))
        return self._post(url, api_key).text

    def set_variable(self, variable_id, value, login_id, api_key):
        token = self.authenticate(login_id, api_key)
        url = "{url}/secrets/{account}/{kind}/{identifier}".format(url=self._url,
                                                                   account=quote(self._account),
                                                                   kind=self.KIND_VARIABLE,
                                                                   identifier=quote(variable_id))
        return self._post(url, value, api_token=token).text

    def get_variable(self, variable_id, login_id, api_key):
        token = self.authenticate(login_id, api_key)
        url = "{url}/secrets/{account}/{kind}/{identifier}".format(url=self._url,
                                                                   account=quote(self._account),
                                                                   kind=self.KIND_VARIABLE,
                                                                   identifier=quote(variable_id))
        return self._get(url, api_token=token).content

    def _base64encode(self, source_str):
        return base64.b64encode(source_str.encode())

    def _get(self, url, *args, check_errors=True, auth=None, api_token=None):
        headers={}
        if api_token and len(api_token) > 0:
            encoded_token = self._base64encode(api_token).decode('utf-8')
            headers['Authorization'] = 'Token token="{}"'.format(encoded_token)


        response = requests.get(url, *args, verify=self._ssl_verify, auth=auth, headers=headers)
        if check_errors and response.status_code >= 300:
            # TODO: Use custom errors
            raise RuntimeError("Request failed: {}: {}".format(response.status_code,
                                                               response.text))

        return response

    def _post(self, url, *args, check_errors=True, auth=None, api_token=None):
        headers={}
        if api_token and len(api_token) > 0:
            encoded_token = self._base64encode(api_token).decode('utf-8')
            headers['Authorization'] = 'Token token="{}"'.format(encoded_token)

        response = requests.post(url, *args, verify=self._ssl_verify, auth=auth, headers=headers)
        if check_errors and response.status_code >= 300:
            # TODO: Use custom errors
            raise RuntimeError("Request failed: {}: {}".format(response.status_code,
                                                               response.text))

        return response
