import unittest
from unittest.mock import MagicMock, patch
from conjur.controller.logout_controller import LogoutController
from conjur.data_object import ConjurrcData


class MockConjurrc:
    conjur_url = 'https://someurl'
    conjur_account = 'someacc'
    cert_file = 'some/path/to/pem'


class LogoutControllerTest(unittest.TestCase):
    def test_logout_controller_constructor(self):
        mock_ssl_verify = True
        mock_logout_logic = None
        mock_logout_controller = LogoutController(mock_ssl_verify, mock_logout_logic)
        self.assertEquals(mock_logout_controller.ssl_verify, mock_ssl_verify)
        self.assertEquals(mock_logout_controller.logout_logic, mock_logout_logic)

    @patch('os.path.exists', return_value=True)
    @patch('os.path.getsize', return_value=1)
    @patch('conjur.data_object.conjurrc_data.ConjurrcData.load_from_file', return_value=MockConjurrc)
    @patch('conjur.logic.logout_logic')
    def test_logout_removes_credentials(self, mock_logout_logic, mock_exists, mock_size, mock_conjurrc):
        mock_logout_logic.remove_credentials = MagicMock()
        mock_logout_controller = LogoutController(True, mock_logout_logic)
        mock_logout_controller.remove_credentials()
        mock_logout_logic.remove_credentials.assert_called_once_with(MockConjurrc.conjur_url)

    @patch('os.path.exists', return_value=True)
    @patch('os.path.getsize', return_value=0)
    @patch('conjur.logic.logout_logic')
    def test_logout_netrc_does_not_exist_raises_already_logged_out_exception(self, mock_logout_logic, mock_exists, mock_size):
        mock_logout_controller = LogoutController(True, mock_logout_logic)
        with self.assertRaises(Exception):
            mock_logout_controller.remove_credentials()

    @patch('os.path.exists', return_value=True)
    @patch('os.path.getsize', return_value=1)
    @patch('conjur.logic.logout_logic')
    def test_logout_remove_credentials_operation_fails_raises_exception(self, mock_logout_logic, mock_size, mock_conjurrc):
        with patch.object(ConjurrcData, 'load_from_file', side_effect=Exception):
            with self.assertRaises(Exception):
                mock_logout_controller = LogoutController(True, mock_logout_logic)
                mock_logout_controller.remove_credentials()
