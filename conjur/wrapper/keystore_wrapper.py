# -*- coding: utf-8 -*-

"""
KeystoreWrapper module

This module is a wrapper for the third-party keyring module used to get and set
credentials in a system's keyring. This module allows us to easily swap out both
library and functionality should we need to do so in the future.
"""

# Builtins
import logging
from typing import Optional

# Third party
import keyring

# Internals
from conjur.errors import KeyringWrapperDeletionError, KeyringWrapperGeneralError \
    , KeyringWrapperSetError
from conjur.util.util_functions import configure_env_var_with_keyring

# Function is called in the module so that before accessing the
# system’s keyring, the environment will be configured correctly
configure_env_var_with_keyring()


def validate_log_level(func):
    """
    Method decorator that make sure no sensitive log is written
    """

    def inner(*args, **kwargs):
        if logging.getLogger("keyring").level <= logging.INFO:
            logging.getLogger("keyring").setLevel(logging.INFO)
        return func(*args, **kwargs)

    return inner


class KeystoreWrapper:
    """
    KeystoreWrapper

    A class for wrapping used functionality from the keyring library
    """

    @staticmethod
    @validate_log_level
    def set_password(identifier: str, key: str, val: str):
        """
        Method for setting a password in keyring
        """
        try:
            keyring.set_password(identifier, key, val)
        except keyring.errors.PasswordSetError as password_error:
            raise KeyringWrapperSetError(f"Failed to set key '{key}' for identifier "
                                         f"'{identifier}'") from password_error
        except Exception as exception:
            raise KeyringWrapperGeneralError(message=f"General keyring error has occurred "
                                                     f"(Failed to set '{key}')'") from exception

    # pylint: disable=try-except-raise
    @staticmethod
    @validate_log_level
    def get_password(identifier: str, key: str):
        """
        Method for getting a password in keyring
        """
        try:
            return keyring.get_password(identifier, key)
        except Exception as exception:
            raise KeyringWrapperGeneralError(message=f"General keyring error has occurred "
                                                     f"(Failed to get '{key}')'") from exception

    # pylint: disable=try-except-raise
    @staticmethod
    @validate_log_level
    def delete_password(identifier: str, key: str):
        """
        Method for deleting a password in keyring
        """
        try:
            keyring.delete_password(identifier, key)
        except keyring.errors.PasswordDeleteError as password_error:
            raise KeyringWrapperDeletionError(f"Failed to delete key '{key}' for identifier "
                                              f"'{identifier}'") from password_error
        except Exception as exception:
            raise KeyringWrapperGeneralError(message=f"General keyring error has occurred "
                                                     f"(Failed to delete '{key}')'") from exception

    @staticmethod
    @validate_log_level
    def get_keyring_name() -> Optional[str]:
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

    @staticmethod
    @validate_log_level
    def is_keyring_accessible() -> bool:
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
            # Catch Exception and not a specific type since various exceptions
            # can be thrown. For example some related to OS and others related to keyring.
        except Exception as err:  # pylint: disable=broad-except
            logging.debug(err)
            return False

        return True
