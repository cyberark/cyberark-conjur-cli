"""
Client module

This module is used to setup an API client that will be used fo interactions with
the Conjur server
"""

from .api import Api

class ConfigException(Exception):
    """
    ConfigException

    This class is used to wrap a regular exception with a more-descriptive class name
    """
    pass

class Client(object):
    """
    Client

    This class is used to construct a client for API interaction
    """

    _api = None
    _login_id = None
    _api_key = None
    _debug = False

    def __init__(self, url=None, ca_bundle=None, account='default', login_id=None,
            password=None, ssl_verify=True, debug=False):
        print("Initializing configuration...")

        self._debug = debug

        if url is None:
            raise ConfigException("Appliance URL not found!")

        # TODO: This probably should be optional
        print("Verifying the certificate...")
        # TODO: Implement me!

        print("Verifying the URL...")
        # TODO: Implement me!

        self._login_id = login_id

        self._api = Api(url, account=account, ca_bundle=ca_bundle, ssl_verify=ssl_verify, debug=debug)
        self._api_key = self._api.login(login_id, password)

        print("Client initialized")

    def get(self, variable_id):
        return self._api.get_variable(variable_id)

    def set(self, variable_id, value):
        self._api.set_variable(variable_id, value)
