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

class ConjurrcData:
    """
    Used for setting user input data
    """
    def __init__(self, appliance_url=None, account=None, cert_file=None):
        self.appliance_url = appliance_url
        self.account = account
        self.cert_file = cert_file
        self.plugins = []

    @classmethod
    def load_from_file(cls, conjurrc_path=DEFAULT_CONFIG_FILE):
        """
        Method that loads the conjurrc into an object
        """
        with open(conjurrc_path, 'r') as conjurrc:
            loaded_conjurrc = yaml_load(conjurrc, Loader=YamlLoader)
            return ConjurrcData(loaded_conjurrc['appliance_url'],
                                loaded_conjurrc['account'],
                                loaded_conjurrc['cert_file'])

    # pylint: disable=line-too-long
    def __repr__(self):
        return f"{{'appliance_url': '{self.appliance_url}', 'account': '{self.account}', " \
               f"'cert_file': '{self.cert_file}', 'plugins': {self.plugins}}}"
