# -*- coding: utf-8 -*-

"""
Client module

This module is used to setup an API client that will be used fo interactions with
the Conjur server
"""

import logging

from .api import Api
from .config import Config as ApiConfig
from .util import get_api_methods


class ConfigException(Exception):
    """
    ConfigException

    This class is used to wrap a regular exception with a more-descriptive class name
    """


#pylint: disable=too-few-public-methods
class Client():
    """
    Client

    This class is used to construct a client for API interaction. Most of the
    methods get tacked on to the instances during runtime so it's a relatively
    thin wrapper.
    """

    _api = None
    _login_id = None
    _api_key = None

    LOGGING_FORMAT = '%(asctime)s %(levelname)s: %(message)s'


    # The method signature is long but we want to explicitly control
    # what paramteres are allowed
    #pylint: disable=too-many-arguments,too-many-locals
    def __init__(self,
                 account='default',
                 api_class=Api,
                 api_config_class=ApiConfig,
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

        if not url or not account or not login_id or not password:
            logging.info("Not all expected variables were provided. " \
                "Using conjurrc as credential store...")
            try:
                on_disk_config = dict(api_config_class())

                # We want to retain any overrides that the user provided from params
                on_disk_config.update(config)
                config = on_disk_config

            except Exception as exc:
                raise ConfigException(exc)

        self._api = api_class(ssl_verify=ssl_verify, http_debug=http_debug, **config)

        # Pass-through for all the API client-facing methods. Dynamically populated
        # based on the decorators on methods:
        # - get(self, variable_id)
        # - set(self, variable_id, value)
        # - apply_policy_file(self, policy_name, policy_file)
        for method_name, method_info in get_api_methods(Api).items():
            setattr(self, method_name, getattr(self._api, method_info['matching_method_name']))

        if password:
            logging.info("Creating API key with password...")
            self._api_key = self._api.login(login_id, password)
        else:
            logging.info("Using API key with netrc credentials...")

        logging.info("Client initialized")

    def _setup_logging(self, debug):
        if debug:
            logging.basicConfig(level=logging.DEBUG, format=self.LOGGING_FORMAT)
        else:
            logging.basicConfig(level=logging.WARNING, format=self.LOGGING_FORMAT)
