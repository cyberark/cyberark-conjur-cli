# -*- coding: utf-8 -*-

"""
CredentialsFromKeystore module

This module holds the logic for saving user-specific credentials
to the system's keyring when they login
"""

# Builtins
import logging

# Third party
import keyring

STORE_ATTRIBUTES = ["machine", "login_id", "api_key"]

# pylint: disable=logging-fstring-interpolation
class CredentialsFromKeystore:
    """
    CredentialsFromKeystore

    This class holds logic when credentials are kept in the system's keystore
    """

    def __init__(self):
        pass

    @classmethod
    def save(cls, credential_data):
        """
        Method for saving user credentials in the system's keyring
        """
        logging.debug("Attempting to save credentials to the system's keyring "
                      f"'{keyring.get_keyring().name}'")
        keyring.set_password(credential_data.machine, "machine", credential_data.machine)
        keyring.set_password(credential_data.machine, "login_id", credential_data.login)
        keyring.set_password(credential_data.machine, "api_key", credential_data.api_key)
        logging.debug(f"Credentials saved to keyring '{keyring.get_keyring().name}'")

    @classmethod
    def load(cls, conjurrc_conjur_url):
        """
        Method for fetching user credentials from the system's keyring
        """
        loaded_credentials = {}
        for attr in STORE_ATTRIBUTES:
            loaded_credentials[attr] = keyring.get_password(conjurrc_conjur_url, attr)

        return loaded_credentials

    @classmethod
    def update_api_key_entry(cls, user_to_update, credential_data, new_api_key):
        """
        Method for updating user credentials in the system's keyring
        """
        keyring.set_password(credential_data['machine'], "machine", credential_data['machine'])
        keyring.set_password(credential_data['machine'], "login_id", user_to_update)
        keyring.set_password(credential_data['machine'], "api_key", new_api_key)

    @classmethod
    # pylint: disable=logging-fstring-interpolation,line-too-long
    def remove_credentials(cls, conjurrc):
        """
        Method for removing user credentials in the system's keyring
        """
        logging.debug(f"Attempting to remove credentials from the keyring '{keyring.get_keyring().name}'")
        for attr in STORE_ATTRIBUTES:
            keyring.delete_password(conjurrc.conjur_url, attr)
        logging.debug(f"Successfully removed credentials from the keyring '{keyring.get_keyring().name}'")
