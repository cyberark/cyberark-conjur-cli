# Builtin
import unittest
from unittest.mock import patch, call
# Third-Party
import keyring
# Internal
from conjur.constants import TEST_HOSTNAME, PASSWORD, LOGIN, MACHINE
from conjur.wrapper import KeystoreAdapter


class KeystoreAdapterTest(unittest.TestCase):
    @patch.object(keyring, "delete_password")
    def test_delete_password_calls_keyring_delete_password(self, mock_keyring):
        KeystoreAdapter.delete_password(TEST_HOSTNAME)
        calls = [
            call(TEST_HOSTNAME, MACHINE),
            call(TEST_HOSTNAME, LOGIN),
            call(TEST_HOSTNAME, PASSWORD),
        ]
        mock_keyring.assert_has_calls(calls)

    @patch.object(keyring, "delete_password", side_effect=keyring.errors.KeyringError)
    def test_delete_password_raises_keyring_error(self, mock_keyring):
        with self.assertRaises(keyring.errors.KeyringError):
            KeystoreAdapter.delete_password(TEST_HOSTNAME)

    @patch.object(keyring, "delete_password", side_effect=keyring.errors.PasswordDeleteError)
    def test_delete_password_returns_none_on_password_delete_error(self, mock_keyring):
        self.assertEquals(None, KeystoreAdapter.delete_password(TEST_HOSTNAME))

    @patch.object(keyring, "get_password", return_value=None)
    def test_is_keyring_accessible_return_true_when_get_password(self, mock_keyring):
        keyring_accessible = KeystoreAdapter.is_keyring_accessible()
        mock_keyring.assert_called_once_with('test-system', 'test-accessibility')
        self.assertEquals(True, keyring_accessible)

    @patch.object(keyring, "get_password", side_effect=keyring.errors.KeyringError)
    def test_is_keyring_accessible_returns_false_on_keyring_error(self, mock_keyring):
        self.assertEquals(False, KeystoreAdapter.is_keyring_accessible())
