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
    def create_credential_store(cls) -> CredentialsProviderInterface:
        """
        Factory method for determining which store to use
        """
        keyring_name = KeystoreWrapper.get_keyring_name()
        file_keystore = util_functions.get_file_keystore_from_conjurrc()

        if keyring_name in SUPPORTED_BACKENDS and file_keystore is None:
            # If the keyring is unlocked then we will use it
            if KeystoreWrapper.is_keyring_accessible():
                return KeystoreCredentialsProvider()

        return FileCredentialsProvider()
