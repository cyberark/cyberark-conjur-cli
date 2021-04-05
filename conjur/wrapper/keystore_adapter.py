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
from conjur.errors import KeyringAdapterDeletionError, KeyringAdapterGeneralError, KeyringAdapterSetError
from conjur.util.util_functions import setup_keyring_env_variable

setup_keyring_env_variable()

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
        try:
            keyring.set_password(identifier, key, val)
        except keyring.errors.PasswordSetError as password_error:
            raise KeyringAdapterSetError(f"unable to set key: {key} for identifier: "
                                  f"{identifier}") from password_error
        except keyring.errors.KeyringError as keyring_error:
            raise KeyringAdapterGeneralError(f"unable to set key: {key} for identifier: "
                                      f"{identifier}") from keyring_error

    @classmethod
    def get_password(cls, identifier, key):
        """
        Method for getting a password in keyring
        """
        try:
            return keyring.get_password(identifier, key)
        except keyring.errors.KeyringError as keyring_error:
            raise KeyringAdapterGeneralError(f"unable to get value for key: {key} "
                                      f"for identifier: {identifier}") from keyring_error

    # pylint: disable=try-except-raise
    @classmethod
    def delete_password(cls, identifier, key):
        """
        Method for deleting a password in keyring
        """
        try:
            keyring.delete_password(identifier, key)
        except keyring.errors.PasswordDeleteError as password_error:
            raise KeyringAdapterDeletionError(f"Failed to delete key '{key}' for identifier "
                                       f"'{identifier}'") from password_error
        except keyring.errors.KeyringError as keyring_error:
            raise KeyringAdapterGeneralError(f"Failed to delete key '{key}' for identifier "
                                      f"'{identifier}'") from keyring_error

    @classmethod
    def get_keyring_name(cls):
        """
        Method to get the system's keyring name
        """
        # keyring.get_keyring() can throw various types of exceptions
        # some are OS exceptions that is the reason we catch general exception.
        # please note that this is a critical path, if we get error here the
        # entire app could not function
        try:
            return keyring.get_keyring().name
        except Exception as err:  # pylint: disable=broad-except
            logging.debug(err)
            return None

    @classmethod
    def is_keyring_accessible(cls):
        """
        Method to check if the keyring is accessible
        """
        try:
            # Send a dummy request to test if the keyring is accessible
            # this should return None if value not exist
            # catch Exception and not specific type since it can throw various
            # types of exceptions (some are OS exceptions) and if get_password
            # doesn't throws it means that kearying is accessible otherwise it isn't
            keyring.get_password('test-system', 'test-accessibility')
        except Exception as err:  # pylint: disable=broad-except
            logging.debug(err)
            return False

        return True
