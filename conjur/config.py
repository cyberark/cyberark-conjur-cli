# -*- coding: utf-8 -*-

"""
Config module

This module provides high-level parsing and setting of configuration
variables needed for the API to be used with minimal effort
"""

import logging

from yaml import load, dump
try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:  # pragma: no cover
    from yaml import Loader, Dumper

# Internals
from conjur.constants import DEFAULT_CONFIG_FILE, DEFAULT_CERTIFICATE_BUNDLE_FILE


class Config():
    """
    Used for handling setting and parsing of various configuration
    settings required for the API to connect to the Conjur instance.
    """

    # We intentionally remap some fields to friendlier names
    # Conjurrc field / Config name / Mandatory
    FIELDS = [
        ('account', 'account', True),
        ('appliance_url', 'url', True),
        ('cert_file', 'ca_bundle', False),
        ('plugins', 'plugins', False),
    ]

    _config = {}

    def __init__(self, config_file=DEFAULT_CONFIG_FILE):
        # pylint: disable=logging-fstring-interpolation
        logging.debug(f"Fetching connection details from filesystem {config_file}")

        config = None
        with open(config_file, 'r') as config_fp:
            config = load(config_fp, Loader=Loader)

        for config_field_name, attribute_name, mandatory in self.FIELDS:
            if mandatory:
                assert config_field_name in config

            if config_field_name == 'cert_file' and config[config_field_name] is not None:
                setattr(self, attribute_name, DEFAULT_CERTIFICATE_BUNDLE_FILE)
            else:
                setattr(self, attribute_name, config[config_field_name])
            self._config[attribute_name] = getattr(self, attribute_name)

    def __repr__(self):
        return dump({'config': self._config}, Dumper=Dumper, indent=4)

    def __iter__(self):
        return iter(self._config.items())
