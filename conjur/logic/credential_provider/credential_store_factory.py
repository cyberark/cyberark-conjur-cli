# -*- coding: utf-8 -*-

"""
CredentialStoreFactory module

This module is a factory for determining which credential store to use
"""
# Builtins
import logging

# Internals
from conjur.constants import SUPPORTED_BACKENDS, DEFAULT_NETRC_FILE
from conjur.interface.credentials_store_interface import CredentialsStoreInterface
from conjur.logic.credential_provider.file_credentials_provider import FileCredentialsProvider
from conjur.logic.credential_provider.keystore_credentials_provider \
    import KeystoreCredentialsProvider
from conjur.wrapper import KeystoreAdapter
from conjur.util.singleton import Singleton


# pylint: disable=too-few-public-methods
class CredentialStoreFactory(metaclass=Singleton):
    """
    CredentialStoreFactory

    This class follows the Factory pattern to determine which credential store to choose
    """

    def create_credential_store(self) -> CredentialsStoreInterface:
        """
        Factory method for determining which store to use
        """
        if KeystoreAdapter.get_keyring_name() in SUPPORTED_BACKENDS:
            # TODO investigate other errors that would make a keyring not accessible
            # If the keyring is unlocked then we will use that
            if KeystoreAdapter.is_keyring_accessible():
                # pylint: disable=line-too-long
                return KeystoreCredentialsProvider(), f'{KeystoreAdapter.get_keyring_name()} credential store'

        return FileCredentialsProvider(), DEFAULT_NETRC_FILE
