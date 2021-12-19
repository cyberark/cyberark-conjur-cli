import logging
import netrc
import unittest
import uuid
from unittest.mock import patch

from conjur.api.client import  Client
from conjur.api.models import SslVerificationMetadata, SslVerificationMode

from conjur.data_object import CredentialsData
from conjur.data_object.create_token_data import CreateTokenData
from conjur.errors import CertificateVerificationException, ConfigurationMissingException
from conjur.data_object.conjurrc_data import ConjurrcData
from conjur.logic.credential_provider import FileCredentialsProvider

# region api settings
MockCredentialsApi = CredentialsData(login='apiconfigloginid', password='apiconfigapikey')
MockConjurrcApi = ConjurrcData(conjur_url="apiconfigurl",
                               account="apiconfigaccount",
                               cert_file="apiconfigcabundle")
MockSslVerificationMetaDataApi = SslVerificationMetadata(
    mode=SslVerificationMode.WITH_CA_BUNDLE,
    ca_cert_path="apiconfigcabundle")
# endregion

# region regular settings
MockCredentials = CredentialsData(login='mylogin', password='someapikey')
MockConjurrc = ConjurrcData(conjur_url="http://foo",
                            account="myacct",
                            cert_file=None)
MockSslVerificationMetaData = SslVerificationMetadata(
    mode=SslVerificationMode.WITH_TRUST_STORE)


# endregion

def create_client(api_format=False, debug=True):
    if api_format:
        return Client(conjurrc_data=MockConjurrcApi,
                      ssl_verification_mode=MockSslVerificationMetaDataApi.mode,
                      credentials_provider=FileCredentialsProvider(),
                      debug=debug)
    return Client(conjurrc_data=MockConjurrc,
                  ssl_verification_mode=MockSslVerificationMetaData.mode,
                  credentials_provider=FileCredentialsProvider(),
                  debug=debug)


class MOCK_RESOURCE:
    type = "sometype"
    name = "somename"


class ConfigErrorTest(unittest.TestCase):
    def test_config_exception_wrapper_exists(self):
        with self.assertRaises(ConfigurationMissingException):
            raise ConfigurationMissingException


class ClientTest(unittest.TestCase):
    # To run properly, we need to configure the loaded conjurrc

    ### Init configuration tests ###
    @patch('conjur.wrapper.keystore_wrapper.KeystoreWrapper.is_keyring_accessible',
           return_value=False)
    @patch('conjur.logic.credential_provider.FileCredentialsProvider.load',
           return_value=MockCredentials)
    @patch('conjur.api.client.Api')
    @patch('logging.basicConfig')
    def test_client_initializes_logging(self, mock_logging, mock_api, mock_creds, mock):
        create_client(debug=False)

        mock_logging.assert_called_once_with(format=Client.LOGGING_FORMAT_WARNING,
                                             level=logging.WARNING)

    @patch('conjur.api.client.Api')
    @patch('logging.basicConfig')
    def test_client_increases_logging_with_debug_flag(self, mock_logging, mock_api):
        create_client()

        mock_logging.assert_called_once_with(format=Client.LOGGING_FORMAT, level=logging.DEBUG)

    @patch('conjur.api.Api')
    @patch('conjur.logic.credential_provider.FileCredentialsProvider.load',
           side_effect=netrc.NetrcParseError(''))
    def test_client_can_raise_netrc_exception_error(self, mock_cred, mock_api_instance):
        with self.assertRaises(Exception):
            create_client().list()

    ### API passthrough tests ###

    @patch('conjur.api.client.Api')
    @patch('conjur.logic.credential_provider.FileCredentialsProvider.load',
           return_value=MockCredentialsApi)
    @patch('logging.basicConfig')
    def test_client_increases_logging_with_debug_flag(self, mock_logging, mock_creds, mock_api):
        Client(conjurrc_data=MockConjurrcApi,
               ssl_verification_mode=MockSslVerificationMetaDataApi.mode,
               credentials_provider=FileCredentialsProvider(),
               debug=True)

        mock_logging.assert_called_once_with(format=Client.LOGGING_FORMAT, level=logging.DEBUG)

    @patch('conjur.wrapper.keystore_wrapper.KeystoreWrapper.is_keyring_accessible',
           return_value=False)
    @patch('conjur.data_object.conjurrc_data.ConjurrcData.load_from_file',
           return_value=MockConjurrcApi)
    @patch('conjur.logic.credential_provider.FileCredentialsProvider.load',
           return_value=MockCredentialsApi)
    @patch('conjur.api.client.Api')
    def test_client_passes_through_api_get_variable_params(
            self, mock_api_instance, mock_creds, mock_conjurrc, mock_accessible):
        create_client().get('variable_id')

        mock_api_instance.return_value.get_variable.assert_called_once_with('variable_id', None)

    @patch('conjur.wrapper.keystore_wrapper.KeystoreWrapper.is_keyring_accessible',
           return_value=False)
    @patch('conjur.data_object.conjurrc_data.ConjurrcData.load_from_file',
           return_value=MockConjurrcApi)
    @patch('conjur.data_object.conjurrc_data.ConjurrcData.load_from_file',
           return_value=MockConjurrcApi)
    @patch('conjur.logic.credential_provider.FileCredentialsProvider.load',
           return_value=MockCredentialsApi)
    @patch('conjur.api.client.Api')
    def test_client_returns_get_variable_result(
            self, mock_api_instance, mock_creds, mock_conjurrc,
            mock_api_config, mock_accessible):
        variable_value = uuid.uuid4().hex
        mock_api_instance.return_value.get_variable.return_value = variable_value

        return_value = create_client().get('variable_id')
        self.assertEquals(return_value, variable_value)

    @patch('conjur.wrapper.keystore_wrapper.KeystoreWrapper.is_keyring_accessible',
           return_value=False)
    @patch('conjur.data_object.conjurrc_data.ConjurrcData.load_from_file',
           return_value=MockConjurrcApi)
    @patch('conjur.logic.credential_provider.FileCredentialsProvider.load',
           return_value=MockCredentialsApi)
    @patch('conjur.api.client.Api')
    def test_client_passes_through_api_get_many_variables_params(
            self, mock_api_instance, mock_creds,
            mock_api_config, mock_accessible):
        create_client().get_many('variable_id', 'variable_id2')

        mock_api_instance.return_value.get_variables.assert_called_once_with(
            'variable_id',
            'variable_id2'
        )

    @patch('conjur.wrapper.keystore_wrapper.KeystoreWrapper.is_keyring_accessible',
           return_value=False)
    @patch('conjur.data_object.conjurrc_data.ConjurrcData.load_from_file',
           return_value=MockConjurrcApi)
    @patch('conjur.logic.credential_provider.FileCredentialsProvider.load',
           return_value=MockCredentialsApi)
    @patch('conjur.api.client.Api')
    def test_client_returns_get_variables_result(
            self, mock_api_instance, mock_creds,
            mock_api_config, mock_accessible):
        variable_values = uuid.uuid4().hex
        mock_api_instance.return_value.get_variables.return_value = variable_values

        return_value = create_client().get_many('variable_id', 'variable_id2')
        self.assertEquals(return_value, variable_values)

    @patch('conjur.wrapper.keystore_wrapper.KeystoreWrapper.is_keyring_accessible',
           return_value=False)
    @patch('conjur.data_object.conjurrc_data.ConjurrcData.load_from_file',
           return_value=MockConjurrcApi)
    @patch('conjur.logic.credential_provider.FileCredentialsProvider.load',
           return_value=MockCredentialsApi)
    @patch('conjur.api.client.Api')
    def test_client_passes_through_api_set_variable_params(
            self, mock_api_instance, mock_creds,
            mock_api_config, mock_accessible):
        create_client().set('variable_id', 'variable_value')

        mock_api_instance.return_value.set_variable.assert_called_once_with(
            'variable_id',
            'variable_value',
        )

    @patch('conjur.wrapper.keystore_wrapper.KeystoreWrapper.is_keyring_accessible',
           return_value=False)
    @patch('conjur.data_object.conjurrc_data.ConjurrcData.load_from_file',
           return_value=MockConjurrcApi)
    @patch('conjur.logic.credential_provider.FileCredentialsProvider.load',
           return_value=MockCredentialsApi)
    @patch('conjur.api.client.Api')
    def test_client_passes_through_api_load_policy_params(
            self, mock_api_instance, mock_creds,
            mock_api_config, mock_accessible):
        create_client().load_policy_file('name', 'policy')

        mock_api_instance.return_value.load_policy_file.assert_called_once_with(
            'name',
            'policy',
        )

    @patch('conjur.wrapper.keystore_wrapper.KeystoreWrapper.is_keyring_accessible',
           return_value=False)
    @patch('conjur.data_object.conjurrc_data.ConjurrcData.load_from_file',
           return_value=MockConjurrcApi)
    @patch('conjur.logic.credential_provider.FileCredentialsProvider.load',
           return_value=MockCredentialsApi)
    @patch('conjur.api.client.Api')
    def test_client_returns_load_policy_result(
            self, mock_api_instance, mock_creds,
            mock_api_config, mock_accessible):
        load_policy_result = uuid.uuid4().hex
        mock_api_instance.return_value.load_policy_file.return_value = load_policy_result

        return_value = create_client().load_policy_file('name', 'policy')
        self.assertEquals(return_value, load_policy_result)

    @patch('conjur.wrapper.keystore_wrapper.KeystoreWrapper.is_keyring_accessible',
           return_value=False)
    @patch('conjur.data_object.conjurrc_data.ConjurrcData.load_from_file',
           return_value=MockConjurrcApi)
    @patch('conjur.logic.credential_provider.FileCredentialsProvider.load',
           return_value=MockCredentialsApi)
    @patch('conjur.api.client.Api')
    def test_client_passes_through_api_replace_policy_params(
            self, mock_api_instance, mock_creds,
            mock_api_config, mock_accessible):
        create_client().replace_policy_file('name', 'policy')

        mock_api_instance.return_value.replace_policy_file.assert_called_once_with(
            'name',
            'policy'
        )

    @patch('conjur.wrapper.keystore_wrapper.KeystoreWrapper.is_keyring_accessible',
           return_value=False)
    @patch('conjur.data_object.conjurrc_data.ConjurrcData.load_from_file',
           return_value=MockConjurrcApi)
    @patch('conjur.api.client.Api')
    def test_client_returns_replace_policy_result(
            self, mock_api_instance,
            mock_api_config, mock_accessible):
        with patch('conjur.logic.credential_provider.FileCredentialsProvider.load',
                   return_value=MockCredentialsApi):
            replace_policy_result = uuid.uuid4().hex
            mock_api_instance.return_value.replace_policy_file.return_value = replace_policy_result

            return_value = create_client().replace_policy_file('name', 'policy')
            self.assertEquals(return_value, replace_policy_result)

    @patch('conjur.wrapper.keystore_wrapper.KeystoreWrapper.is_keyring_accessible',
           return_value=False)
    @patch('conjur.data_object.conjurrc_data.ConjurrcData.load_from_file',
           return_value=MockConjurrcApi)
    @patch('conjur.logic.credential_provider.FileCredentialsProvider.load',
           return_value=MockCredentialsApi)
    @patch('conjur.api.client.Api')
    def test_client_passes_through_api_update_policy_params(
            self, mock_api_instance, mock_creds,
            mock_api_config, mock_accessible):
        create_client().update_policy_file('name', 'policy')

        mock_api_instance.return_value.update_policy_file.assert_called_once_with(
            'name',
            'policy'
        )

    @patch('conjur.wrapper.keystore_wrapper.KeystoreWrapper.is_keyring_accessible',
           return_value=False)
    @patch('conjur.data_object.conjurrc_data.ConjurrcData.load_from_file',
           return_value=MockConjurrcApi)
    @patch('conjur.logic.credential_provider.FileCredentialsProvider.load',
           return_value=MockCredentialsApi)
    @patch('conjur.api.client.Api')
    def test_client_returns_update_policy_result(
            self, mock_api_instance, mock_creds,
            mock_api_config, mock_accessible):
        update_policy_result = uuid.uuid4().hex
        mock_api_instance.return_value.update_policy_file.return_value = update_policy_result

        return_value = create_client().update_policy_file('name', 'policy')
        self.assertEquals(return_value, update_policy_result)

    @patch('conjur.wrapper.keystore_wrapper.KeystoreWrapper.is_keyring_accessible',
           return_value=False)
    @patch('conjur.data_object.conjurrc_data.ConjurrcData.load_from_file',
           return_value=MockConjurrcApi)
    @patch('conjur.logic.credential_provider.FileCredentialsProvider.load',
           return_value=MockCredentialsApi)
    @patch('conjur.api.client.Api')
    def test_client_passes_through_resource_list_method(
            self, mock_api_instance, mock_creds,
            mock_api_config, mock_accessible):
        create_client().list({})

        mock_api_instance.return_value.resources_list.assert_called_once_with({})

    @patch('conjur.wrapper.keystore_wrapper.KeystoreWrapper.is_keyring_accessible',
           return_value=False)
    @patch('conjur.data_object.conjurrc_data.ConjurrcData.load_from_file',
           return_value=MockConjurrcApi)
    @patch('conjur.logic.credential_provider.FileCredentialsProvider.load',
           return_value=MockCredentialsApi)
    @patch('conjur.api.client.Api')
    def test_client_passes_through_whoami_method(
            self, mock_api_instance, mock_creds,
            mock_api_config, mock_accessible):
        create_client().whoami()

        mock_api_instance.return_value.whoami.assert_called_once_with()

    @patch('conjur.wrapper.keystore_wrapper.KeystoreWrapper.is_keyring_accessible',
           return_value=False)
    @patch('conjur.data_object.conjurrc_data.ConjurrcData.load_from_file',
           return_value=MockConjurrcApi)
    @patch('conjur.logic.credential_provider.FileCredentialsProvider.load',
           return_value=MockCredentialsApi)
    @patch('conjur.api.client.Api')
    def test_client_passes_through_api_rotate_other_api_key_params(
            self, mock_api_instance, mock_creds,
            mock_api_config, mock_accessible):
        create_client().rotate_other_api_key(MOCK_RESOURCE)

        mock_api_instance.return_value.rotate_other_api_key.assert_called_once_with(MOCK_RESOURCE)

    @patch('conjur.wrapper.keystore_wrapper.KeystoreWrapper.is_keyring_accessible',
           return_value=False)
    @patch('conjur.data_object.conjurrc_data.ConjurrcData.load_from_file',
           return_value=MockConjurrcApi)
    @patch('conjur.logic.credential_provider.FileCredentialsProvider.load',
           return_value=MockCredentialsApi)
    @patch('conjur.api.client.Api')
    def test_client_passes_through_api_rotate_personal_api_key_params(
            self, mock_api_instance, mock_creds,
            mock_api_config, mock_accessible):
        create_client().rotate_personal_api_key("someloggedinuser", "somecurrentpassword")

        mock_api_instance.return_value.rotate_personal_api_key.assert_called_once_with(
            "someloggedinuser",
            "somecurrentpassword")

    @patch('conjur.wrapper.keystore_wrapper.KeystoreWrapper.is_keyring_accessible',
           return_value=False)
    @patch('conjur.data_object.conjurrc_data.ConjurrcData.load_from_file',
           return_value=MockConjurrcApi)
    @patch('conjur.logic.credential_provider.FileCredentialsProvider.load',
           return_value=MockCredentialsApi)
    @patch('conjur.api.client.Api')
    def test_client_passes_through_api_change_password_params(
            self, mock_api_instance, mock_creds,
            mock_api_config, mock_accessible):
        create_client().change_personal_password("someloggedinuser", "somecurrentpassword",
                                                 "somenewpassword")

        mock_api_instance.return_value.change_personal_password.assert_called_once_with(
            "someloggedinuser",
            "somecurrentpassword",
            "somenewpassword")

    @patch('conjur.wrapper.keystore_wrapper.KeystoreWrapper.is_keyring_accessible',
           return_value=False)
    @patch('conjur.data_object.conjurrc_data.ConjurrcData.load_from_file',
           return_value=MockConjurrcApi)
    @patch('conjur.logic.credential_provider.FileCredentialsProvider.load',
           return_value=MockCredentialsApi)
    @patch('conjur.api.client.Api')
    def test_client_passes_through_api_host_factory_token_create_params(
            self, mock_api_instance, mock_creds,
            mock_api_config, mock_accessible):
        mock_create_token_data = CreateTokenData(host_factory="some_hostfactory_id", days=1)
        create_client().create_token(mock_create_token_data)

        mock_api_instance.return_value.create_token.assert_called_once_with(mock_create_token_data)
