# Builtin
import unittest
from unittest.mock import patch, call
# Third-Party
import keyring
# Internal
from conjur.wrapper import KeystoreAdapter

CONJUR_URL = "https://conjur-hostname.com"


class KeystoreAdapterTest(unittest.TestCase):
    @patch.object(keyring, 'delete_password')
    def test_delete_password_calls_keyring_delete_password(self, mock_keyring):
        KeystoreAdapter.delete_password(CONJUR_URL)
        calls = [
            call(CONJUR_URL, "machine"),
            call(CONJUR_URL, "login"),
            call(CONJUR_URL, "password"),
        ]
        mock_keyring.assert_has_calls(calls)

    @patch.object(keyring, 'delete_password', side_effect=keyring.errors.KeyringError)
    def test_delete_password_raises_keyring_error(self, mock_keyring):
        with self.assertRaises(keyring.errors.KeyringError):
            KeystoreAdapter.delete_password(CONJUR_URL)

    @patch.object(keyring, 'delete_password', side_effect=keyring.errors.PasswordDeleteError)
    def test_delete_password_returns_none_on_password_delete_error(self, mock_keyring):
        self.assertEquals(None, KeystoreAdapter.delete_password(CONJUR_URL))

    @patch.object(keyring, 'get_password', return_value=None)
    def test_is_keyring_accessible_return_true_when_get_password_words(self, mock_keyring):
        keyring_accessible = KeystoreAdapter.is_keyring_accessible()
        calls = [
            call('test-system', 'test-accessibility')
        ]
        mock_keyring.assert_has_calls(calls)
        self.assertEquals(True, keyring_accessible)

    @patch.object(keyring, 'get_password', side_effect=keyring.errors.KeyringError)
    def test_is_keyring_accessible_returns_false_on_keyring_error(self, mock_keyring):
        self.assertEquals(False, KeystoreAdapter.is_keyring_accessible())
