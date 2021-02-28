import unittest
from unittest.mock import MagicMock, patch

from conjur.util.credentials_from_file import CredentialsFromFile
from conjur.logic.logout_logic import LogoutLogic


class LogoutLogicTest(unittest.TestCase):
    def test_logout_logic_constructor(self):
        mock_credentials = CredentialsFromFile
        mock_logout_logic = LogoutLogic(mock_credentials)

        self.assertEquals(mock_logout_logic.credentials, mock_credentials)

    @patch('conjur.util.credentials_from_file')
    def test_logout_remove_credentials_calls_remove_credentials(self, mock_credentials):
        mock_logout_logic = LogoutLogic(mock_credentials)
        mock_logout_logic.remove_credentials("someurl")
        mock_credentials.remove_credentials.assert_called_once_with("someurl")
