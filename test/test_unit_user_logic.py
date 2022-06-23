import unittest
from unittest.mock import MagicMock, patch

from conjur_api import Client
from conjur_api.models import CredentialsData
from conjur_api.errors.errors import HttpError
from conjur.errors import OperationNotCompletedException

from conjur.data_object.conjurrc_data import ConjurrcData
from conjur.logic.credential_provider.file_credentials_provider import FileCredentialsProvider
from conjur.logic.user_logic import UserLogic

MockCredentials = CredentialsData(username='someuser', password="somePassword", api_key='someAPIKey')

class MockConjurrc:
    conjur_url = 'someurl'
    account = 'someacc'
    cert_file = 'some/path/to/pem'


CONJURRC_DICT = {'conjur_url': 'someurl',
                 'account': 'someacc',
                 'cert_file': 'some/path/to/pem'}


class UserLogicTest(unittest.TestCase):
    conjurrc_data = ConjurrcData('someurl', 'someacc', 'some/path/to/pem')
    credential_provider = FileCredentialsProvider()
    client = Client
    user_logic = UserLogic(conjurrc_data, credential_provider, client)

    def test_user_logic_constructor(self):
        mock_conjurrc_data = None
        mock_credential_provider = None
        mock_client = None
        user_logic = UserLogic(mock_conjurrc_data, mock_credential_provider, mock_client)
        self.assertEquals(user_logic.conjurrc_data, mock_conjurrc_data)
        self.assertEquals(user_logic.credential_provider, mock_credential_provider)
        self.assertEquals(user_logic.client, mock_client)

    '''
    Validate that if user doesn't provide username, rotate_other_api_key will be called once with proper params
    '''
    def test_user_does_not_provide_username_can_rotate_own_key(self):
        self.user_logic.extract_credentials_from_credential_store = MagicMock(return_value=MockCredentials)
        self.user_logic.rotate_other_api_key = MagicMock(return_value='someAPIKey')
        self.user_logic.rotate_api_key('someUserToRotate')
        self.user_logic.rotate_other_api_key.assert_called_once_with('someUserToRotate')

    '''
    Validate that if user doesn't provide username, rotate_personal_api_key will be called once with proper params
    '''
    def test_user_provides_username_can_rotate_anothers_key(self):
        self.user_logic.extract_credentials_from_credential_store = MagicMock(return_value=MockCredentials)
        self.user_logic.rotate_personal_api_key = MagicMock(return_value='someAPIKey')
        self.user_logic.rotate_api_key(None)
        self.user_logic.rotate_personal_api_key.assert_called_once_with('someuser',
                                                                        MockCredentials,
                                                                        'someAPIKey')

    def test_change_password_returns_user(self):
        with patch.object(UserLogic, 'extract_credentials_from_credential_store', return_value=MockCredentials):
            client = MagicMock(return_value=None)
            mock_user_logic = UserLogic(ConjurrcData, FileCredentialsProvider, client)
            mock_user_logic.client.change_personal_password = MagicMock(return_value='success!')
            resource_to_update = mock_user_logic.change_personal_password('someNewPassword')
            self.assertEquals(resource_to_update, 'someuser')

    @patch('conjur.data_object.conjurrc_data.ConjurrcData.load_from_file', return_value=MockConjurrc)
    def test_extract_credential_provider_returns_netrc_store(self, mock_conjurrc):
        mock_user_logic = UserLogic(self.conjurrc_data, self.credential_provider, self.client)
        mock_user_logic.credential_provider.load = MagicMock(return_value=CONJURRC_DICT)
        mock_user_logic.extract_credentials_from_credential_store()
        self.assertEquals(mock_user_logic.extract_credentials_from_credential_store(), CONJURRC_DICT)

    '''
    Validates that a rotated API key for another user can be returned
    '''
    def test_rotate_other_api_key_returns_new_key(self):
        new_api_key = 'someAPIKey'
        client = MagicMock(return_value=None)
        mock_user_logic = UserLogic(ConjurrcData, FileCredentialsProvider, client)
        mock_user_logic.client.rotate_other_api_key = MagicMock(return_value=new_api_key)
        self.assertEquals(mock_user_logic.rotate_other_api_key('someuser'), new_api_key)

    '''
    Validates that a new personal API key can be returned
    '''
    def test_rotate_personal_api_key_returns_api_key(self):
        new_api_key = 'someAPIKey'
        client = MagicMock(return_value=None)
        mock_user_logic = UserLogic(ConjurrcData, FileCredentialsProvider, client)
        mock_user_logic.client.rotate_personal_api_key = MagicMock(return_value=new_api_key)
        mock_user_logic.update_api_key_in_credential_store = MagicMock(return_value='someupdatedstore!')
        self.assertEquals(mock_user_logic.rotate_personal_api_key('someuser', 'somecreds', 'somepass'), new_api_key)

    '''
    Raises exception when HTTPError was raised
    '''
    def test_rotate_personal_api_key_raises_exception_when_unauthorized(self):
        with self.assertRaises(HttpError):
            client = MagicMock(return_value=None)
            mock_user_logic = UserLogic(ConjurrcData, FileCredentialsProvider, client)
            mock_user_logic.client.rotate_personal_api_key = MagicMock(side_effect=HttpError)
            mock_user_logic.rotate_personal_api_key('someuser', 'somecreds', 'somepass')

    '''
    Raises exception when operation was not able to be completed successfully
    '''
    def test_rotate_personal_api_key_raises_exception_when_incomplete_operation(self):
        client = MagicMock(return_value=None)
        mock_user_logic = UserLogic(ConjurrcData, FileCredentialsProvider, client)
        mock_user_logic.client.rotate_personal_api_key = MagicMock(side_effect=OperationNotCompletedException)
        with self.assertRaises(OperationNotCompletedException):
            mock_user_logic.rotate_personal_api_key('someuser', 'somecreds', 'somepass')

    '''
    Validates that update_api_key_entry was called
    '''
    def test_update_entry_was_called(self):
        FileCredentialsProvider.update_api_key_entry = MagicMock()
        mock_user_logic = UserLogic(self.conjurrc_data, self.credential_provider, self.client)
        mock_user_logic.update_api_key_in_credential_store('some_user_to_update', 'loaded_creds', 'someapikey')
        FileCredentialsProvider.update_api_key_entry.assert_called_once_with('some_user_to_update', 'loaded_creds',
                                                                         'someapikey')
