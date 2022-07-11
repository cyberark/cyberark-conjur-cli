# -*- coding: utf-8 -*-

"""
Config module

This module provides high-level parsing and setting of configuration
variables needed for the API to be used with minimal effort
"""
# Builtin
import logging
from typing import Union

# Third Party
from yaml import load, dump

try:
    from yaml import CLoader as Loader, CDumper as Dumper
except ImportError:  # pragma: no cover
    from yaml import Loader, Dumper

# Internals
from conjur.constants import DEFAULT_CONFIG_FILE
from conjur.errors import ConfigurationMissingException, InvalidConfigurationException

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
        ('cert_file', 'ca_bundle', True),
        ('authn_type', 'authn_type', False),
    ]

    _config = {}

    # pylint: disable=unspecified-encoding
    def __init__(self, config_file=DEFAULT_CONFIG_FILE):
        # pylint: disable=logging-fstring-interpolation
        logging.debug(f"Fetching connection details from filesystem '{config_file}'...")
        config = None
        with open(config_file, 'r') as config_fp:
            config = load(config_fp, Loader=Loader)

        if not config:
            raise ConfigurationMissingException

        # TODO consider using load_from_file (ConjurrcData) instead of the following logic
        # Sets the value of that FIELDS maps to with the values found in the conjurrc
        for config_field_name, attribute_name, mandatory in self.FIELDS:
            if mandatory and config_field_name not in config:
                raise InvalidConfigurationException
            setattr(self, attribute_name, config.get(config_field_name))
            self._config[attribute_name] = getattr(self, attribute_name)

    def __repr__(self) -> Union[str,bytes]:
        return dump({'config': self._config}, Dumper=Dumper, indent=4)

    def __iter__(self):
        return iter(self._config.items())
