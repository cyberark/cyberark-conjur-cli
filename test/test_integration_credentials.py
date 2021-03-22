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

from conjur.data_object import CredentialsData
from conjur.logic.credential_provider import CredentialStoreFactory, KeystoreCredentialsProvider
from test.util.test_infrastructure import integration_test
from test.util.test_runners.integration_test_case import IntegrationTestCaseBase
from test.util import test_helpers as utils

from conjur.constants import DEFAULT_NETRC_FILE, DEFAULT_CONFIG_FILE, DEFAULT_CERTIFICATE_FILE


class CliIntegrationTestCredentials(IntegrationTestCaseBase):
    # *************** HELPERS ***************
    def __init__(self, testname, client_params=None, environment_params=None):
        super(CliIntegrationTestCredentials, self).__init__(testname, client_params, environment_params)

    def setup_cli_params(self, env_vars, *params):
        self.cli_auth_params = ['--debug']
        self.cli_auth_params += params

        return self.cli_auth_params

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


    def write_to_netrc(self, machine, login, password):
        with open(f"{DEFAULT_NETRC_FILE}", "w") as netrc_test:
            netrc_test.write(f"machine {machine}\n")
            netrc_test.write(f"login {login}\n")
            netrc_test.write(f"password {password}\n")

    # *************** LOGIN CREDENTIALS TESTS ***************

    '''
    Validates that if a user configures the CLI in insecure mode and runs the command not in 
    insecure mode, then they will fail
    '''
    @integration_test(True)
    def test_cli_configured_in_insecure_mode_but_run_in_secure_mode_raises_error(self):
        shutil.copy(self.environment.path_provider.test_insecure_conjurrc_file_path, self.environment.path_provider.conjurrc_path)
        output = self.invoke_cli(self.cli_auth_params,
                            ['login', '-i', 'admin', '-p', self.client_params.env_api_key], exit_code=1)
        self.assertIn("The client was initialized without", output)

    '''
    Validates that if a user configures the CLI in insecure mode and runs a command in 
    insecure mode, then they will succeed
    '''
    @integration_test(True)
    @patch('builtins.input', return_value='yes')
    def test_cli_configured_in_insecure_mode_and_run_in_insecure_mode_passes(self, mock_input):
        self.invoke_cli(self.cli_auth_params,
                        ['--insecure', 'init', '--url', self.client_params.hostname, '--account', self.client_params.account])

        output = self.invoke_cli(self.cli_auth_params,
                            ['--insecure', 'login', '-i', 'admin', '-p', self.client_params.env_api_key])
        self.assertIn('Successfully logged in to Conjur', output)

    '''
    Validates a user can log in with a password, instead of their API key
    To do this, we perform the following:
    '''
    @integration_test()
    @patch('builtins.input', return_value='yes')
    def test_https_netrc_is_created_with_all_parameters_given(self, mock_input):
        self.invoke_cli(self.cli_auth_params,
                        ['login', '-i', 'admin', '-p', self.client_params.env_api_key])

        # Load in new user
        self.invoke_cli(self.cli_auth_params,
                        ['policy', 'replace', '-b', 'root', '-f', self.environment.path_provider.get_policy_path('conjur')])

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

    '''
    Validates a wrong username will raise Unauthorized error
    '''
    @integration_test()
    @patch('builtins.input', return_value='somebaduser')
    def test_https_netrc_raises_error_with_wrong_user(self, mock_pass):
        with patch('getpass.getpass', return_value=self.client_params.env_api_key):
            output = self.invoke_cli(self.cli_auth_params,
                                     ['login'], exit_code=1)

            self.assertRegex(output, "Reason: 401")
            assert not os.path.exists(DEFAULT_NETRC_FILE)

    '''
    Validates a wrong password will raise Unauthorized error
    '''
    @integration_test()
    @patch('builtins.input', return_value='admin')
    @patch('getpass.getpass', return_value='somewrongpass')
    def test_https_netrc_with_wrong_password(self, mock_pass, mock_input):

        output = self.invoke_cli(self.cli_auth_params,
                                 ['login'], exit_code=1)

        self.assertRegex(output, "Reason: 401")
        assert not os.path.exists(DEFAULT_NETRC_FILE)






    '''
    Validates that when the user hasn't logged in and attempts 
    to run a command, they will be prompted to login
    '''
    @integration_test()
    @patch('builtins.input', return_value='someaccount')
    @patch('getpass.getpass', return_value='somepass')
    def test_user_runs_list_without_netrc_prompts_user_to_login(self, mock_pass, mock_input):
        # Set this environment variable to prompt the user to login
        os.environ["TEST_ENV"] = "False"
        list_attempt = self.invoke_cli(self.cli_auth_params,
                                       ['list'], exit_code=1)
        self.assertRegex(list_attempt.strip(), "Unable to authenticate with Conjur.")
        os.environ["TEST_ENV"] = "True"

    @integration_test()
    @patch('builtins.input', return_value='admin')
    def test_https_netrc_is_created_when_provided_user_api_key(self, mock_pass):
        with patch('getpass.getpass', return_value=self.client_params.env_api_key):
            output = self.invoke_cli(self.cli_auth_params,
                                     ['login'])

            assert utils.get_credentials() is not None
            self.assertIn("Successfully logged in to Conjur", output.strip())

            self.validate_credentials(f"{self.client_params.hostname}", "admin", self.client_params.env_api_key)

    '''
        Validates interactively provided params create netrc
        '''

    @integration_test()
    @patch('builtins.input', return_value='admin')
    def test_https_netrc_is_created_with_all_parameters_given_interactively(self, mock_pass):
        with patch('getpass.getpass', return_value=self.client_params.env_api_key):
            output = self.invoke_cli(self.cli_auth_params, ['login'])

            assert utils.get_credentials() is not None
            self.assertIn("Successfully logged in to Conjur", output.strip())
            self.validate_credentials(f"{self.client_params.hostname}", "admin", self.client_params.env_api_key)

    '''
        Validates login is successful for hosts

        Note we need to create the host first and rotate it's API key so that we can access it.
        There is currently no way to fetch a host's API key so this is a work around for the 
        purposes of this test
        '''

    @integration_test()
    def test_https_netrc_is_created_with_host(self):
        # Setup for fetching the API key of a host. To fetch we need to login
        credentials = CredentialsData(self.client_params.hostname,"admin",self.client_params.env_api_key)
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

    @integration_test()
    def test_working_with_keystore(self):
        cred_store,_ = CredentialStoreFactory().create_credential_store()
        self.assertEquals(type(cred_store) , type(KeystoreCredentialsProvider()))