import unittest
from unittest.mock import MagicMock, patch

from conjur.api.models import SslVerificationMetadata, SslVerificationMode
from conjur.errors import CertificateVerificationException, MissingRequiredParameterException, \
    HttpError
from conjur.util import util_functions
from conjur.data_object.credentials_data import CredentialsData
from conjur.controller.login_controller import LoginController
from conjur.logic.login_logic import LoginLogic


class MockConjurrc:
    conjur_url = 'https://someurl'
    account = 'someacc'
    cert_file = 'some/path/to/pem'


class MockCredentialsData:
    machine = 'https://someurl'
    login = 'somelogin'
    api_key = 'somepass'



class LoginControllerTest(unittest.TestCase):
    mock_ssl_verify = SslVerificationMetadata(SslVerificationMode.SELF_SIGN, 'path/to/cert')
    def test_login_controller_constructor(self):

        mock_user_password = None
        mock_credential_data = None
        mock_login_logic = None
        mock_login_controller = LoginController(self.mock_ssl_verify, mock_user_password, mock_credential_data,
                                                mock_login_logic)
        self.assertEquals(mock_login_controller.user_password, mock_user_password)
        self.assertEquals(mock_login_controller.credential_data, mock_credential_data)
        self.assertEquals(mock_login_controller.login_logic, mock_login_logic)

    def test_login_controller_constructor_with_ssl_verify_false_calls_warning_message(self):
        mock_ssl_verify = SslVerificationMetadata(SslVerificationMode.INSECURE)
        util_functions.get_insecure_warning_in_debug = MagicMock()
        LoginController(mock_ssl_verify, None, None, None)
        util_functions.get_insecure_warning_in_debug.assert_called_once()

    def test_login_load_calls_all_functions_correctly(self):
        mock_credential_data = CredentialsData
        mock_login_logic = LoginLogic
        mock_login_controller = LoginController(self.mock_ssl_verify, 'someuserpass', mock_credential_data, mock_login_logic)
        mock_login_controller.get_username = MagicMock()
        mock_login_controller.get_password = MagicMock()
        mock_login_controller.get_api_key = MagicMock()
        mock_login_controller.load_conjurrc_data = MagicMock()
        mock_login_logic.save = MagicMock()
        mock_login_controller.load()
        mock_login_controller.get_username.assert_called_once()
        mock_login_controller.get_password.assert_called_once()
        mock_login_logic.save.assert_called_once_with(mock_credential_data)

    @patch('builtins.input', return_value='')
    def test_login_raises_error_when_not_provided_username(self, mock_input):
        mock_credential_data = CredentialsData('somemachine', None, 'somepass')
        mock_login_controller = LoginController(self.mock_ssl_verify, 'someuserpass', mock_credential_data, LoginLogic)
        with self.assertRaises(MissingRequiredParameterException):
            mock_login_controller.get_username()

    @patch('getpass.getpass', side_effect=['', 'somepass'])
    def test_login_user_does_not_provide_password_prompts_for_one(self, mock_input):
        mock_credential_data = CredentialsData('somemachine', None, 'somepass')
        mock_login_controller = LoginController(self.mock_ssl_verify, None, mock_credential_data, LoginLogic)
        mock_login_controller.get_password()

    @patch('conjur.data_object.conjurrc_data.ConjurrcData.load_from_file', return_value=MockConjurrc)
    def test_login_conjurrc_is_loaded(self, mock_conjurrc_data):
        mock_login_controller = LoginController(self.mock_ssl_verify, None, MockCredentialsData, LoginLogic)
        self.assertEquals(MockConjurrc, mock_login_controller.load_conjurrc_data())

    def test_login_get_api_key_is_called(self):
        with patch('conjur.logic.login_logic') as mock_logic:
            mock_logic.get_api_key = MagicMock()
            mock_login_controller = LoginController(self.mock_ssl_verify, None, MockCredentialsData, mock_logic)
            mock_login_controller.user_password = 'somepass'
            mock_login_controller.get_api_key(MockConjurrc)
            mock_logic.get_api_key.assert_called_once_with(mock_login_controller.ssl_verification_metadata,
                                                           MockCredentialsData,
                                                           mock_login_controller.user_password,
                                                           MockConjurrc)

    @patch('conjur.logic.login_logic')
    def test_login_get_api_can_raise_operation_invalid_operation_exception(self, mock_logic):
        mock_logic.get_api_key = MagicMock(side_effect=CertificateVerificationException)
        mock_login_controller = LoginController(self.mock_ssl_verify, None, MockCredentialsData, mock_logic)
        with self.assertRaises(CertificateVerificationException):
            mock_login_controller.get_api_key('someconjurrc')

    def test_login_raises_error_when_error_occurred_while_getting_api_key(self):
        mock_response = MagicMock()
        mock_response.status_code = 401
        with patch('conjur.logic.login_logic') as mock_logic:
            mock_logic.get_api_key = MagicMock(side_effect=HttpError(response=mock_response))
            mock_login_controller = LoginController(self.mock_ssl_verify, None, MockCredentialsData, mock_logic)
            with self.assertRaises(HttpError):
                mock_login_controller.get_api_key(MockCredentialsData)
