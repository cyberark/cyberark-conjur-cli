# Builtin
import unittest
from unittest.mock import patch, call

from conjur.logic.credential_provider import CredentialStoreFactory, KeystoreCredentialsProvider, \
    FileCredentialsProvider
from conjur.wrapper import KeystoreAdapter


class CredentialStoreFactoryTest(unittest.TestCase):
    @patch.object(KeystoreAdapter, "get_keyring_name", return_value="SecretService Keyring")
    @patch.object(KeystoreAdapter, "is_keyring_accessible", return_value=True)
    def test_create_credential_store_returns_keystore_credentials_provider_when_there_is_keyring_and_its_accessible(
            self, mock_keystore_adapter, mock_another_keystore_adapter):
        provider, message = CredentialStoreFactory.create_credential_store()
        self.assertIsInstance(provider, KeystoreCredentialsProvider)

    test_create_credential_store_returns_keystore_credentials_provider_when_there_is_keyring_and_its_accessible.t1 = True

    @patch.object(KeystoreAdapter, "get_keyring_name", return_value=None)
    def test_create_credential_store_returns_file_credentials_provider_when_there_is_no_keyring(self,
                                                                                                mock_keystore_adapter):
        provider, message = CredentialStoreFactory.create_credential_store()
        self.assertIsInstance(provider, FileCredentialsProvider)

    @patch.object(KeystoreAdapter, "get_keyring_name", return_value="keyring")
    def test_create_credential_store_returns_file_credentials_provider_when_there_is_keyring_and_its_not_accessible(
            self, mock_keystore_adapter):
        mock_keystore_adapter.is_keyring_accessible.return_value = False
        provider, message = CredentialStoreFactory.create_credential_store()
        self.assertIsInstance(provider, FileCredentialsProvider)
