import unittest
from unittest.mock import patch

from conjur.errors import CertificateVerificationException
from conjur.logic.credential_provider.file_credentials_provider import FileCredentialsProvider
from conjur.api.endpoints import ConjurEndpoint
from conjur.wrapper.http_wrapper import HttpVerb
from conjur.logic.login_logic import LoginLogic

class MockCredentialsData:
    machine = 'https://someurl'
    login = 'somelogin'
    password = 'somepass'

class MockConjurrc:
    conjur_url = 'https://someurl'
    conjur_account = 'someacc'
    cert_file = 'some/path/to/pem'

class MockConjurrcEmptyCertEntry:
    conjur_url = 'https://someurl'
    conjur_account = 'someacc'
    cert_file = ''

class MockClientResponse():
    def __init__(self, text='myretval', content='mycontent'):
        setattr(self, 'content', content.encode('utf-8'))
        setattr(self, 'text', text)

class LoginLogicTest(unittest.TestCase):
    credential_store = FileCredentialsProvider
    login_logic = LoginLogic(credential_store)

    def test_login_logic_controller_constructor(self):
        mock_credential_store = None
        login_logic = LoginLogic(mock_credential_store)
        self.assertEquals(login_logic.credentials_provider, mock_credential_store)

    def test_verify_false_invoke_endpoint_and_passes_false(self):
        with patch('conjur.logic.login_logic.invoke_endpoint', return_value=MockClientResponse()) as mock_endpoint:
            LoginLogic.get_api_key(False, MockCredentialsData, 'somepass', MockConjurrc)
            params={'url':'https://someurl','account':'someacc'}
            mock_endpoint.assert_called_once_with(HttpVerb.GET,
                                                         ConjurEndpoint.LOGIN,
                                                         params,
                                                         auth=('somelogin', 'somepass'),
                                                         ssl_verify=False)

    @patch('conjur.logic.login_logic.invoke_endpoint', return_value=MockClientResponse())
    def test_verify_true_invoke_endpoint_and_passes_cert_path(self, mock_invoke_endpoint):
        mock_credential_store = FileCredentialsProvider
        mock_login_logic = LoginLogic(mock_credential_store)
        mock_login_logic.get_api_key(True, MockCredentialsData, 'somepass', MockConjurrc)
        params={'url':'https://someurl','account':'someacc'}
        mock_invoke_endpoint.assert_called_once_with(HttpVerb.GET,
                                                     ConjurEndpoint.LOGIN,
                                                     params,
                                                     auth=('somelogin', 'somepass'),
                                                     ssl_verify='some/path/to/pem')

    def test_empty_cert_file_entry_and_ssl_verify_enabled(self):
        with self.assertRaises(CertificateVerificationException):
            mock_login_logic = LoginLogic(MockCredentialsData)
            mock_login_logic.get_api_key(True, MockCredentialsData, 'somepass', MockConjurrcEmptyCertEntry)
