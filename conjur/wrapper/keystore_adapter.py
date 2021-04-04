# -*- coding: utf-8 -*-

"""
KeystoreAdapter module

This module is a wrapper for the third-party keyring module used to get and set
credentials in a system's keyring. This module allows us to easily swap out both
library and functionality should we need to do so in the future.
"""

# Builtins
import logging

# Third party
import keyring

# Internals
from conjur.constants import KEYSTORE_ATTRIBUTES

# TODO should verify we are using the exact keyring version wanted and
#  disable insecure keyring such as PlaintextKeyring.
class KeystoreAdapter:
    """
    KeystoreAdapter

    A class for wrapping used functionality from the keyring library
    """

    @classmethod
    def set_password(cls, identifier, key, val):
        """
        Method for setting a password in keyring
        """
        keyring.set_password(identifier, key, val)

    @classmethod
    def get_password(cls, identifier, key):
        """
        Method for getting a password in keyring
        """
        return keyring.get_password(identifier, key)

    # TODO add simple delete for one attribute only here in the adapter
    # TODO do not raise keyring module errors
    # pylint: disable=try-except-raise
    @classmethod
    def delete_password(cls, identifier):
        """
        Method for deleting a password in keyring
        """
        try:
            for attr in KEYSTORE_ATTRIBUTES:
                keyring.delete_password(identifier, attr)
        # Catches when credentials do not exist in the keyring. If the key does not exist,
        # the user has already logged out
        except keyring.errors.PasswordDeleteError:
            return
        except keyring.errors.KeyringError:
            raise

    @classmethod
    def get_keyring_name(cls):
        """
        Method to get the system's keyring name
        """
        return keyring.get_keyring().name

    @classmethod
    def is_keyring_accessible(cls):
        """
        Method to check if the keyring is accessible
        """
        try:
            # The following sends a dummy request to test if the system's keyring is
            # accessible. 'get_password' returns None if the password does not exist.
            # If get_password raises an error, then we can infer that the keyring has
            # not be configured correctly and not available for use. Therefore, false
            # will be returned
            keyring.get_password('test-system', 'test-accessibility')
        except keyring.errors.KeyringError:
            return False

        return True

    @classmethod
    def configure_keyring_log_to_info(cls):
        """
        Method to configure the keyring logs to info
        """
        logging.getLogger('keyring').setLevel(logging.INFO)
