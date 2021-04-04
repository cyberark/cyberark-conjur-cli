# -*- coding: utf-8 -*-

"""
KeystoreAdapter module

This module is a wrapper for the third-party keyring module used to get and set
credentials in a system's keyring. This module allows us to easily swap out both
library and functionality should we need to do so in the future.
"""

# Builtins
import logging
import platform
import os

# Third party
import keyring

# TODO should verify we are using the exact keyring version wanted and
#  disable insecure keyring such as PlaintextKeyring.
from conjur.errors import KeyringDeletionError, KeyringGeneralError, KeyringSetError

if platform.system() == "Darwin":
    os.environ["PYTHON_KEYRING_BACKEND"] = "keyring.backends.macOS.Keyring"
if platform.system() == "Linux":
    os.environ["PYTHON_KEYRING_BACKEND"] = "keyring.backends.SecretService.Keyring"
if platform.system() == "Windows":
    os.environ["PYTHON_KEYRING_BACKEND"] = "keyring.backends.Windows.WinVaultKeyring"


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
        except keyring.errors.PasswordSetError as err:
            raise KeyringSetError(
                f"unable to set key: {key} for identifier: {identifier}") from err
        except keyring.errors.KeyringError as err:
            raise KeyringGeneralError(
                f"unable to set key: {key} for identifier: {identifier}") from err

    @classmethod
    def get_password(cls, identifier, key):
        """
        Method for getting a password in keyring
        """
        try:
            return keyring.get_password(identifier, key)
        except keyring.errors.KeyringError as err:
            raise KeyringGeneralError(
                f"unable to get value for key: {key} for identifier: {identifier}") from err

    # pylint: disable=try-except-raise
    @classmethod
    def delete_password(cls, identifier, key):
        """
        Method for deleting a password in keyring
        """
        try:
            keyring.delete_password(identifier, key)
        except keyring.errors.PasswordDeleteError as err:
            raise KeyringDeletionError(
                f"unable to delete key: {key} for identifier: {identifier}") from err
        except keyring.errors.KeyringError as err:
            raise KeyringGeneralError(
                f"unable to delete key: {key} for identifier: {identifier}") from err

    @classmethod
    def get_keyring_name(cls):
        """
        Method to get the system's keyring name
        """
        try:
            return keyring.get_keyring().name
        except Exception:  # pylint: disable=broad-except
            return None

    @classmethod
    def is_keyring_accessible(cls):
        """
        Method to check if the keyring is accessible
        """
        # noinspection PyBroadException
        try:
            # Send a dummy request to test if the keyring is accessible
            # this should return None if value not exist
            keyring.get_password('test-system', 'test-accessibility')
        except Exception as keyring_error:  # pylint: disable=broad-except
            logging.debug(keyring_error)
            return False

        return True
