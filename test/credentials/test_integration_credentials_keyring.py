# -*- coding: utf-8 -*-

"""
CLI Integration Credentials tests

This test file handles the login/logout test flows when running
`conjur login`/`conjur logout`
"""
import os
import shutil
import string
from unittest.mock import patch
import uuid

from conjur.data_object import CredentialsData
from conjur.logic.credential_provider import CredentialStoreFactory, KeystoreCredentialsProvider
from conjur.util.os_types import OSTypes
from conjur.util.util_functions import get_current_os
from test.util.test_infrastructure import integration_test
from test.util.test_runners.integration_test_case import IntegrationTestCaseBase
from test.util import test_helpers as utils

from conjur.constants import DEFAULT_CONFIG_FILE, DEFAULT_CERTIFICATE_FILE, DEFAULT_NETRC_FILE, \
    KEYRING_TYPE_ENV_VARIABLE_NAME, MAC_OS_KEYRING_NAME, LINUX_KEYRING_NAME, WINDOWS_KEYRING_NAME


class CliIntegrationTestCredentialsKeyring(IntegrationTestCaseBase):
    # *************** HELPERS ***************
    def __init__(self, testname, client_params=None, environment_params=None):
        super(CliIntegrationTestCredentialsKeyring, self).__init__(testname, client_params, environment_params)

    def setUp(self):
        self.setup_cli_params({})
        try:
            utils.delete_credentials()
            utils.remove_file(DEFAULT_NETRC_FILE)
            utils.remove_file(DEFAULT_CONFIG_FILE)
            utils.remove_file(DEFAULT_CERTIFICATE_FILE)
        except OSError:
            pass
        utils.init_to_cli(self)

    def validate_credentials(self, machine, login, password):
        creds = utils.get_credentials()

        assert creds.machine == machine
        assert creds.login == login
        assert creds.password == password

    # *************** LOGIN CREDENTIALS TESTS ***************

    '''
    Validate the correct CredentialStore selected. This test is important 
    because it determines if we are using the correct credential provider 
    for these tests (keyring)
    '''
    @integration_test()
    def test_provider_can_return_keystore_provider_keyring(self):
        cred_store = utils.create_cred_store()
        self.assertEquals(type(cred_store), type(KeystoreCredentialsProvider()))

    '''
    Validates that if a user configures the CLI in insecure mode and runs the command not in 
    insecure mode, then they will fail
    '''
    @integration_test(True)
    def test_cli_configured_in_insecure_mode_but_run_in_secure_mode_raises_error_keyring(self):
        shutil.copy(self.environment.path_provider.test_insecure_conjurrc_file_path,
                    self.environment.path_provider.conjurrc_path)
        output = self.invoke_cli(self.cli_auth_params,
                                 ['login', '-i', 'admin', '-p', self.client_params.env_api_key], exit_code=1)
        self.assertIn("The client was initialized without", output)
        self.assertEquals(utils.is_netrc_exists(), False)

    '''
    Validates that if a user configures the CLI in insecure mode and runs a command in 
    insecure mode, then they will succeed
    '''
    @integration_test(True)
    @patch('builtins.input', return_value='yes')
    def test_cli_configured_in_insecure_mode_and_run_in_insecure_mode_passes_keyring(self, mock_input):
        self.invoke_cli(self.cli_auth_params,
                        ['--insecure', 'init', '--url', self.client_params.hostname, '--account',
                         self.client_params.account])

        output = self.invoke_cli(self.cli_auth_params,
                                 ['--insecure', 'login', '-i', 'admin', '-p', self.client_params.env_api_key])
        self.assertIn('Successfully logged in to Conjur', output)
        self.assertEquals(utils.is_netrc_exists(), False)

    '''
    Validates that if a user runs in insecure mode without supplying inputs, 
    we will ask for them and successfully initialize the client
    '''
    @integration_test(True)
    def test_cli_configured_in_insecure_mode_with_params_and_passes_keyring(self):
        utils.remove_file(DEFAULT_CONFIG_FILE)
        utils.remove_file(DEFAULT_CERTIFICATE_FILE)
        with patch('builtins.input', side_effect=[self.client_params.hostname, self.client_params.account]):
            output = self.invoke_cli(self.cli_auth_params,
                                    ['--insecure', 'init'])

        self.assertRegex(output, 'To start using the Conjur CLI')

    '''
    Validates a user can log in with a password, instead of their API key
    To do this, we perform the following:
    '''
    @integration_test()
    @patch('builtins.input', return_value='yes')
    def test_https_credentials_user_can_login_successfully_when_another_user_is_already_logged_in_keyring(self, mock_input):
        self.invoke_cli(self.cli_auth_params,
                        ['login', '-i', 'admin', '-p', self.client_params.env_api_key])

        # Load in new user
        self.invoke_cli(self.cli_auth_params,
                        ['policy', 'replace', '-b', 'root', '-f',
                         self.environment.path_provider.get_policy_path('conjur')])

        # Rotate the new user's API key
        user_api_key = self.invoke_cli(self.cli_auth_params,
                                       ['user', 'rotate-api-key', '-i', 'someuser'])
        extract_api_key_from_message = user_api_key.split(":")[1].strip()

        # Login to change personal password
        self.invoke_cli(self.cli_auth_params,
                        ['login', '-i', 'someuser', '-p', extract_api_key_from_message])

        # Creates a password that meets Conjur password complexity standards
        password = string.hexdigits + "$!@"
        self.invoke_cli(self.cli_auth_params,
                        ['user', 'change-password', '-p', password])

        self.invoke_cli(self.cli_auth_params,
                        ['logout'])

        # Attempt to login with newly created password
        output = self.invoke_cli(self.cli_auth_params,
                                 ['login', '-i', 'someuser', '-p', password])

        self.assertIn("Successfully logged in to Conjur", output.strip())
        utils.get_credentials()
        self.validate_credentials(f"{self.client_params.hostname}", "someuser", extract_api_key_from_message)
        self.assertEquals(utils.is_netrc_exists(), False)

    '''
    Validate that login create valid credentials
    '''
    @integration_test()
    @patch('builtins.input', return_value='yes')
    def test_https_credentials_created_with_all_parameters_given_keyring(self, mock_input):
        self.invoke_cli(self.cli_auth_params,
                        ['login', '-i', 'admin', '-p', self.client_params.env_api_key])
        utils.get_credentials()
        self.validate_credentials(f"{self.client_params.hostname}", "admin", self.client_params.env_api_key)
        self.assertEquals(utils.is_netrc_exists(), False)

    '''
    Validate correct message when try to logout already logout user
    '''
    @integration_test(True)
    def test_no_credentials_and_logout_returns_successful_logout_message_keyring(self):
        utils.delete_credentials()
        logout = self.invoke_cli(self.cli_auth_params,
                                 ['logout'], exit_code=1)
        self.assertIn("You are already logged out", logout.strip())

    '''
    Validates a wrong username will raise Unauthorized error
    '''
    @integration_test()
    @patch('builtins.input', return_value='somebaduser')
    def test_https_credentials_raises_error_with_wrong_user_keyring(self, mock_pass):
        with patch('getpass.getpass', return_value=self.client_params.env_api_key):
            output = self.invoke_cli(self.cli_auth_params,
                                     ['login'], exit_code=1)

            self.assertRegex(output, "Reason: 401")

    '''
    Validates a wrong password will raise Unauthorized error
    '''
    @integration_test()
    @patch('builtins.input', return_value='admin')
    @patch('getpass.getpass', return_value='somewrongpass')
    def test_https_credentials_with_wrong_password_keyring(self, mock_pass, mock_input):

        output = self.invoke_cli(self.cli_auth_params,
                                 ['login'], exit_code=1)

        self.assertRegex(output, "Reason: 401")

    '''
    Validates that when the user hasn't logged in and attempts 
    to run a command, they will be prompted to login
    '''
    @integration_test()
    @patch('builtins.input', return_value='someaccount')
    @patch('getpass.getpass', return_value='somepass')
    def test_user_runs_list_without_credentials_prompts_user_to_login_keyring(self, mock_pass, mock_input):
        # Set this environment variable to prompt the user to login
        os.environ["TEST_ENV"] = "False"
        list_attempt = self.invoke_cli(self.cli_auth_params,
                                       ['list'], exit_code=1)
        self.assertRegex(list_attempt.strip(), "Unable to authenticate with Conjur.")
        os.environ["TEST_ENV"] = "True"

    '''
    Validate interactive login 
    '''
    @integration_test()
    @patch('builtins.input', return_value='admin')
    def test_https_credentials_is_created_when_provided_user_api_key_keyring(self, mock_pass):
        with patch('getpass.getpass', return_value=self.client_params.env_api_key):
            output = self.invoke_cli(self.cli_auth_params,
                                     ['login'])

            assert utils.get_credentials() is not None
            self.assertIn("Successfully logged in to Conjur", output.strip())

            self.validate_credentials(f"{self.client_params.hostname}", "admin", self.client_params.env_api_key)
            self.assertEquals(utils.is_netrc_exists(), False)

    '''
    Validates interactively provided params create credentials
    '''
    @integration_test()
    @patch('builtins.input', return_value='admin')
    def test_https_credentials_is_created_with_all_parameters_given_interactively_keyring(self, mock_pass):
        with patch('getpass.getpass', return_value=self.client_params.env_api_key):
            output = self.invoke_cli(self.cli_auth_params, ['login'])

            assert utils.get_credentials() is not None
            self.assertIn("Successfully logged in to Conjur", output.strip())
            self.validate_credentials(f"{self.client_params.hostname}", "admin", self.client_params.env_api_key)
            self.assertEquals(utils.is_netrc_exists(), False)

    '''
    Validates login is successful for hosts
    Note we need to create the host first and rotate it's API key so that we can access it.
    There is currently no way to fetch a host's API key so this is a work around for the 
    purposes of this test
    '''
    @integration_test()
    def test_https_credentials_is_created_with_host_keyring(self):
        # Setup for fetching the API key of a host. To fetch we need to login
        credentials = CredentialsData(self.client_params.hostname, "admin", self.client_params.env_api_key)
        utils.save_credentials(credentials)

        self.invoke_cli(self.cli_auth_params,
                        ['policy', 'replace', '-b', 'root', '-f',
                         self.environment.path_provider.get_policy_path('conjur')])

        host_api_key = self.invoke_cli(self.cli_auth_params,
                                       ['host', 'rotate-api-key', '-i', 'somehost'])

        extract_api_key_from_message = host_api_key.split(":")[1].strip()

        self.invoke_cli(self.cli_auth_params,
                        ['logout'])

        output = self.invoke_cli(self.cli_auth_params,
                                 ['login', '-i', 'host/somehost', '-p', f'{extract_api_key_from_message}'])

        self.validate_credentials(f"{self.client_params.hostname}", "host/somehost", extract_api_key_from_message)
        self.assertIn("Successfully logged in to Conjur", output.strip())
        self.assertEquals(utils.is_netrc_exists(), False)

    '''
    Validates logout doesn't remove an irrelevant entry
    '''
    @integration_test(True)
    def test_https_credentials_does_not_remove_irrelevant_entry_keyring(self):
        creds = CredentialsData(self.client_params.hostname, "admin", self.client_params.env_api_key)
        utils.save_credentials(creds)

        creds = CredentialsData("somemachine", "somelogin", "somepass")
        utils.save_credentials(creds)

        self.invoke_cli(self.cli_auth_params,
                        ['logout'])
        cred_store = utils.create_cred_store()
        assert cred_store.is_exists("somemachine")
        assert not cred_store.is_exists(self.client_params.hostname)

    '''
    Validate logout after logout flow
    '''
    @integration_test(True)
    def test_https_logout_twice_returns_could_not_logout_message_keyring(self):
        self.invoke_cli(self.cli_auth_params,
                        ['login', '-i', 'admin', '-p', self.client_params.env_api_key])

        self.invoke_cli(self.cli_auth_params,
                        ['logout'])

        unsuccessful_logout = self.invoke_cli(self.cli_auth_params,
                                              ['logout'], exit_code=1)

        self.assertIn("Failed to log out. You are already logged out", unsuccessful_logout.strip())
        assert not utils.is_credentials_exist()

    '''
    Validates that a user can logout successfully
    '''
    @integration_test(True)
    def test_https_logout_successful_keyring(self):

        self.invoke_cli(self.cli_auth_params,
                        ['login', '-i', 'admin', '-p', self.client_params.env_api_key])

        output = self.invoke_cli(self.cli_auth_params,
                                 ['logout'])

        self.assertIn('Successfully logged out from Conjur', output.strip())
        assert not utils.is_credentials_exist()

    '''
    Validates that if a user configures the CLI in insecure mode and runs the command not in 
    insecure mode, then they will fail
    '''
    @integration_test(True)
    def test_cli_configured_in_insecure_mode_but_run_in_secure_mode_raises_error_keyring(self):
        shutil.copy(self.environment.path_provider.test_insecure_conjurrc_file_path,
                    self.environment.path_provider.conjurrc_path)
        output = self.invoke_cli(self.cli_auth_params,
                                 ['login', '-i', 'admin', '-p', self.client_params.env_api_key], exit_code=1)
        self.assertIn("The client was initialized without", output)

    '''
    Validate logout flow when using the system's keyring
    '''
    @integration_test(True)
    def test_https_logout_successful_keyring(self):
        utils.setup_cli(self)
        self.invoke_cli(self.cli_auth_params,
                        ['login', '-i', 'admin', '-p', self.client_params.env_api_key])

        output = self.invoke_cli(self.cli_auth_params,
                                 ['logout'])

        self.assertIn('Successfully logged out from Conjur', output.strip())

    '''
    Validates that if a user configures the CLI in insecure mode and runs the command not in 
    insecure mode, then they will fail
    '''
    @integration_test(True)
    def test_cli_configured_in_insecure_mode_but_run_in_secure_mode_raises_error_keyring(self):
        shutil.copy(self.environment.path_provider.test_insecure_conjurrc_file_path,
                    self.environment.path_provider.conjurrc_path)
        output = self.invoke_cli(self.cli_auth_params,
                                 ['login', '-i', 'admin', '-p', self.client_params.env_api_key], exit_code=1)
        self.assertIn("The client was initialized without", output)

    '''
    Validate that logout indeed remove credentials and terminate access to Conjur
    '''
    @integration_test()
    def test_cli_simple_login_logout_flow_keyring(self):
        utils.setup_cli(self)
        creds = utils.get_credentials()
        assert creds.machine == self.client_params.hostname
        self.invoke_cli(self.cli_auth_params, ['logout'])
        assert not utils.is_credentials_exist(creds.machine)
        self.invoke_cli(self.cli_auth_params, ['list'], exit_code=1)

    '''
    Validate basic policy flow with keyring
    '''
    @integration_test(True)
    def test_https_can_load_policy_keyring(self):
        self.setup_cli_params({})
        utils.setup_cli(self)
        policy, variables = utils.generate_policy_string()
        utils.load_policy_from_string(self, policy)

        for variable in variables:
            utils.assert_set_and_get(self, variable)

    '''
    Validate access is blocked when keyring disabled after login
    '''
    @integration_test(True)
    def test_keyring_locked_after_login_will_raise_error_keyring(self):
        utils.setup_cli(self)
        with patch('conjur.wrapper.keystore_wrapper.KeystoreWrapper.is_keyring_accessible', return_value=False):
            self.invoke_cli(self.cli_auth_params, ['list'], exit_code=1)

    '''
    Validate env variable is set correctly
    '''
    @integration_test(True)
    def test_keyring_locked_after_login_will_raise_error_keyring(self):
        utils.create_cred_store()

        current_platform = get_current_os()
        if current_platform == OSTypes.MAC_OS:
            assert os.getenv(KEYRING_TYPE_ENV_VARIABLE_NAME) == MAC_OS_KEYRING_NAME
        if current_platform == OSTypes.LINUX:
            assert os.getenv(KEYRING_TYPE_ENV_VARIABLE_NAME) == LINUX_KEYRING_NAME
        if current_platform == OSTypes.WINDOWS:
            assert os.getenv(KEYRING_TYPE_ENV_VARIABLE_NAME) == WINDOWS_KEYRING_NAME

    '''
    Validate variable operation with keyring
    '''
    @integration_test()
    def test_basic_secret_retrieval_with_keyring(self):
        """
        Note about version tests, the Conjur server only keeps a certain number of versions.
        With each run of the integration tests, version tests are resetting variable values
        making, after a certain number of runs, version=1 not valid and fail
        Therefore, the variable name needs to be a random string so that the version
        will still be accessible
        """
        utils.setup_cli(self)
        variable_name = "someversionedvar" + uuid.uuid4().hex
        policy = f"- !variable {variable_name}"
        utils.load_policy_from_string(self, policy)

        expected_value = "anothersecret"
        utils.set_variable(self, variable_name, expected_value)
        output = self.invoke_cli(self.cli_auth_params,
                                 ['variable', 'get', '-i', variable_name, '--version', '1'])
        self.assertIn(expected_value, output.strip())
