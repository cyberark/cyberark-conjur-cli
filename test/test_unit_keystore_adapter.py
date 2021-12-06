# Builtin
import unittest
from unittest.mock import patch
import logging

# Third-Party
import keyring

# Internal
from conjur.constants import TEST_HOSTNAME
from conjur.errors import KeyringWrapperGeneralError, KeyringWrapperDeletionError
from conjur.util import util_functions
from conjur.wrapper import KeystoreWrapper


class KeystoreWrapperTest(unittest.TestCase):
    @patch.object(keyring, "delete_password")
    def test_delete_password_calls_keyring_delete_password(self, mock_keyring):
        KeystoreWrapper.delete_password(TEST_HOSTNAME, "key")
        mock_keyring.assert_called_once_with(TEST_HOSTNAME, "key")

    @patch.object(keyring, "delete_password", side_effect=keyring.errors.KeyringError)
    def test_delete_password_raises_keyring_error(self, mock_delete_password):
        with self.assertRaises(KeyringWrapperGeneralError):
            KeystoreWrapper.delete_password(TEST_HOSTNAME, "some_key")

    @patch.object(keyring, "delete_password", side_effect=keyring.errors.PasswordDeleteError)
    def test_delete_password_raises_expected_exceptions(self, mock_delete_password):
        with self.assertRaises(KeyringWrapperDeletionError):
            KeystoreWrapper.delete_password(TEST_HOSTNAME, "some_key")

    @patch.object(keyring, "get_password", return_value=None)
    def test_is_keyring_accessible_return_true_when_get_password(self, mock_keyring):
        keyring_accessible = KeystoreWrapper.is_keyring_accessible()
        mock_keyring.assert_called_once_with('test-system', 'test-accessibility')
        self.assertEquals(True, keyring_accessible)

    @patch.object(keyring, "get_password", side_effect=keyring.errors.KeyringError)
    def test_is_keyring_accessible_returns_false_on_keyring_error(self, mock_keyring):
        self.assertEquals(False, KeystoreWrapper.is_keyring_accessible())

    def test_get_keyring_name_use_proper_log_level(self):
        logging.getLogger('keyring').setLevel(logging.DEBUG)
        KeystoreWrapper.get_keyring_name()
        self.assertEquals(logging.getLogger('keyring').level, logging.INFO)

    @patch.object(keyring, "get_password", return_value=None)
    def test_get_password_use_proper_log_level(self, mock):
        logging.getLogger('keyring').setLevel(logging.DEBUG)
        KeystoreWrapper.get_password("", "")
        self.assertEquals(logging.getLogger('keyring').level, logging.INFO)

    @patch.object(keyring, "delete_password", return_value=None)
    def test_get_delete_password_use_proper_log_level(self, mock):
        logging.getLogger('keyring').setLevel(logging.DEBUG)
        KeystoreWrapper.delete_password("", "")
        self.assertEquals(logging.getLogger('keyring').level, logging.INFO)

    @patch.object(keyring, "set_password", return_value=None)
    def test_get_set_password_use_proper_log_level(self, mock):
        logging.getLogger('keyring').setLevel(logging.DEBUG)
        KeystoreWrapper.set_password("", "", "")
        self.assertEquals(logging.getLogger('keyring').level, logging.INFO)
