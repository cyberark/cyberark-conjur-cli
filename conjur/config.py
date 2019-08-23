# -*- coding: utf-8 -*-

"""
Config module

This module provides high-level parsing and setting of configuration
variables needed for the API to be used with minimal effort
"""

import logging
import netrc
import os.path

from yaml import load, dump
try:
    from yaml import CSafeLoader as SafeLoader, CDumper as Dumper
except ImportError:
    from yaml import SafeLoader, Dumper

NETRC_HOST_URL = "{url}/authn"

class Config():
    """
    Used for handling setting and parsing of various configuration
    settings required for the API to connect to the Conjur instance.
    """

    DEFAULT_CONFIG_FILE = os.path.expanduser(os.path.join('~', '.conjurrc'))
    DEFAULT_NETRC_FILE = os.path.expanduser(os.path.join('~', '.netrc'))

    # We intentionally remap some fields to friendlier names
    # Conjurrc field / Config name / Mandatory
    FIELDS = [
        ('account', 'account', True),
        ('appliance_url', 'url', True),
        ('cert_file', 'ca_bundle', False),
        ('plugins', 'plugins', False),
    ]

    _config = {}

    def __init__(self, config_file=DEFAULT_CONFIG_FILE, netrc_file=DEFAULT_NETRC_FILE):
        logging.info("Trying to get configuration from filesystem (%s)...", config_file)

        config = None
        with open(config_file, 'r') as config_fp:
            config = load(config_fp, Loader=SafeLoader)

        for config_field_name, attribute_name, mandatory in self.FIELDS:
            if mandatory:
                assert config_field_name in config

            setattr(self, attribute_name, config[config_field_name])
            self._config[attribute_name] = getattr(self, attribute_name)

        logging.info("Trying to get API key from netrc...")
        netrc_obj = netrc.netrc(netrc_file)
        netrc_host_url = NETRC_HOST_URL.format(**self._config)
        netrc_auth = netrc_obj.authenticators(netrc_host_url)
        if netrc_auth is None:
            raise RuntimeError("Netrc '{}' didn't contain auth info for {}!".format(netrc_file,
                                                                                    netrc_host_url))

        login_id, _, api_key = netrc_auth

        setattr(self, 'api_key', api_key)
        setattr(self, 'login_id', login_id)

        self._config['api_key'] = api_key
        self._config['login_id'] = login_id

    def __repr__(self):
        return dump({'config': self._config}, Dumper=Dumper, indent=4)

    def __iter__(self):
        return iter(self._config.items())
