import logging
import netrc
import unittest
import uuid
from unittest.mock import patch, MagicMock

from conjur.api.client import ConfigException, Client

# CredentialsFromFile mocked class
from conjur.errors import OperationNotCompletedException

MockCredentials = {
    'login_id': 'apiconfigloginid',
    'api_key': 'apiconfigapikey',
}

# ApiConfig mocking class
class MockApiConfig(object):
    CONFIG = {
        'key1': 'value1',
        'key2': 'value2',

        'url': 'apiconfigurl',
        'account': 'apiconfigaccount',
        'ca_bundle': 'apiconfigcabundle',
    }

    def __iter__(self):
        return iter(self.CONFIG.items())

# ApiConfig mocking class
class MockApiConfigNoCert(object):
    CONFIG = {
        'key1': 'value1',
        'key2': 'value2',

        'url': 'apiconfigurl',
        'account': 'apiconfigaccount',
        'ca_bundle': '',
    }

    def __iter__(self):
        return iter(self.CONFIG.items())


class MOCK_RESOURCE:
    type = "sometype"
    name = "somename"


class MissingMockApiConfig(object):
    def __init__(self):
        raise FileNotFoundError("oops!")


class ConfigErrorTest(unittest.TestCase):
    def test_config_exception_wrapper_exists(self):
        with self.assertRaises(ConfigException):
            raise ConfigException('abc')


class ClientTest(unittest.TestCase):
    # To run properly, we need to configure the loaded conjurrc

    ### Init configuration tests ###

    @patch('conjur.api.client.ApiConfig', new=MissingMockApiConfig)
    def test_client_throws_error_when_no_config(self):
        with self.assertRaises(ConfigException):
            Client()

    @patch('conjur.api.client.Api')
    @patch('logging.basicConfig')
    def test_client_initializes_logging(self, mock_logging, mock_api):
        Client(url='http://myurl', account='myacct', login_id='mylogin',
               password='mypass')

        mock_logging.assert_called_once_with(format=Client.LOGGING_FORMAT, level=logging.WARNING)

    @patch('conjur.api.client.Api')
    @patch('logging.basicConfig')
    def test_client_increases_logging_with_debug_flag(self, mock_logging, mock_api):
        Client(url='http://myurl', account='myacct', login_id='mylogin',
               password='mypass', debug=True)

        mock_logging.assert_called_once_with(format=Client.LOGGING_FORMAT, level=logging.DEBUG)

    @patch('conjur.api.client.Api')
    def test_client_passes_init_config_params_to_api_initializer(self, mock_api_instance):
        Client(url='http://myurl', account='myacct', login_id='mylogin',
               password='mypass', ca_bundle="mybundle", ssl_verify=False)

        mock_api_instance.assert_called_with(
            account='myacct',
            ca_bundle='mybundle',
            http_debug=False,
            ssl_verify=False,
            url='http://myurl',
        )

    @patch('conjur.api.Api')
    @patch('conjur.util.credentials_from_file.CredentialsFromFile.load', side_effect=netrc.NetrcParseError(''))
    def test_client_can_raise_netrc_exception_error(self, mock_cred, mock_api_instance):
        with self.assertRaises(Exception):
            Client(url='https://myurl', account='myacct', login_id='mylogin', ca_bundle="mybundle", ssl_verify=False)

    @patch('conjur.api.client.ApiConfig', return_value=MockApiConfigNoCert())
    def test_client_can_raise_incomplete_operation_error_if_ssl_modes_are_conflicting(self, mock_config):
        with self.assertRaises(OperationNotCompletedException):
            Client(ssl_verify=True)

    @patch('conjur.api.client.Api')
    def test_client_passes_default_account_to_api_initializer_if_none_is_provided(self, mock_api_instance):
        Client(url='http://myurl', login_id='mylogin', password='mypass',
               ca_bundle="mybundle")

        mock_api_instance.assert_called_with(
            account='default',
            ca_bundle='mybundle',
            http_debug=False,
            ssl_verify=True,
            url='http://myurl',
        )

    @patch('conjur.api.client.Api')
    def test_client_performs_password_api_login_if_password_is_provided(self, mock_api_instance):
        Client(url='http://foo', account='myacct', login_id='mylogin',
               password='mypass')

        mock_api_instance.return_value.login.assert_called_once_with('mylogin', 'mypass')

    @patch('conjur.api.client.Api')
    def test_client_initializes_client_with_api_key_if_its_provided(self, mock_api_instance):
        Client(url='http://foo', account='myacct', login_id='mylogin',
               api_key='someapikey')

        mock_api_instance.assert_called_with(
            account='myacct',
            api_key='someapikey',
            ca_bundle=None,
            http_debug=False,
            login_id='mylogin',
            ssl_verify=True,
            url='http://foo',
        )

    @patch('conjur.api.client.ApiConfig', return_value=MockApiConfig())
    @patch('conjur.util.credentials_from_file.CredentialsFromFile.load', return_value=MockCredentials)
    @patch('conjur.api.client.Api')
    def test_client_performs_no_api_login_if_password_is_not_provided(self, mock_api_instance, mock_creds,
                                                                      mock_api_config):
        Client(url='http://foo', account='myacct', login_id='mylogin')

        mock_api_instance.return_value.login.assert_not_called()

    @patch('conjur.api.client.ApiConfig', return_value=MockApiConfig())
    @patch('conjur.util.credentials_from_file.CredentialsFromFile.load', return_value=MockCredentials)
    @patch('conjur.api.client.Api')
    def test_client_passes_config_from_apiconfig_if_url_is_not_provided(self, mock_api_instance, mock_creds,
                                                                        mock_api_config):
        Client(account='myacct', login_id='mylogin', password="mypass")

        mock_api_instance.assert_called_with(
            account='myacct',
            ca_bundle='apiconfigcabundle',
            http_debug=False,
            key1='value1',
            key2='value2',
            ssl_verify=True,
            url='apiconfigurl',
        )

    @patch('conjur.api.client.Api')
    def test_client_does_not_pass_config_from_apiconfig_if_only_account_is_empty(
            self, mock_api_instance):
        Client(url='http://foo', login_id='mylogin', password="mypass")

        mock_api_instance.assert_called_with(
            account='default',
            ca_bundle=None,
            http_debug=False,
            ssl_verify=True,
            url='http://foo',
        )

        mock_api_instance.return_value.login.assert_called_once_with('mylogin', 'mypass')

    @patch('conjur.api.client.ApiConfig', return_value=MockApiConfig())
    @patch('conjur.util.credentials_from_file.CredentialsFromFile.load', return_value=MockCredentials)
    @patch('conjur.api.client.Api')
    def test_client_passes_config_from_apiconfig_if_login_id_is_not_provided(self, mock_api_instance, mock_creds,
                                                                             mock_api_config):
        Client(url='http://foo', account='myacct', password="mypass")

        mock_api_instance.assert_called_with(
            account='myacct',
            ca_bundle='apiconfigcabundle',
            http_debug=False,
            key1='value1',
            key2='value2',
            ssl_verify=True,
            url='http://foo',
        )

    @patch('conjur.api.client.ApiConfig', return_value=MockApiConfig())
    @patch('conjur.util.credentials_from_file.CredentialsFromFile.load', return_value=MockCredentials)
    @patch('conjur.api.client.Api')
    def test_client_passes_config_from_apiconfig_if_password_is_not_provided(self, mock_api_instance, mock_creds,
                                                                             mock_api_config):
        Client(url='http://foo', account='myacct', login_id='mylogin')

        mock_api_instance.assert_called_with(
            account='myacct',
            api_key='apiconfigapikey',
            ca_bundle='apiconfigcabundle',
            http_debug=False,
            key1='value1',
            key2='value2',
            login_id='apiconfigloginid',
            ssl_verify=True,
            url='http://foo',
        )

    @patch('conjur.api.client.ApiConfig', return_value=MockApiConfig())
    @patch('conjur.util.credentials_from_file.CredentialsFromFile.load', return_value=MockCredentials)
    @patch('conjur.api.client.Api')
    def test_client_overrides_apiconfig_value_with_explicitly_provided_ones(self, mock_api_instance, mock_creds,
                                                                            mock_api_config):
        Client(url='http://foo', account='myacct', login_id='mylogin',
               ca_bundle='mybundle')

        mock_api_instance.assert_called_with(
            account='myacct',
            api_key='apiconfigapikey',
            ca_bundle='mybundle',
            http_debug=False,
            key1='value1',
            key2='value2',
            login_id='apiconfigloginid',
            ssl_verify=True,
            url='http://foo',
        )

    @patch('conjur.api.client.ApiConfig', return_value=MockApiConfig())
    @patch('conjur.util.credentials_from_file.CredentialsFromFile.load', return_value=MockCredentials)
    @patch('conjur.api.client.Api')
    def test_client_does_not_override_apiconfig_values_with_empty_values(self, mock_api_instance, mock_creds,
                                                                         mock_api_config):
        Client(url=None, account=None, login_id=None, ca_bundle=None)

        mock_api_instance.assert_called_with(
            account='apiconfigaccount',
            api_key='apiconfigapikey',
            ca_bundle='apiconfigcabundle',
            http_debug=False,
            key1='value1',
            key2='value2',
            login_id='apiconfigloginid',
            ssl_verify=True,
            url='apiconfigurl',
        )

    ### API passthrough tests ###

    @patch('conjur.api.client.Api')
    @patch('conjur.util.credentials_from_file.CredentialsFromFile.load', return_value=MockCredentials)
    @patch('logging.basicConfig')
    def test_client_increases_logging_with_debug_flag(self, mock_logging, mock_creds, mock_api):
        Client(url='http://myurl', account='myacct', login_id='mylogin',
               password='mypass', debug=True)

        mock_logging.assert_called_once_with(format=Client.LOGGING_FORMAT, level=logging.DEBUG)

    @patch('conjur.api.client.ApiConfig', return_value=MockApiConfig())
    @patch('conjur.util.credentials_from_file.CredentialsFromFile.load', return_value=MockCredentials)
    @patch('conjur.api.client.Api')
    def test_client_passes_through_api_get_variable_params(self, mock_api_instance, mock_creds,
                                                           mock_api_config):
        Client().get('variable_id')

        mock_api_instance.return_value.get_variable.assert_called_once_with('variable_id', None)

    @patch('conjur.api.client.ApiConfig', return_value=MockApiConfig())
    @patch('conjur.util.credentials_from_file.CredentialsFromFile.load', return_value=MockCredentials)
    @patch('conjur.api.client.Api')
    def test_client_returns_get_variable_result(self, mock_api_instance, mock_creds,
                                                mock_api_config):
        variable_value = uuid.uuid4().hex
        mock_api_instance.return_value.get_variable.return_value = variable_value

        return_value = Client().get('variable_id')
        self.assertEquals(return_value, variable_value)

    @patch('conjur.api.client.ApiConfig', return_value=MockApiConfig())
    @patch('conjur.util.credentials_from_file.CredentialsFromFile.load', return_value=MockCredentials)
    @patch('conjur.api.client.Api')
    def test_client_passes_through_api_get_many_variables_params(self, mock_api_instance, mock_creds,
                                                                 mock_api_config):
        Client().get_many('variable_id', 'variable_id2')

        mock_api_instance.return_value.get_variables.assert_called_once_with(
            'variable_id',
            'variable_id2'
        )

    @patch('conjur.api.client.ApiConfig', return_value=MockApiConfig())
    @patch('conjur.util.credentials_from_file.CredentialsFromFile.load', return_value=MockCredentials)
    @patch('conjur.api.client.Api')
    def test_client_returns_get_variables_result(self, mock_api_instance, mock_creds,
                                                 mock_api_config):
        variable_values = uuid.uuid4().hex
        mock_api_instance.return_value.get_variables.return_value = variable_values

        return_value = Client().get_many('variable_id', 'variable_id2')
        self.assertEquals(return_value, variable_values)

    @patch('conjur.api.client.ApiConfig', return_value=MockApiConfig())
    @patch('conjur.util.credentials_from_file.CredentialsFromFile.load', return_value=MockCredentials)
    @patch('conjur.api.client.Api')
    def test_client_passes_through_api_set_variable_params(self, mock_api_instance, mock_creds,
                                                           mock_api_config):
        Client().set('variable_id', 'variable_value')

        mock_api_instance.return_value.set_variable.assert_called_once_with(
            'variable_id',
            'variable_value',
        )

    @patch('conjur.api.client.ApiConfig', return_value=MockApiConfig())
    @patch('conjur.util.credentials_from_file.CredentialsFromFile.load', return_value=MockCredentials)
    @patch('conjur.api.client.Api')
    def test_client_passes_through_api_load_policy_params(self, mock_api_instance, mock_creds,
                                                          mock_api_config):
        Client().load_policy_file('name', 'policy')

        mock_api_instance.return_value.load_policy_file.assert_called_once_with(
            'name',
            'policy',
        )

    @patch('conjur.api.client.ApiConfig', return_value=MockApiConfig())
    @patch('conjur.util.credentials_from_file.CredentialsFromFile.load', return_value=MockCredentials)
    @patch('conjur.api.client.Api')
    def test_client_returns_load_policy_result(self, mock_api_instance, mock_creds, mock_api_config):
        load_policy_result = uuid.uuid4().hex
        mock_api_instance.return_value.load_policy_file.return_value = load_policy_result

        return_value = Client().load_policy_file('name', 'policy')
        self.assertEquals(return_value, load_policy_result)

    @patch('conjur.api.client.ApiConfig', return_value=MockApiConfig())
    @patch('conjur.util.credentials_from_file.CredentialsFromFile.load', return_value=MockCredentials)
    @patch('conjur.api.client.Api')
    def test_client_passes_through_api_replace_policy_params(self, mock_api_instance, mock_creds,
                                                             mock_api_config):
        Client().replace_policy_file('name', 'policy')

        mock_api_instance.return_value.replace_policy_file.assert_called_once_with(
            'name',
            'policy'
        )

    @patch('conjur.api.client.ApiConfig', return_value=MockApiConfig())
    @patch('conjur.util.credentials_from_file.CredentialsFromFile.load', return_value=MockCredentials)
    @patch('conjur.api.client.Api')
    def test_client_returns_replace_policy_result(self, mock_api_instance, mock_creds,
                                                  mock_api_config):
        replace_policy_result = uuid.uuid4().hex
        mock_api_instance.return_value.replace_policy_file.return_value = replace_policy_result

        return_value = Client().replace_policy_file('name', 'policy')
        self.assertEquals(return_value, replace_policy_result)

    @patch('conjur.api.client.ApiConfig', return_value=MockApiConfig())
    @patch('conjur.util.credentials_from_file.CredentialsFromFile.load', return_value=MockCredentials)
    @patch('conjur.api.client.Api')
    def test_client_passes_through_api_update_policy_params(self, mock_api_instance, mock_creds,
                                                            mock_api_config):
        Client().update_policy_file('name', 'policy')

        mock_api_instance.return_value.update_policy_file.assert_called_once_with(
            'name',
            'policy'
        )

    @patch('conjur.api.client.ApiConfig', return_value=MockApiConfig())
    @patch('conjur.util.credentials_from_file.CredentialsFromFile.load', return_value=MockCredentials)
    @patch('conjur.api.client.Api')
    def test_client_returns_update_policy_result(self, mock_api_instance, mock_creds,
                                                 mock_api_config):
        update_policy_result = uuid.uuid4().hex
        mock_api_instance.return_value.update_policy_file.return_value = update_policy_result

        return_value = Client().update_policy_file('name', 'policy')
        self.assertEquals(return_value, update_policy_result)

    @patch('conjur.api.client.ApiConfig', return_value=MockApiConfig())
    @patch('conjur.util.credentials_from_file.CredentialsFromFile.load', return_value=MockCredentials)
    @patch('conjur.api.client.Api')
    def test_client_passes_through_resource_list_method(self, mock_api_instance, mock_creds,
                                                        mock_api_config):
        Client().list({})

        mock_api_instance.return_value.resources_list.assert_called_once_with({})

    @patch('conjur.api.client.ApiConfig', return_value=MockApiConfig())
    @patch('conjur.util.credentials_from_file.CredentialsFromFile.load', return_value=MockCredentials)
    @patch('conjur.api.client.Api')
    def test_client_passes_through_whoami_method(self, mock_api_instance, mock_creds,
                                                 mock_api_config):
        Client().whoami()

        mock_api_instance.return_value.whoami.assert_called_once_with()

    @patch('conjur.api.client.ApiConfig', return_value=MockApiConfig())
    @patch('conjur.util.credentials_from_file.CredentialsFromFile.load', return_value=MockCredentials)
    @patch('conjur.api.client.Api')
    def test_client_passes_through_api_rotate_other_api_key_params(self, mock_api_instance, mock_creds,
                                                                   mock_api_config):
        Client().rotate_other_api_key(MOCK_RESOURCE)

        mock_api_instance.return_value.rotate_other_api_key.assert_called_once_with(MOCK_RESOURCE)

    @patch('conjur.api.client.ApiConfig', return_value=MockApiConfig())
    @patch('conjur.util.credentials_from_file.CredentialsFromFile.load', return_value=MockCredentials)
    @patch('conjur.api.client.Api')
    def test_client_passes_through_api_rotate_personal_api_key_params(self, mock_api_instance, mock_creds,
                                                                      mock_api_config):
        Client().rotate_personal_api_key("someloggedinuser", "somecurrentpassword")

        mock_api_instance.return_value.rotate_personal_api_key.assert_called_once_with("someloggedinuser",
                                                                                       "somecurrentpassword")

    @patch('conjur.api.client.ApiConfig', return_value=MockApiConfig())
    @patch('conjur.util.credentials_from_file.CredentialsFromFile.load', return_value=MockCredentials)
    @patch('conjur.api.client.Api')
    def test_client_passes_through_api_change_password_params(self, mock_api_instance, mock_creds,
                                                              mock_api_config):
        Client().change_personal_password("someloggedinuser", "somecurrentpassword", "somenewpassword")

        mock_api_instance.return_value.change_personal_password.assert_called_once_with("someloggedinuser",
                                                                                        "somecurrentpassword",
                                                                                        "somenewpassword")
