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
from conjur.util.Singleton import Singleton


# pylint: disable=too-few-public-methods
class CredentialStoreFactory(metaclass=Singleton):
    """
    CredentialStoreFactory

    This class follows the Factory pattern to determine which credential store to choose
    """

    def __init__(self):
        self.first_time_log_insecure_store_warning = True

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

        self._log_netrc_warning()
        return FileCredentialsProvider(), DEFAULT_NETRC_FILE

    def _log_netrc_warning(self):
        """
        Method logging the fact we are using insecure CredentialProvider.
        This will be displayed to the user as a warning on every CLI run
        """
        if self.first_time_log_insecure_store_warning:
            logging.warning("No supported keystore found! Saving credentials in "
                            f"plaintext in '{DEFAULT_NETRC_FILE}'. Make sure to logoff "
                            f"after you have finished using the CLI")
        self.first_time_log_insecure_store_warning = False
