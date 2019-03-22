import unittest
from datetime import datetime
from unittest.mock import call, patch, MagicMock

from conjur_api_python3.http import HttpVerb
from conjur_api_python3.endpoints import ConjurEndpoint

from conjur_api_python3.api import Api


class ApiTest(unittest.TestCase):
    class MockClientResponse(object):
        def __init__(self, text='myretval', content='mycontent'):
            self._text = text
            self._content = content

        def text(self):
            return self._text

        def content(self):
            return self._content

    @patch('conjur_api_python3.api.invoke_endpoint', return_value=MockClientResponse())
    def test_login_invokes_http_client_correctly(self, mock_http_client):
        Api(url='http://localhost').login('myuser', 'mypass')
        mock_http_client.assert_called_once_with(HttpVerb.GET,
                                                 ConjurEndpoint.LOGIN,
                                                 {
                                                     'url': 'http://localhost',
                                                     'account': 'default',
                                                 },
                                                 auth=('myuser', 'mypass'),
                                                 ssl_verify=True)

    @patch('conjur_api_python3.api.invoke_endpoint', return_value=MockClientResponse())
    def test_login_saves_login_id(self, _):
        api = Api(url='http://localhost')

        api.login('myuser', 'mypass')

        self.assertEquals(api.login_id, 'myuser')

    @patch('conjur_api_python3.api.invoke_endpoint', return_value=MockClientResponse())
    def test_if_api_token_is_missing_fetch_a_new_one(self, mock_http_client):
        api = Api(url='http://localhost')
        api.authenticate = MagicMock(return_value='mytoken')

        self.assertEquals(api.api_token, 'mytoken')
        api.authenticate.assert_called_once_with()

    @patch('conjur_api_python3.api.invoke_endpoint', return_value=MockClientResponse())
    def test_if_api_token_is_not_expired_dont_fetch_new_one(self, mock_http_client):
        api = Api(url='http://localhost')
        api.authenticate = MagicMock(return_value='mytoken')

        token = api.api_token
        api.authenticate = MagicMock(return_value='newtoken')

        self.assertEquals(api.api_token, 'mytoken')

    @patch('conjur_api_python3.api.invoke_endpoint', return_value=MockClientResponse())
    def test_if_api_token_is_expired_fetch_new_one(self, mock_http_client):
        api = Api(url='http://localhost')
        api.authenticate = MagicMock(return_value='mytoken')

        api.api_token
        api.api_token_expiration = datetime.now()

        api.authenticate = MagicMock(return_value='newtoken')

        self.assertEquals(api.api_token, 'newtoken')

    @patch('conjur_api_python3.api.invoke_endpoint', return_value=MockClientResponse())
    def test_authenticate_invokes_http_client_correctly(self, mock_http_client):
        Api(url='http://localhost', login_id='mylogin', api_key='apikey').authenticate()

        mock_http_client.assert_called_once_with(HttpVerb.POST,
                                                 ConjurEndpoint.AUTHENTICATE,
                                                 {
                                                     'url': 'http://localhost',
                                                     'login': 'mylogin',
                                                     'account': 'default',
                                                 },
                                                 'apikey',
                                                 ssl_verify=True)

    @patch('conjur_api_python3.api.invoke_endpoint', return_value=MockClientResponse())
    def test_authenticate_passes_down_ssl_verify_param(self, mock_http_client):
        Api(url='http://localhost', login_id='mylogin', api_key='apikey',
            ssl_verify='verify').authenticate()

        mock_http_client.assert_called_once_with(HttpVerb.POST,
                                                 ConjurEndpoint.AUTHENTICATE,
                                                 {
                                                     'url': 'http://localhost',
                                                     'login': 'mylogin',
                                                     'account': 'default',
                                                 },
                                                 'apikey',
                                                 ssl_verify='verify')

    @patch('conjur_api_python3.api.invoke_endpoint', return_value=MockClientResponse())
    def test_get_variable_invokes_http_client_correctly(self, mock_http_client):
        api = Api(url='http://localhost', login_id='mylogin', api_key='apikey')
        def mock_auth():
            return 'apitoken'
        api.authenticate = mock_auth

        api.get_variable('myvar')

        mock_http_client.assert_called_once_with(HttpVerb.GET,
                                                 ConjurEndpoint.SECRETS,
                                                 {
                                                     'url': 'http://localhost',
                                                     'kind': 'variable',
                                                     'identifier': 'myvar',
                                                     'account': 'default',
                                                 },
                                                 api_token='apitoken',
                                                 ssl_verify=True)

    @patch('conjur_api_python3.api.invoke_endpoint', return_value=MockClientResponse())
    def test_get_variable_passes_down_ssl_verify_param(self, mock_http_client):
        api = Api(url='http://localhost', login_id='mylogin', api_key='apikey',
                  ssl_verify='verify')
        def mock_auth():
            return 'apitoken'
        api.authenticate = mock_auth

        api.get_variable('myvar')

        mock_http_client.assert_called_once_with(HttpVerb.GET,
                                                 ConjurEndpoint.SECRETS,
                                                 {
                                                     'url': 'http://localhost',
                                                     'kind': 'variable',
                                                     'identifier': 'myvar',
                                                     'account': 'default',
                                                 },
                                                 api_token='apitoken',
                                                 ssl_verify='verify')

    @patch('conjur_api_python3.api.invoke_endpoint', return_value=MockClientResponse())
    def test_set_variable_invokes_http_client_correctly(self, mock_http_client):
        api = Api(url='http://localhost', login_id='mylogin', api_key='apikey')
        def mock_auth():
            return 'apitoken'
        api.authenticate = mock_auth

        api.set_variable('myvar', 'myvalue')

        mock_http_client.assert_called_once_with(HttpVerb.POST,
                                                 ConjurEndpoint.SECRETS,
                                                 {
                                                     'url': 'http://localhost',
                                                     'kind': 'variable',
                                                     'identifier': 'myvar',
                                                     'account': 'default',
                                                 },
                                                 'myvalue',
                                                 api_token='apitoken',
                                                 ssl_verify=True)

    @patch('conjur_api_python3.api.invoke_endpoint', return_value=MockClientResponse())
    def test_set_variable_passes_down_ssl_verify_param(self, mock_http_client):
        api = Api(url='http://localhost', login_id='mylogin', api_key='apikey',
                  ssl_verify='verify')
        def mock_auth():
            return 'apitoken'
        api.authenticate = mock_auth

        api.set_variable('myvar', 'myvalue')

        mock_http_client.assert_called_once_with(HttpVerb.POST,
                                                 ConjurEndpoint.SECRETS,
                                                 {
                                                     'url': 'http://localhost',
                                                     'kind': 'variable',
                                                     'identifier': 'myvar',
                                                     'account': 'default',
                                                 },
                                                 'myvalue',
                                                 api_token='apitoken',
                                                 ssl_verify='verify')
