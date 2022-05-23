# -*- coding: utf-8 -*-

"""
ConjurrcData module

This module represents an object that holds conjurrc data
"""
# pylint: disable=too-few-public-methods
from yaml import load as yaml_load
from yaml import dump as yaml_dump

try:
    from yaml import CLoader as YamlLoader
except ImportError:  # pragma: no cover
    from yaml import Loader as YamlLoader

from conjur_api.models import ConjurConnectionInfo

# Internals
from conjur.data_object.authn_types import AuthnTypes
from conjur.constants import DEFAULT_CONFIG_FILE
from conjur.errors import InvalidConfigurationException, ConfigurationMissingException


class ConjurrcData:
    """
    Used for setting user input data
    """

    def __init__(self, conjur_url: str = None, account: str = None, cert_file: str = None, authn_type: str = None):
        self.conjur_url = conjur_url
        self.conjur_account = account
        self.cert_file = cert_file
        self.authn_type = ConjurrcData._parse_authn_type(authn_type)

    # pylint: disable=unspecified-encoding
    @classmethod
    def load_from_file(cls, conjurrc_path: str = DEFAULT_CONFIG_FILE):
        """
        Method that loads the conjurrc into an object
        """
        try:
            with open(conjurrc_path, 'r') as conjurrc:
                loaded_conjurrc = yaml_load(conjurrc, Loader=YamlLoader)
                return ConjurrcData(loaded_conjurrc['conjur_url'],
                                    loaded_conjurrc['conjur_account'],
                                    loaded_conjurrc['cert_file'],
                                    loaded_conjurrc.get('authn_type'))
        except KeyError as key_error:
            raise InvalidConfigurationException from key_error
        except FileNotFoundError as not_found_err:
            raise ConfigurationMissingException from not_found_err

    def write_to_file(self, dest: str):
        """
        Method for writing the conjurrc configuration
        details needed to create a connection to Conjur
        """
        with open(dest, 'w') as config_fp:
            data = {key: str(val) for key, val in self.__dict__.items() if val is not None}
            out = f"---\n{yaml_dump(data)}"
            config_fp.write(out)

    def __repr__(self) -> str:
        return f"{self.__dict__}"

    def get_client_connection_info(self) -> ConjurConnectionInfo:
        """
        Method return the SDK ConjurConnectionInfo with the ConjurrcData params
        """
        return ConjurConnectionInfo(conjur_url=self.conjur_url,
                                    account=self.conjur_account,
                                    cert_file=self.cert_file)

    @staticmethod
    def _parse_authn_type(authn_type: str | AuthnTypes) -> AuthnTypes:
        """
        Method parses the authn_type string to the AuthnTypes enum
        """

        if isinstance(authn_type, AuthnTypes):
            return authn_type

        if authn_type == 'authn' or authn_type is None:
            return AuthnTypes.AUTHN

        # Future:
        # elif authn_type_str == 'ldap':
        #     return AuthnTypes.LDAP

        raise InvalidConfigurationException(f"Invalid authn_type: {authn_type}")
