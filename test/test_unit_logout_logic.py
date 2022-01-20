import unittest
from unittest.mock import patch

from conjur.data_object import ConjurrcData
from conjur.logic.credential_provider.file_credentials_provider import FileCredentialsProvider
from conjur.logic.logout_logic import LogoutLogic


class LogoutLogicTest(unittest.TestCase):
    def test_logout_logic_constructor(self):
        mock_credentials = FileCredentialsProvider
        mock_logout_logic = LogoutLogic(mock_credentials)

        self.assertEquals(mock_logout_logic.credentials_provider, mock_credentials)

    @patch('conjur.logic.credential_provider.file_credentials_provider')
    def test_logout_remove_credentials_calls_remove_credentials(self, mock_credentials):
        conjurrc = ConjurrcData("someurl")
        mock_logout_logic = LogoutLogic(mock_credentials)
        mock_logout_logic.remove_credentials(conjurrc)
        mock_credentials.remove_credentials.assert_called_once_with("someurl")
