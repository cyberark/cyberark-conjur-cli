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
from conjur.errors import KeyringAdapterDeletionError, KeyringAdapterGeneralError\
    , KeyringAdapterSetError
from conjur.util.util_functions import configure_env_var_with_keyring

# Function is called in the module so that before accessing the
# system’s keyring, the environment will be configured correctly
configure_env_var_with_keyring()


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
            raise KeyringAdapterSetError(f"Failed to set key '{key}' for identifier "
                                         f"'{identifier}'") from password_error
        except Exception as exception:
            raise KeyringAdapterGeneralError(message=f"General keyring error has occurred "
                                                     f"(Failed to set '{key}')'") from exception

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
        except Exception as exception:
            raise KeyringAdapterGeneralError(message=f"General keyring error has occurred "
                                                     f"(Failed to delete '{key}')'") from exception

    @classmethod
    def get_keyring_name(cls):
        """
        Method to get the system's keyring name
        """
        # keyring.get_keyring can throw various types of Exceptions.
        # Some are OS exceptions and that is the reason we catch general Exceptions.
        # Note that this is a critical path, if we get error, we will return None and not raise
        # the exception because we want to write to the netrc and not fail the CLI
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
            # this should return None if value not exist.
            keyring.get_password('test-system', 'test-accessibility')
        # Catch Exception and not a specific type since various exceptions
        # can be thrown. For example some related to OS and others related to keyring.
        except Exception as err:  # pylint: disable=broad-except
            logging.debug(err)
            return False

        return True
