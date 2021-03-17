# -*- coding: utf-8 -*-

"""
CredentialStoreFactory module

This module is a factory for determining which credential store to use
"""

# Internals
from conjur.constants import SUPPORTED_BACKENDS, DEFAULT_NETRC_FILE
from conjur.logic.credential_provider.file_credentials_provider import FileCredentialsProvider
from conjur.logic.credential_provider.keystore_credentials_provider \
    import KeyStoreCredentialsProvider
from conjur.wrapper import KeystoreAdapter

# pylint: disable=too-few-public-methods
class CredentialStoreFactory:
    """
    CredentialStoreFactory

    This class follows the Factory pattern to determine which credential store to choose
    """
    @classmethod
    def create_credential_store(cls):
        """
        Factory method for determining which store to use
        """
        if KeystoreAdapter.get_keyring_name() in SUPPORTED_BACKENDS:
            # If the keyring is unlocked then we will use that
            if KeystoreAdapter.is_keyring_accessible():
                # pylint: disable=line-too-long
                return KeyStoreCredentialsProvider(), f'keyring {KeystoreAdapter.get_keyring_name()}'
            # If the keystore is not unlocked we will resort to netrc
            return FileCredentialsProvider(), DEFAULT_NETRC_FILE

        return FileCredentialsProvider(), DEFAULT_NETRC_FILE
