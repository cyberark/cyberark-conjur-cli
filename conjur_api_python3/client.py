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

    def __init__(self, url=None, server_cert=None, account='default', login_id=None,
            password=None, ssl_verify=True):
        print("Initializing configuration...")

        if url is None:
            raise ConfigException("Appliance URL not found!")

        if server_cert is None:
            raise ConfigException("Server certificate not found!")

        # TODO: This probably should be optional
        print("Verifying the certificate...")
        # TODO: Implement me!

        print("Verifying the URL...")
        # TODO: Implement me!

        self._api = Api(url, server_cert, account, ssl_verify=ssl_verify)

        self._login_id = login_id
        self._api_key = self._api.login(login_id, password)

        print("Client initialized")

    def get(self, variable_id):
        return self._api.get_variable(variable_id, self._login_id, self._api_key)

    def set(self, variable_id, value):
        self._api.set_variable(variable_id, value, self._login_id, self._api_key)
