# -*- coding: utf-8 -*-

"""
ConjurrcData module

This module represents an object that holds conjurrc data
"""
# pylint: disable=too-few-public-methods
from yaml import load as yaml_load

try:
    from yaml import CLoader as YamlLoader
except ImportError: # pragma: no cover
    from yaml import Loader as YamlLoader

# Internals
from conjur.constants import DEFAULT_CONFIG_FILE
from conjur.errors import InvalidConfigurationException

class ConjurrcData:
    """
    Used for setting user input data
    """
    def __init__(self, conjur_url=None, account=None, cert_file=None):
        self.conjur_url = conjur_url
        self.conjur_account = account
        self.cert_file = cert_file

    @classmethod
    def load_from_file(cls, conjurrc_path:str=DEFAULT_CONFIG_FILE):
        """
        Method that loads the conjurrc into an object
        """
        try:
            with open(conjurrc_path, 'r') as conjurrc:
                loaded_conjurrc = yaml_load(conjurrc, Loader=YamlLoader)
                return ConjurrcData(loaded_conjurrc['conjur_url'],
                                    loaded_conjurrc['conjur_account'],
                                    loaded_conjurrc['cert_file'])
        except KeyError as key_error:
            raise InvalidConfigurationException from key_error

    # pylint: disable=line-too-long
    def __repr__(self) -> str:
        return f"{{'conjur_url': '{self.conjur_url}', 'conjur_account': '{self.conjur_account}', " \
               f"'cert_file': '{self.cert_file}'}}"
