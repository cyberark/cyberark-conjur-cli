# Builtin
import unittest
from unittest.mock import patch, call
# Third-Party
import keyring
# Internal
from conjur.constants import TEST_HOSTNAME, PASSWORD, USERNAME, MACHINE, TEST_KEYRING
from conjur.data_object import ConjurrcData
from conjur_api.models import CredentialsData
from conjur.errors import OperationNotCompletedException, CredentialRetrievalException, KeyringWrapperGeneralError
from conjur.logic.credential_provider import KeystoreCredentialsProvider
from conjur.wrapper import KeystoreWrapper

MockCredentials = CredentialsData(machine=TEST_HOSTNAME, username='somelogin', password='somepass')
MockConjurrcData = ConjurrcData(conjur_url=TEST_HOSTNAME, account="admin")


class KeystoreCredentialsProviderTest(unittest.TestCase):

    @patch.object(KeystoreWrapper, 'set_password')
    def test_save_calls_methods_properly(self, mock_store_wrapper):
        credential_provider = KeystoreCredentialsProvider()
        credential_provider.save(MockCredentials)
        calls = [
            call(TEST_HOSTNAME, MACHINE, TEST_HOSTNAME),
            call(TEST_HOSTNAME, USERNAME, 'somelogin'),
            call(TEST_HOSTNAME, PASSWORD, 'somepass')
        ]
        mock_store_wrapper.assert_has_calls(calls)

    @patch.object(KeystoreWrapper, 'set_password', side_effect=Exception)
    def test_save_can_raise_operation_not_complete_exception(self, mock_store_wrapper):
        with self.assertRaises(OperationNotCompletedException):
            credential_provider = KeystoreCredentialsProvider()
            credential_provider.save(MockCredentials)

    @patch.object(KeystoreCredentialsProvider, 'is_exists', return_value=False)
    def test_load_credentials_do_not_exist_raises_credential_retrieval_exception(self, mock_cred_provider):
        with self.assertRaises(CredentialRetrievalException):
            credential_provider = KeystoreCredentialsProvider()
            credential_provider.load(TEST_HOSTNAME)

    @patch.object(KeystoreCredentialsProvider, 'is_exists', return_value=True)
    @patch.object(KeystoreWrapper, "get_password", return_value="password")
    @patch.object(CredentialsData, "convert_dict_to_obj", return_value=MockCredentials)
    def test_load_credentials_calls_get_password(self, mock_credentials_data, mock_store_wrapper, mock_cred_provider):
        credential_provider = KeystoreCredentialsProvider()
        credentials_data = credential_provider.load(TEST_HOSTNAME)
        calls = [
            call(TEST_HOSTNAME, MACHINE),
            call(TEST_HOSTNAME, USERNAME),
            call(TEST_HOSTNAME, PASSWORD)
        ]
        mock_store_wrapper.assert_has_calls(calls)
        self.assertEquals(MockCredentials.machine, credentials_data.machine)
        self.assertEquals(MockCredentials.username, credentials_data.username)
        self.assertEquals(MockCredentials.password, credentials_data.password)

    @patch.object(KeystoreWrapper, 'set_password')
    def test_update_api_key_calls_methods_properly(self, mock_store_wrapper):
        # mock_store_wrapper.set_password.return_value=None
        credential_provider = KeystoreCredentialsProvider()
        credential_provider.update_api_key_entry('someusertoupdate', MockCredentials, 'newapikey')
        calls = [call(TEST_HOSTNAME, MACHINE, TEST_HOSTNAME),
                 call(TEST_HOSTNAME, USERNAME, 'someusertoupdate'),
                 call(TEST_HOSTNAME, PASSWORD, 'newapikey')]
        mock_store_wrapper.assert_has_calls(calls)

    @patch.object(KeystoreWrapper, 'set_password', side_effect=Exception)
    def test_update_api_key_can_raise_operation_not_complete_exception(self, mock_store_wrapper):
        with self.assertRaises(OperationNotCompletedException):
            credential_provider = KeystoreCredentialsProvider()
            credential_provider.update_api_key_entry('someusertoupdate', MockCredentials, 'newapikey')

    @patch.object(KeystoreWrapper, "get_password", return_value=None)
    def test_is_exists_return_false_if_attr_not_exists(self, mock_store_wrapper):
        credential_provider = KeystoreCredentialsProvider()
        self.assertEquals(False, credential_provider.is_exists(TEST_HOSTNAME))

    @patch.object(KeystoreWrapper, "get_password", return_value="password")
    def test_is_exists_return_true_when_attr_exists(self, mock_store_wrapper):
        credential_provider = KeystoreCredentialsProvider()
        self.assertEquals(True, credential_provider.is_exists(TEST_HOSTNAME))

    @patch.object(KeystoreWrapper, "get_password", side_effect=Exception)
    def test_is_exists_raises_exception_when_exception_is_thrown_by_get_password(self, mock_store_wrapper):
        credential_provider = KeystoreCredentialsProvider()
        with self.assertRaises(Exception):
            credential_provider.is_exists(TEST_HOSTNAME)

    @patch.object(KeystoreWrapper, "delete_password", return_value=None)
    @patch.object(KeystoreWrapper, "get_keyring_name", return_value=TEST_KEYRING)
    def test_remove_credentials_calls_delete_password_for_each_credential(self, mock_keyring_name,
                                                                          mock_delete_password):
        credential_provider = KeystoreCredentialsProvider()
        credential_provider.remove_credentials(MockConjurrcData)
        calls = [call(TEST_HOSTNAME, MACHINE),
                 call(TEST_HOSTNAME, USERNAME),
                 call(TEST_HOSTNAME, PASSWORD)]
        mock_delete_password.assert_has_calls(calls)

    @patch.object(KeystoreWrapper, "delete_password", side_effect=KeyringWrapperGeneralError)
    @patch.object(KeystoreWrapper, "get_keyring_name", return_value=TEST_KEYRING)
    def test_remove_credentials_raises_keyring_error_when_delete_password_raises_keyring_error(self,
                                                                                               mock_keystore_wrapper,
                                                                                               another_mock_keystore_wrapper):
        credential_provider = KeystoreCredentialsProvider()
        with self.assertRaises(Exception):
            credential_provider.remove_credentials(MockConjurrcData)

    @patch.object(KeystoreWrapper, "get_password", return_value="somepassword")
    @patch.object(KeystoreWrapper, "delete_password", return_value=None)
    @patch.object(KeystoreWrapper, "get_keyring_name", return_value=TEST_KEYRING)
    def test_cleanup_calls_delete_for_each_attribute(self, mock_keyring_name, mock_delete_password, mock_get_password):
        credential_provider = KeystoreCredentialsProvider()
        credential_provider.remove_credentials(MockConjurrcData)
        calls = [call(TEST_HOSTNAME, MACHINE),
                 call(TEST_HOSTNAME, USERNAME),
                 call(TEST_HOSTNAME, PASSWORD)]
        mock_delete_password.assert_has_calls(calls)
