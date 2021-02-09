import unittest
from unittest.mock import MagicMock, patch

import conjur
from conjur.logic.credentials_from_file import CredentialsFromFile
from conjur.api.endpoints import ConjurEndpoint
from conjur.wrapper.http_wrapper import HttpVerb
from conjur.logic.login_logic import LoginLogic

class MockCredentialsData:
    machine = 'https://someurl'
    login = 'somelogin'
    api_key = 'somepass'

class MockConjurrc:
    appliance_url = 'https://someurl'
    account = 'someacc'
    cert_file = 'some/path/to/pem'
    plugins: []

class MockClientResponse():
    def __init__(self, text='myretval', content='mycontent'):
        setattr(self, 'content', content.encode('utf-8'))
        setattr(self, 'text', text)

class LoginLogicTest(unittest.TestCase):
    credential_store = CredentialsFromFile
    login_logic = LoginLogic(credential_store)

    def test_login_logic_controller_constructor(self):
        mock_credential_store = None
        login_logic = LoginLogic(mock_credential_store)
        self.assertEquals(login_logic.credentials_storage, mock_credential_store)

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
        mock_credential_store = CredentialsFromFile
        mock_login_logic = LoginLogic(mock_credential_store)
        mock_login_logic.get_api_key(True, MockCredentialsData, 'somepass', MockConjurrc)
        params={'url':'https://someurl','account':'someacc'}
        mock_invoke_endpoint.assert_called_once_with(HttpVerb.GET,
                                                     ConjurEndpoint.LOGIN,
                                                     params,
                                                     auth=('somelogin', 'somepass'),
                                                     ssl_verify='some/path/to/pem')
