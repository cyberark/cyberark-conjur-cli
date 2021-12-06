# -*- coding: utf-8 -*-

"""
CredentialStoreFactory module

This module is a factory for determining which credential store to use
"""
# Builtin
from typing import Tuple

# Internals
from conjur.constants import SUPPORTED_BACKENDS, DEFAULT_NETRC_FILE
from conjur.interface.credentials_store_interface import CredentialsStoreInterface
from conjur.logic.credential_provider.file_credentials_provider import FileCredentialsProvider
from conjur.logic.credential_provider.keystore_credentials_provider \
    import KeystoreCredentialsProvider
from conjur.wrapper import KeystoreWrapper


# pylint: disable=too-few-public-methods
class CredentialStoreFactory:
    """
    CredentialStoreFactory

    This class follows the Factory pattern to determine which credential store to choose
    """

    @classmethod
    def create_credential_store(cls) -> Tuple[CredentialsStoreInterface, str]:
        """
        Factory method for determining which store to use
        """
        key_store_wrapper = KeystoreWrapper()
        if key_store_wrapper.get_keyring_name() in SUPPORTED_BACKENDS:
            # If the keyring is unlocked then we will use it
            if key_store_wrapper.is_keyring_accessible():
                # pylint: disable=line-too-long
                return KeystoreCredentialsProvider(), f'{key_store_wrapper.get_keyring_name()} credential store'

        return FileCredentialsProvider(), DEFAULT_NETRC_FILE
