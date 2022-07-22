# -*- coding: utf-8 -*-

"""
ConjurrcData module

This module represents an object that holds conjurrc data
"""

from yaml import dump as yaml_dump
from yaml import load as yaml_load

try:
    from yaml import CLoader as YamlLoader
except ImportError:  # pragma: no cover
    from yaml import Loader as YamlLoader

from conjur_api.interface import (AuthenticationStrategyInterface,
                                  CredentialsProviderInterface)
from conjur_api.models import ConjurConnectionInfo
from conjur_api.providers import (AuthnAuthenticationStrategy,
                                  LdapAuthenticationStrategy)

# Internals
from conjur.data_object.authn_types import AuthnTypes
from conjur.constants import DEFAULT_CONFIG_FILE
from conjur.errors import (ConfigurationMissingException,
                           InvalidConfigurationException)

class ConjurrcData:
    """
    Used for setting user input data
    """

    # pylint: disable=too-many-arguments
    def __init__(self, conjur_url: str = None, account: str = None, cert_file: str = None,
                 authn_type: str = None, service_id: str = None, netrc_path: str = None):
        self.conjur_url = conjur_url
        self.conjur_account = account
        self.cert_file = cert_file
        self.authn_type = ConjurrcData._parse_authn_type(authn_type)
        self.service_id = service_id
        self.netrc_path = netrc_path

    # pylint: disable=unspecified-encoding
    @classmethod
    def load_from_file(cls, conjurrc_path: str = DEFAULT_CONFIG_FILE):
        """
        Method that loads the conjurrc into an object
        """
        try:
            with open(conjurrc_path, 'r') as conjurrc:
                loaded_conjurrc = yaml_load(conjurrc, Loader=YamlLoader)
                # For backwards compatibility with CLI 7.0-7.1, we accept the 'conjur_url' and 'conjur_account'
                # keys as well as the 'appliance_url' and 'account' keys. When writing the config file, we write
                # only the 'appliance_url' and 'account' keys which are used in CLI 6.x and 7.2+ as
                # well as summon-conjur.
                return ConjurrcData(loaded_conjurrc.get('appliance_url') or loaded_conjurrc['conjur_url'],
                                    loaded_conjurrc.get('account') or loaded_conjurrc['conjur_account'],
                                    loaded_conjurrc['cert_file'],
                                    loaded_conjurrc.get('authn_type'),
                                    loaded_conjurrc.get('service_id'),
                                    loaded_conjurrc.get('netrc_path'))
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
            data = {
                'appliance_url': self.conjur_url,
                'account': self.conjur_account,
                'cert_file': self.cert_file,
                'authn_type': str(self.authn_type),
                'service_id': self.service_id,
                'netrc_path': self.netrc_path
            }
            out = f"---\n{yaml_dump(data)}"
            config_fp.write(out)

    def __repr__(self) -> str:
        return f"{self.__dict__}"

    def get_client_connection_info(self) -> ConjurConnectionInfo:
        """
        Method returns the SDK ConjurConnectionInfo with the ConjurrcData params
        """
        return ConjurConnectionInfo(conjur_url=self.conjur_url,
                                    account=self.conjur_account,
                                    cert_file=self.cert_file,
                                    service_id=self.service_id)

    def get_authn_strategy(self, credentials_provider: CredentialsProviderInterface) -> AuthenticationStrategyInterface:
        """
        Method returns the AuthnStrategyInterface based on the ConjurrcData params
        """
        if self.authn_type == AuthnTypes.AUTHN or self.authn_type is None:
            return AuthnAuthenticationStrategy(credentials_provider)

        if self.authn_type == AuthnTypes.LDAP:
            return LdapAuthenticationStrategy(credentials_provider)

        raise InvalidConfigurationException(
            f"Invalid authn_type: {self.authn_type.value}. Must be either 'authn' or 'ldap'.")

    @staticmethod
    def _parse_authn_type(authn_type: str | AuthnTypes) -> AuthnTypes:
        """
        Method parses the authn_type string to the AuthnTypes enum
        """

        if isinstance(authn_type, AuthnTypes):
            return authn_type

        if authn_type == 'authn' or authn_type is None:
            return AuthnTypes.AUTHN

        if authn_type == 'ldap':
            return AuthnTypes.LDAP

        raise InvalidConfigurationException(
            f"Invalid authn_type: {authn_type}. Must be either 'authn' or 'ldap'.")
