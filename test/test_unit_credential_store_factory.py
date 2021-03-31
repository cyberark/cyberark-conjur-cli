# Builtin
import unittest
from unittest.mock import patch, call

from conjur.constants import TEST_KEYRING
from conjur.logic.credential_provider import CredentialStoreFactory, KeystoreCredentialsProvider, \
    FileCredentialsProvider
from conjur.wrapper import KeystoreAdapter


class CredentialStoreFactoryTest(unittest.TestCase):
    @patch.object(KeystoreAdapter, "get_keyring_name", return_value=TEST_KEYRING)
    @patch.object(KeystoreAdapter, "is_keyring_accessible", return_value=True)
    def test_create_credential_store_returns_keystore_when_there_is_keyring_and_is_accessible(
            self, mock_keystore_adapter, mock_another_keystore_adapter):
        provider, _ = CredentialStoreFactory.create_credential_store()
        self.assertIsInstance(provider, KeystoreCredentialsProvider)

    @patch.object(KeystoreAdapter, "get_keyring_name", return_value=None)
    def test_create_credential_store_returns_file_when_there_is_no_keyring(self,
                                                                           mock_keystore_adapter):
        provider, _ = CredentialStoreFactory.create_credential_store()
        self.assertIsInstance(provider, FileCredentialsProvider)

    @patch.object(KeystoreAdapter, "get_keyring_name", return_value=TEST_KEYRING)
    @patch.object(KeystoreAdapter, "is_keyring_accessible", return_value=False)
    def test_create_credential_store_returns_file_when_there_is_keyring_and_its_not_accessible(
            self, mock_keystore_adapter, mock_another_keystore_adapter):
        provider, _ = CredentialStoreFactory.create_credential_store()
        self.assertIsInstance(provider, FileCredentialsProvider)
