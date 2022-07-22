# -*- coding: utf-8 -*-

"""
CredentialStoreFactory module

This module is a factory for determining which credential store to use
"""
# SDK
from conjur_api.interface import CredentialsProviderInterface

# Internals
from conjur.constants import SUPPORTED_BACKENDS
from conjur.logic.credential_provider.file_credentials_provider import FileCredentialsProvider
from conjur.logic.credential_provider.keystore_credentials_provider \
    import KeystoreCredentialsProvider
from conjur.wrapper import KeystoreWrapper
from conjur.util import util_functions


# pylint: disable=too-few-public-methods
class CredentialStoreFactory:
    """
    CredentialStoreFactory

    This class follows the Factory pattern to determine which credential store to choose
    """

    @classmethod
    def create_credential_store(cls, force_netrc_flag: bool = None) -> CredentialsProviderInterface:
        """
        Factory method for determining which store to use
        """
        keyring_name = KeystoreWrapper.get_keyring_name()
        use_netrc = force_netrc_flag or util_functions.get_netrc_path_from_conjurrc()

        if keyring_name in SUPPORTED_BACKENDS and use_netrc is None:
            if KeystoreWrapper.is_keyring_accessible():
                return KeystoreCredentialsProvider()

        return FileCredentialsProvider(use_netrc=use_netrc)
