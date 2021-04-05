# Builtin
import unittest
from unittest.mock import patch, call
# Third-Party
import keyring
# Internal
from conjur.constants import TEST_HOSTNAME
from conjur.errors import KeyringAdapterDeletionError, KeyringAdapterGeneralError
from conjur.wrapper import KeystoreAdapter
from conjur.util import util_functions


class KeystoreAdapterTest(unittest.TestCase):
    @patch.object(keyring, "delete_password")
    def test_delete_password_calls_keyring_delete_password(self, mock_keyring):
        KeystoreAdapter.delete_password(TEST_HOSTNAME, "key")
        mock_keyring.assert_called_once_with(TEST_HOSTNAME, "key")

    @patch.object(keyring, "delete_password", side_effect=keyring.errors.KeyringError)
    def test_delete_password_raises_keyring_error(self, mock_keyring):
        with self.assertRaises(KeyringAdapterGeneralError):
            KeystoreAdapter.delete_password(TEST_HOSTNAME, "some_key")

    @patch.object(keyring, "delete_password", side_effect=keyring.errors.PasswordDeleteError)
    def test_delete_password_expected_exceptions(self, mock_keyring):
        with self.assertRaises(KeyringAdapterDeletionError):
            KeystoreAdapter.delete_password(TEST_HOSTNAME, "some_key")

    @patch.object(keyring, "get_password", return_value=None)
    def test_is_keyring_accessible_return_true_when_get_password(self, mock_keyring):
        keyring_accessible = KeystoreAdapter.is_keyring_accessible()
        mock_keyring.assert_called_once_with('test-system', 'test-accessibility')
        self.assertEquals(True, keyring_accessible)

    @patch.object(keyring, "get_password", side_effect=keyring.errors.KeyringError)
    def test_is_keyring_accessible_returns_false_on_keyring_error(self, mock_keyring):
        self.assertEquals(False, KeystoreAdapter.is_keyring_accessible())

    @patch.object(util_functions, "configure_env_var_with_keyring")
    def test_env_variables_set_on_keyring_adapter_import(self, mock_utils):
        import importlib
        import conjur.wrapper.keystore_adapter
        importlib.reload(conjur.wrapper.keystore_adapter)
        mock_utils.assert_called_once()
