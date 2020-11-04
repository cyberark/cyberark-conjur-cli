# -*- coding: utf-8 -*-

"""
Client module

This module is used to setup an API client that will be used fo interactions with
the Conjur server
"""

import logging

from .api import Api
from .config import Config as ApiConfig


class ConfigException(Exception):
    """
    ConfigException

    This class is used to wrap a regular exception with a more-descriptive class name
    """


class Client():
    """
    Client

    This class is used to construct a client for API interaction
    """

    _api = None
    _login_id = None
    _api_key = None

    LOGGING_FORMAT = '%(asctime)s %(levelname)s: %(message)s'


    # The method signature is long but we want to explicitly control
    # what paramteres are allowed
    #pylint: disable=too-many-arguments,too-many-locals
    def __init__(self,
                 account=None,
                 api_key=None,
                 ca_bundle=None,
                 debug=False,
                 http_debug=False,
                 login_id=None,
                 password=None,
                 ssl_verify=True,
                 url=None):

        self._setup_logging(debug)

        logging.info("Initializing configuration...")

        self._login_id = login_id

        config = {
            'url': url,
            'account': account,
            'ca_bundle': ca_bundle,
        }

        if not url or not login_id or (not password and not api_key):
            logging.info("Not all expected variables were provided. " \
                "Using conjurrc as credential store...")
            try:
                on_disk_config = dict(ApiConfig())

                # We want to retain any overrides that the user provided from params
                # but only if those values are valid
                for field_name, field_value in config.items():
                    if field_value:
                        on_disk_config[field_name] = field_value
                config = on_disk_config

            except Exception as exc:
                raise ConfigException(exc) from Exception

        # We only want to override missing account info with "default"
        # if we can't find it anywhere else.
        if config['account'] is None:
            config['account'] = "default"

        if api_key:
            logging.info("Using API key from parameters...")
            self._api = Api(api_key=api_key,
                            http_debug=http_debug,
                            login_id=login_id,
                            ssl_verify=ssl_verify,
                            **config)
        elif password:
            logging.info("Creating API key with login ID/password combo...")
            self._api = Api(http_debug=http_debug,
                            ssl_verify=ssl_verify,
                            **config)
            self._api.login(login_id, password)
        else:
            logging.info("Using API key with netrc credentials...")
            self._api = Api(http_debug=http_debug,
                            ssl_verify=ssl_verify,
                            **config)

        logging.info("Client initialized")

    def _setup_logging(self, debug):
        if debug:
            logging.basicConfig(level=logging.DEBUG, format=self.LOGGING_FORMAT)
        else:
            logging.basicConfig(level=logging.WARNING, format=self.LOGGING_FORMAT)

    ### API passthrough

    def whoami(self):
        """
        Provides dictionary of information about the user making an API request
        """
        return self._api.whoami()

    def list(self):
        """
        Lists all available resources
        """
        return self._api.list_resources()

    def get(self, variable_id):
        """
        Gets a variable value based on its ID
        """
        return self._api.get_variable(variable_id)

    def get_many(self, *variable_ids):
        """
        Gets multiple variable values based on their IDs. Returns a
        dictionary of mapped values.
        """
        return self._api.get_variables(*variable_ids)

    def set(self, variable_id, value):
        """
        Sets a variable to a specific value based on its ID
        """
        self._api.set_variable(variable_id, value)

    def apply_policy_file(self, policy_name, policy_file):
        """
        Applies a file-based policy to the Conjur instance
        """
        return self._api.apply_policy_file(policy_name, policy_file)

    def replace_policy_file(self, policy_name, policy_file):
        """
        Replaces a file-based policy defined in the Conjur instance
        """
        return self._api.replace_policy_file(policy_name, policy_file)

    def delete_policy_file(self, policy_name, policy_file):
        """
        Replaces a file-based policy defined in the Conjur instance
        """
        return self._api.delete_policy_file(policy_name, policy_file)
