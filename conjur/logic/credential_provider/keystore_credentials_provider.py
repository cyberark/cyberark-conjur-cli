# -*- coding: utf-8 -*-

"""
KeystoreCredentialsProvider module

This module holds the logic for saving user-specific credentials
to the system's keyring when they login
"""

# Builtins
import logging
import traceback

# Internals
from conjur.constants import KEYSTORE_ATTRIBUTES, MACHINE, LOGIN, PASSWORD
from conjur.data_object import CredentialsData
from conjur.errors import OperationNotCompletedException, \
    CredentialRetrievalException, KeyringAdapterDeletionError
from conjur.interface.credentials_store_interface import CredentialsStoreInterface
from conjur.wrapper import KeystoreAdapter


# pylint: disable=logging-fstring-interpolation
class KeystoreCredentialsProvider(CredentialsStoreInterface):
    """
    KeystoreCredentialsProvider

    This class holds logic for performing CRUD operations on credentials are kept
    in the system's keystore
    """

    def __init__(self):  # pragma: no cover
        pass

    # pylint: disable=line-too-long,logging-fstring-interpolation
    def save(self, credential_data: CredentialsData):
        """
        Method for saving user credentials in the system's keyring
        """
        logging.debug("Attempting to save credentials to the system's credential store "
                      f"'{KeystoreAdapter.get_keyring_name()}'...")
        credential_id = credential_data.machine
        try:
            KeystoreAdapter.set_password(credential_id, MACHINE, credential_data.machine)
            KeystoreAdapter.set_password(credential_id, LOGIN, credential_data.login)
            KeystoreAdapter.set_password(credential_id, PASSWORD, credential_data.password)
            logging.debug(f"Credentials saved to the '{KeystoreAdapter.get_keyring_name()}' credential store")
        except Exception as incomplete_operation:
            raise OperationNotCompletedException(incomplete_operation) from incomplete_operation

    def load(self, conjurrc_conjur_url) -> CredentialsData:
        """
        Method for fetching user credentials from the system's keyring
        """
        loaded_credentials = {}
        if not self.is_exists(conjurrc_conjur_url):
            raise CredentialRetrievalException

        for attr in KEYSTORE_ATTRIBUTES:
            loaded_credentials[attr] = KeystoreAdapter.get_password(conjurrc_conjur_url, attr)
        return CredentialsData.convert_dict_to_obj(loaded_credentials)

    def is_exists(self, conjurrc_conjur_url) -> bool:
        for attr in KEYSTORE_ATTRIBUTES:
            if KeystoreAdapter.get_password(conjurrc_conjur_url, attr) is None:
                return False
        return True

    def update_api_key_entry(self, user_to_update, credential_data, new_api_key):
        """
        Method for updating user credentials in the system's keyring
        """
        try:
            KeystoreAdapter.set_password(credential_data.machine, MACHINE, credential_data.machine)
            KeystoreAdapter.set_password(credential_data.machine, LOGIN, user_to_update)
            KeystoreAdapter.set_password(credential_data.machine, PASSWORD, new_api_key)
        except Exception as incomplete_operation:
            raise OperationNotCompletedException(incomplete_operation) from incomplete_operation

    # pylint: disable=logging-fstring-interpolation,line-too-long
    def remove_credentials(self, conjurrc):
        """
        Method for removing user credentials in the system's keyring
        """
        logging.debug("Attempting to remove credentials from "
                      f"the '{KeystoreAdapter.get_keyring_name()}' credential store...")
        for attr in KEYSTORE_ATTRIBUTES:
            try:
                KeystoreAdapter.delete_password(conjurrc.conjur_url, attr)
            # Catches when credentials do not exist in the keyring. If the key does not exist,
            # the user has already logged out. we still try to remove other leftovers
            except KeyringAdapterDeletionError:
                logging.debug(
                    f"Unable to delete key '{attr}' from the '{KeystoreAdapter.get_keyring_name()}' "
                    f"credential store. Key may not exist.\n{traceback.format_exc()}")

        logging.debug("Successfully removed credentials from the "
                      f"'{KeystoreAdapter.get_keyring_name()}' credential store")

    def cleanup_if_exists(self, conjurrc_conjur_url):
        """
        For each credential attribute, check if exists for
        the conjurrc_conjur_url identifier and delete if exists
        """
        for attr in KEYSTORE_ATTRIBUTES:
            try:
                if KeystoreAdapter.get_password(conjurrc_conjur_url, attr) is not None:
                    KeystoreAdapter.delete_password(conjurrc_conjur_url, attr)
            # Catches when credentials do not exist in the keyring. If the key does not exist,
            # the user has already logged out. we still try to remove other leftovers
            except Exception:  # pylint: disable=broad-except
                logging.debug(
                    f"Cleanup failed for key '{attr}' from the '{KeystoreAdapter.get_keyring_name()}' "
                    f"credential store.\n{traceback.format_exc()}")
