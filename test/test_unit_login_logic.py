import unittest
from unittest.mock import patch

import conjur_api
from conjur_api.models import SslVerificationMetadata, SslVerificationMode, ConjurConnectionInfo
from conjur_api.errors.errors import HttpSslError
from conjur.data_object import ConjurrcData
from conjur.errors import CertificateVerificationException
from conjur.logic.credential_provider.file_credentials_provider import FileCredentialsProvider
from conjur.logic.login_logic import LoginLogic


class MockCredentialsData:
    machine = 'https://someurl'
    username = 'somelogin'
    password = 'somepass'


MockConjurrc = ConjurrcData('https://someurl', 'someacc', 'some/path/to/pem')


class MockConjurrcEmptyCertEntry:
    conjur_url = 'https://someurl'
    conjur_account = 'someacc'
    cert_file = ''


class MockClientResponse:
    def __init__(self, text='myretval', content='mycontent'):
        setattr(self, 'content', content.encode('utf-8'))
        setattr(self, 'text', text)


class LoginLogicTest(unittest.TestCase):
    credential_store = FileCredentialsProvider
    login_logic = LoginLogic(credential_store)

    def test_login_logic_controller_constructor(self):
        mock_credential_provider = None
        login_logic = LoginLogic(mock_credential_provider)
        self.assertEquals(login_logic.credentials_provider, mock_credential_provider)

    def test_verify_false_invoke_endpoint_and_passes_false(self):
        with patch('conjur_api.Client.login', return_value=MockClientResponse()) as mock_endpoint:
            ssl_verification_metadata = SslVerificationMetadata(SslVerificationMode.TRUST_STORE)
            LoginLogic.get_api_key(ssl_verification_metadata, MockCredentialsData, 'somepass', MockConjurrc)

    def test_raise_CertificateVerificationException_on_HttpSslError(self):
        with self.assertRaises(CertificateVerificationException):
            with patch('conjur_api.Client.login', side_effect=HttpSslError) as mock:
                mock_credential_store = FileCredentialsProvider()
                mock_login_logic = LoginLogic(mock_credential_store)
                ssl_verification_metadata = SslVerificationMetadata(SslVerificationMode.TRUST_STORE)
                mock_login_logic.get_api_key(ssl_verification_metadata, MockCredentialsData, 'somepass', ConjurrcData())

    @patch('conjur_api.Client.login', return_value=MockClientResponse())
    def test_return_enpoint_text(self, mock_invoke_endpoint):
        mock_credential_store = FileCredentialsProvider
        mock_login_logic = LoginLogic(mock_credential_store)
        ssl_verification_metadata = SslVerificationMetadata(SslVerificationMode.SELF_SIGN, MockConjurrc.cert_file)
        ret = mock_login_logic.get_api_key(ssl_verification_metadata, MockCredentialsData, 'somepass', MockConjurrc)
        self.assertEquals(ret.text, mock_invoke_endpoint.return_value.text)
