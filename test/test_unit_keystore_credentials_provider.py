# Builtin
import unittest
from unittest.mock import patch, call
# Third-Party
import keyring
# Internal
from conjur.data_object import CredentialsData, ConjurrcData
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
        calls = [call('https://somemachine', 'machine', 'https://somemachine'),
                 call('https://somemachine', 'login', 'somelogin'), call('https://somemachine', 'password', 'somepass')]
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

    @patch.object(KeystoreCredentialsProvider, 'is_exists', return_value=True)
    @patch.object(KeystoreAdapter, "get_password", return_value="password")
    def test_load_credentials_calls_get_password(self, mock_store_adapter, mock_cred_provider):
        credential_provider = KeystoreCredentialsProvider()
        credentials_data = credential_provider.load('https://someurl')
        calls = [call('https://someurl', 'machine'), call('https://someurl', 'login'),
                 call('https://someurl', 'password')]
        mock_store_adapter.assert_has_calls(calls)
        self.assertEquals("password", credentials_data.machine)
        self.assertEquals("password", credentials_data.login)
        self.assertEquals("password", credentials_data.password)

    @patch.object(KeystoreAdapter, 'set_password')
    def test_update_api_key_calls_methods_properly(self, mock_store_adapter):
        # mock_store_adapter.set_password.return_value=None
        credential_provider = KeystoreCredentialsProvider()
        credential_provider.update_api_key_entry('someusertoupdate', MockCredentials, 'newapikey')
        calls = [call('https://somemachine', 'machine', 'https://somemachine'),
                 call('https://somemachine', 'login', 'someusertoupdate'),
                 call('https://somemachine', 'password', 'newapikey')]
        mock_store_adapter.assert_has_calls(calls)

    @patch.object(KeystoreAdapter, 'set_password', side_effect=Exception)
    def test_update_api_key_can_raise_operation_not_complete_exception(self, mock_store_adapter):
        with self.assertRaises(OperationNotCompletedException):
            credential_provider = KeystoreCredentialsProvider()
            credential_provider.update_api_key_entry('someusertoupdate', MockCredentials, 'newapikey')

    @patch.object(KeystoreAdapter, "get_password", return_value=None)
    def test_is_exists_return_false_if_attr_not_exists(self, mock_store_adapter):
        credential_provider = KeystoreCredentialsProvider()
        self.assertEquals(False, credential_provider.is_exists('https://somemachine'))

    @patch.object(KeystoreAdapter, "get_password", return_value="password")
    def test_is_exists_return_true_when_attr_exists(self, mock_store_adapter):
        credential_provider = KeystoreCredentialsProvider()
        self.assertEquals(True, credential_provider.is_exists('https://somemachine'))

    @patch.object(KeystoreAdapter, "get_password", side_effect=Exception)
    def test_is_exists_raises_exception_when_exception_is_thrown_by_get_password(self, mock_store_adapter):
        credential_provider = KeystoreCredentialsProvider()
        with self.assertRaises(Exception):
            credential_provider.is_exists('https://somemachine')

    @patch.object(KeystoreAdapter, 'delete_password', return_value=None)
    def test_remove_credentials_calls_delete_password(self, mock_keystore_adapter):
        mock_keystore_adapter.get_keyring_name.return_value = "keyring"
        credential_provider = KeystoreCredentialsProvider()
        conjurrc_data = ConjurrcData(conjur_url="https://conjur-hostname.com", account="admin")
        credential_provider.remove_credentials(conjurrc_data)
        calls = [
            call("https://conjur-hostname.com"),
        ]
        mock_keystore_adapter.assert_has_calls(calls)

    @patch.object(KeystoreAdapter, 'delete_password', side_effect=keyring.errors.KeyringError)
    def test_remove_credentials_raises_keyring_error_when_delete_password_raises_keyring_error(self,
                                                                                               mock_keystore_adapter):
        mock_keystore_adapter.get_keyring_name.return_value = "keyring"
        credential_provider = KeystoreCredentialsProvider()
        conjurrc_data = ConjurrcData(conjur_url="https://conjur-hostname.com", account="admin")
        with self.assertRaises(keyring.errors.KeyringError):
            credential_provider.remove_credentials(conjurrc_data)
