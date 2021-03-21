import unittest
from unittest.mock import patch, call

from conjur.data_object import CredentialsData
from conjur.errors import OperationNotCompletedException, CredentialRetrievalException
from conjur.logic.credential_provider import KeystoreCredentialsProvider
from conjur.wrapper import KeystoreAdapter

MockCredentials = CredentialsData(machine="https://somemachine", login='somelogin', password='somepass')

class KeystoreCredentialsProviderTest(unittest.TestCase):

    @patch.object(KeystoreAdapter, 'set_password')
    def test_save_calls_methods_properly(self, mock_store_adapter):
        # mock_store_adapter.set_password.return_value=None
        credential_provider = KeystoreCredentialsProvider()
        credential_provider.save(MockCredentials)
        calls = [call('https://somemachine', 'machine', 'https://somemachine'), call('https://somemachine', 'login', 'somelogin'), call('https://somemachine', 'password', 'somepass') ]
        mock_store_adapter.assert_has_calls(calls)

    @patch.object(KeystoreAdapter, 'set_password', side_effect=Exception)
    def test_save_can_raise_operation_not_complete_exception(self, mock_store_adapter):
        with self.assertRaises(OperationNotCompletedException):
            credential_provider = KeystoreCredentialsProvider()
            credential_provider.save(MockCredentials)

    @patch.object(KeystoreCredentialsProvider, 'is_exists', return_value=False)
    def test_load_credentials_do_not_exist_raises_credential_retrieval_exception(self, mock_cred_provider):
        with self.assertRaises(CredentialRetrievalException):
            credential_provider = KeystoreCredentialsProvider()
            credential_provider.load('https://someurl')

    @patch.object(KeystoreAdapter, 'set_password')
    def test_update_api_key_calls_methods_properly(self, mock_store_adapter):
        # mock_store_adapter.set_password.return_value=None
        credential_provider = KeystoreCredentialsProvider()
        credential_provider.update_api_key_entry('someusertoupdate', MockCredentials, 'newapikey')
        calls = [call('https://somemachine', 'machine', 'https://somemachine'), call('https://somemachine', 'login', 'someusertoupdate'), call('https://somemachine', 'password', 'newapikey') ]
        mock_store_adapter.assert_has_calls(calls)

    @patch.object(KeystoreAdapter, 'set_password', side_effect=Exception)
    def test_update_api_key_can_raise_operation_not_complete_exception(self, mock_store_adapter):
        with self.assertRaises(OperationNotCompletedException):
            credential_provider = KeystoreCredentialsProvider()
            credential_provider.update_api_key_entry('someusertoupdate', MockCredentials, 'newapikey')
