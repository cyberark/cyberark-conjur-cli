import os
import unittest
import uuid

from unittest.mock import MagicMock, Mock, patch

from conjur.client import ConfigException, Client
from conjur import api


# ApiConfig mocking class
class MockApiConfig(object):
    CONFIG = {
        'key1': 'value1',
        'key2': 'value2',

        'url': 'apiconfigurl',
        'account': 'apiconfigaccount',
        'ca_bundle': 'apiconfigcabundle',
        'login_id': 'apiconfigloginid',
        'api_key': 'apiconfigapikey',
    }

    def __iter__(self):
        return iter(self.CONFIG.items())

class MissingMockApiConfig(object):
    def __init__(self):
        raise FileNotFoundError("oops!")


# Api mocking class
class MockApiHelper(object):
    def __init__(self, **kwargs):
        self.verify_init_args(**kwargs)

    def login(self, username, password):
        pass

    def verify_init_args(self, **kwargs):
        pass

    def verify_apiconfig_dict_in(self, test_instance, **kwargs):
        test_instance.assertEquals(kwargs['key1'], 'value1')
        test_instance.assertEquals(kwargs['key2'], 'value2')


class ClientTest(unittest.TestCase):
    def test_config_exception_wrapper_exists(self):
        with self.assertRaises(ConfigException):
            raise ConfigException('abc')

    def test_client_throws_error_when_no_config(self):
        with self.assertRaises(ConfigException):
            Client(api_config_class=MissingMockApiConfig)

    def test_client_passes_init_config_params_to_api_initializer(self):
        class MockApi(MockApiHelper):
            def verify_init_args(api_instance, **kwargs):
                self.assertEquals(kwargs['url'], 'http://myurl')
                self.assertEquals(kwargs['account'], 'myacct')
                self.assertEquals(kwargs['ca_bundle'], 'mybundle')
                self.assertEquals(kwargs['ssl_verify'], False)

        Client(api_class=MockApi, url='http://myurl', account='myacct', login_id='mylogin',
               password='mypass', ca_bundle="mybundle", ssl_verify=False)

    def test_client_passes_default_account_to_api_initializer_if_none_is_provided(self):
        class MockApi(MockApiHelper):
            def verify_init_args(api_instance, **kwargs):
                self.assertEquals(kwargs['url'], 'http://myurl')
                self.assertEquals(kwargs['account'], 'default')
                self.assertEquals(kwargs['ca_bundle'], 'mybundle')

        Client(api_class=MockApi, url='http://myurl', login_id='mylogin',
               password='mypass', ca_bundle="mybundle")

    def test_client_performs_password_api_login_if_password_is_provided(self):
        class MockApi(MockApiHelper):
            pass
        MockApi.login = MagicMock()

        Client(api_class=MockApi, url='http://foo', account='myacct', login_id='mylogin',
               password='mypass')

        MockApi.login.assert_called_once_with('mylogin', 'mypass')

    def test_client_initializes_client_with_api_key_if_its_provided(self):
        class MockApi(MockApiHelper):
            def verify_init_args(api_instance, **kwargs):
                self.assertEqual(kwargs['account'], 'myacct')
                self.assertEqual(kwargs['url'], 'http://foo')
                self.assertEqual(kwargs['login_id'], 'mylogin')
                self.assertEqual(kwargs['api_key'], 'someapikey')

        Client(api_class=MockApi, url='http://foo', account='myacct', login_id='mylogin',
               api_key='someapikey')

    def test_client_performs_no_api_login_if_password_is_not_provided(self):
        class MockApi(MockApiHelper):
            pass
        MockApi.login = MagicMock()

        Client(api_class=MockApi, api_config_class=MockApiConfig, url='http://foo',
               account='myacct', login_id='mylogin')

        MockApi.login.assert_not_called()

    def test_client_passes_config_from_apiconfig_if_url_is_not_provided(self):
        class MockApi(MockApiHelper):
            def verify_init_args(api_instance, **kwargs):
                api_instance.verify_apiconfig_dict_in(self, **kwargs)

        Client(api_class=MockApi, api_config_class=MockApiConfig,
               account='myacct', login_id='mylogin', password="mypass")

    def test_client_passes_config_from_apiconfig_if_account_is_empty(self):
        class MockApi(MockApiHelper):
            def verify_init_args(api_instance, **kwargs):
                api_instance.verify_apiconfig_dict_in(self, **kwargs)

        Client(api_class=MockApi, api_config_class=MockApiConfig, url='http://foo',
               account=None, login_id='mylogin', password="mypass")

    def test_client_passes_config_from_apiconfig_if_login_id_is_not_provided(self):
        class MockApi(MockApiHelper):
            def verify_init_args(api_instance, **kwargs):
                api_instance.verify_apiconfig_dict_in(self, **kwargs)

        Client(api_class=MockApi, api_config_class=MockApiConfig, url='http://foo',
               account='myacct', password="mypass")

    def test_client_passes_config_from_apiconfig_if_password_is_not_provided(self):
        class MockApi(MockApiHelper):
            def verify_init_args(api_instance, **kwargs):
                api_instance.verify_apiconfig_dict_in(self, **kwargs)

        Client(api_class=MockApi, api_config_class=MockApiConfig, url='http://foo',
               account='myacct', login_id='mylogin')

    def test_client_overrides_apiconfig_value_with_explicitly_provided_ones(self):
        class MockApi(MockApiHelper):
            def verify_init_args(api_instance, **kwargs):
                api_instance.verify_apiconfig_dict_in(self, **kwargs)
                self.assertEqual(kwargs['account'], 'myacct')
                self.assertEqual(kwargs['url'], 'http://foo')
                self.assertEqual(kwargs['ca_bundle'], 'mybundle')

        Client(api_class=MockApi, api_config_class=MockApiConfig, url='http://foo',
               account='myacct', login_id='mylogin', ca_bundle='mybundle')

    def test_client_does_not_override_apiconfig_values_with_empty_values(self):
        class MockApi(MockApiHelper):
            def verify_init_args(api_instance, **kwargs):
                api_instance.verify_apiconfig_dict_in(self, **kwargs)
                self.assertEqual(kwargs['account'], 'apiconfigaccount')
                self.assertEqual(kwargs['url'], 'apiconfigurl')
                self.assertEqual(kwargs['ca_bundle'], 'apiconfigcabundle')
                self.assertEqual(kwargs['login_id'], 'apiconfigloginid')
                self.assertEqual(kwargs['api_key'], 'apiconfigapikey')

        Client(api_class=MockApi, api_config_class=MockApiConfig, url=None,
               account=None, login_id=None, ca_bundle=None)


    ### API passthrough tests ###

    def test_client_passes_through_api_get_variable_params(self):
        class MockApi(MockApiHelper):
            pass
        MockApi.get_variable = MagicMock()

        Client(api_class=MockApi, api_config_class=MockApiConfig).get('variable_id')

        MockApi.get_variable.assert_called_once_with('variable_id')

    def test_client_returns_get_variable_result(self):
        class MockApi(MockApiHelper):
            pass

        MockApi.get_variable = MagicMock()
        MockApi.get_variable.return_value = uuid.uuid4().hex

        return_value = Client(api_class=MockApi, api_config_class=MockApiConfig).get('variable_id')
        self.assertEquals(return_value, MockApi.get_variable.return_value)

    def test_client_passes_through_api_get_many_variables_params(self):
        class MockApi(MockApiHelper):
            pass
        MockApi.get_variables = MagicMock()

        Client(api_class=MockApi, api_config_class=MockApiConfig).get_many('variable_id', 'variable_id2')

        MockApi.get_variables.assert_called_once_with('variable_id', 'variable_id2')

    def test_client_returns_get_variables_result(self):
        class MockApi(MockApiHelper):
            pass

        MockApi.get_variables = MagicMock()
        MockApi.get_variables.return_value = uuid.uuid4().hex

        return_value = Client(api_class=MockApi, api_config_class=MockApiConfig).get_many('variable_id', 'variable_id2')
        self.assertEquals(return_value, MockApi.get_variables.return_value)

    def test_client_passes_through_api_set_variable_params(self):
        class MockApi(MockApiHelper):
            pass
        MockApi.set_variable = MagicMock()

        Client(api_class=MockApi, api_config_class=MockApiConfig).set('variable_id', 'variable_value')

        MockApi.set_variable.assert_called_once_with('variable_id', 'variable_value')

    def test_client_passes_through_api_apply_policy_params(self):
        class MockApi(MockApiHelper):
            pass
        MockApi.apply_policy_file = MagicMock()

        Client(api_class=MockApi, api_config_class=MockApiConfig).apply_policy_file('name', 'policy')

        MockApi.apply_policy_file.assert_called_once_with('name', 'policy')

    def test_client_returns_apply_policy_result(self):
        class MockApi(MockApiHelper):
            pass

        MockApi.apply_policy_file = MagicMock()
        MockApi.apply_policy_file.return_value = uuid.uuid4().hex

        return_value = Client(api_class=MockApi, api_config_class=MockApiConfig).apply_policy_file('name', 'policy')
        self.assertEquals(return_value, MockApi.apply_policy_file.return_value)

    def test_client_passes_through_api_replace_policy_params(self):
        class MockApi(MockApiHelper):
            pass
        MockApi.replace_policy_file = MagicMock()

        Client(api_class=MockApi, api_config_class=MockApiConfig).replace_policy_file('name', 'policy')

        MockApi.replace_policy_file.assert_called_once_with('name', 'policy')

    def test_client_returns_replace_policy_result(self):
        class MockApi(MockApiHelper):
            pass

        MockApi.replace_policy_file = MagicMock()
        MockApi.replace_policy_file.return_value = uuid.uuid4().hex

        return_value = Client(api_class=MockApi, api_config_class=MockApiConfig).replace_policy_file('name', 'policy')
        self.assertEquals(return_value, MockApi.replace_policy_file.return_value)

    def test_client_passes_through_resource_list_method(self):
        class MockApi(MockApiHelper):
            pass
        MockApi.list_resources = MagicMock()

        Client(api_class=MockApi, api_config_class=MockApiConfig).list()

        MockApi.list_resources.assert_called_once_with()
