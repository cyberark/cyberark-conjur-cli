import os
import unittest

from unittest.mock import MagicMock, Mock, patch

from conjur_api_python3.client import ConfigException, Client
from conjur_api_python3 import api

class ClientTest(unittest.TestCase):
    def test_config_exception_wrapper_exists(self):
        with self.assertRaises(ConfigException):
            raise ConfigException('abc')

    def test_client_throws_error_when_no_config(self):
        with self.assertRaises(ConfigException):
            Client()

    def test_client_passes_url_and_account_to_api_initializer(self):
        class MockApi(object):
            def __init__(*args, **kwargs):
                self.assertEquals(kwargs['url'], 'http://foo')
                self.assertEquals(kwargs['account'], 'foo')
                self.assertEquals(kwargs['ca_bundle'], None)

            def login(*args):
                pass

        Client(api_class=MockApi, url='http://foo', account='foo', login_id='bar', password='baz')

    def test_client_passes_ca_bundle_to_api_initializer_if_provided(self):
        class MockApi(object):
            def __init__(*args, **kwargs):
                self.assertEquals(kwargs['ca_bundle'], 'bundle_path')

            def login(*args):
                pass

        Client(api_class=MockApi, url='http://foo', ca_bundle='bundle_path',
                account='foo', login_id='bar', password='baz')

    def test_client_performs_api_login_if_password_is_provided(self):
        class MockApi(object):
            def __init__(*args, **kwargs):
                pass
        MockApi.login = MagicMock()

        Client(api_class=MockApi, url='http://foo', ca_bundle='bundle_path',
                account='foo', login_id='login id', password='login password')

        MockApi.login.assert_called_once_with('login id', 'login password')

    @unittest.skip("Skipped until ApiConfig is mocked")
    def test_client_performs_no_api_login_if_password_is_not_provided(self):
        class MockApi(object):
            def __init__(*args, **kwargs):
                pass
        MockApi.login = MagicMock()

        Client(api_class=MockApi, url='http://foo', ca_bundle='bundle_path',
                account='foo', login_id='login id')

        MockApi.login.assert_not_called()
