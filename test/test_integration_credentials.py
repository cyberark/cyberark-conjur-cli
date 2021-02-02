# -*- coding: utf-8 -*-

"""
CLI Integration Credentials tests

This test file handles the login/logout test flows when running
`conjur login`/`conjur logout`
"""
import base64
import os
import string
from unittest.mock import patch

import requests

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
            utils.remove_file(DEFAULT_NETRC_FILE)
            utils.remove_file(DEFAULT_CONFIG_FILE)
            utils.remove_file(DEFAULT_CERTIFICATE_FILE)
        except OSError:
            pass
        utils.init_to_cli(self)

    def validate_netrc(self, machine, login, password):
        with open(DEFAULT_NETRC_FILE, 'r') as netrc:
            lines = netrc.readlines()
            assert f"machine {machine}" in lines[0]
            assert f"login {login}" in lines[1]
            assert f"password {password}" in lines[2]

    def write_to_netrc(self, machine, login, password):
        with open(f"{DEFAULT_NETRC_FILE}", "w") as netrc_test:
            netrc_test.write(f"machine {machine}\n")
            netrc_test.write(f"login {login}\n")
            netrc_test.write(f"password {password}\n")

    # *************** INITIAL LOGIN CREDENTIALS TESTS ***************

    '''
    Validates a user can log in with a password, instead of their API key
    To do this, we perform the following:
    1. Load the user
    2. Fetch the user's API key (using the admin's access token) 
       to be able to use it to create a password for them
    3. Update their password to a randomly generated one
    4. Login with their password
    '''
    @integration_test(True)
    @patch('builtins.input', return_value='yes')
    def test_https_netrc_is_created_with_all_parameters_given(self, mock_input):
        self.invoke_cli(self.cli_auth_params,
                        ['login', '-i', 'admin', '-p', self.client_params.env_api_key])

        # Load in new user
        self.invoke_cli(self.cli_auth_params,
                        ['policy', 'replace', '-b', 'root', '-f', self.environment.path_provider.get_policy_path('conjur')])

        # Get admin's access token to be able to use it to change the user's password
        headers = {
            'Content-Type': 'text/plain'
        }
        response = requests.request("POST",
                                    f"{self.client_params.hostname}/authn/{self.client_params.account}/admin/authenticate",
                                    headers=headers, data=self.client_params.env_api_key,
                                    verify=self.environment.path_provider.certificate_path)
        access_token = base64.b64encode(response.content).decode("utf-8")
        headers = {
            'Authorization': f'Token token="{access_token}"'
        }

        # We want to rotate the API key of the host so we will know the value
        user_api_key = requests.request("PUT",
                                        f"{self.client_params.hostname}/authn/{self.client_params.account}/api_key?role=user:someuser",
                                        headers=headers, data=self.client_params.env_api_key,
                                        verify=self.environment.path_provider.certificate_path).text

        # Creates a password that meets Conjur-specific criteria
        password = string.hexdigits + "$!@"
        combo = base64.b64encode(f"someuser:{user_api_key}".encode("utf-8"))
        headers = {
            'Authorization': f'Basic {str(combo, "utf-8")}',
            'Content-Type': 'text/plain'
        }
        requests.request("PUT", f"{self.client_params.hostname}/authn/{self.client_params.account}/password",
                         headers=headers, data=password,
                         verify=self.environment.path_provider.certificate_path)

        # Need to remove the netrc because we are attempting to login as a user with their new password
        os.remove(DEFAULT_NETRC_FILE)
        output = self.invoke_cli(self.cli_auth_params,
                                 ['login', '-i', 'someuser', '-p', password])

        self.assertIn("Successfully logged in to Conjur", output.strip())
        self.validate_netrc(f"{self.client_params.hostname}/authn", "someuser", user_api_key)

    '''
    Validates interactively provided params create netrc
    '''
    @integration_test()
    @patch('builtins.input', return_value='admin')
    def test_https_netrc_is_created_with_all_parameters_given_interactively(self, mock_pass):
        with patch('getpass.getpass', return_value=self.client_params.env_api_key):
            output = self.invoke_cli(self.cli_auth_params, ['login'])

            assert os.path.exists(DEFAULT_NETRC_FILE) and os.path.getsize(DEFAULT_NETRC_FILE) != 0
            self.assertIn("Successfully logged in to Conjur", output.strip())
            self.validate_netrc(f"{self.client_params.hostname}/authn", "admin", self.client_params.env_api_key)

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

    @integration_test()
    @patch('builtins.input', return_value='admin')
    def test_https_netrc_is_created_when_provided_user_api_key(self, mock_pass):
        with patch('getpass.getpass', return_value=self.client_params.env_api_key):
            output = self.invoke_cli(self.cli_auth_params,
                                     ['login'])

            assert os.path.exists(DEFAULT_NETRC_FILE) and os.path.getsize(DEFAULT_NETRC_FILE) != 0
            self.assertIn("Successfully logged in to Conjur", output.strip())

            self.validate_netrc(f"{self.client_params.hostname}/authn", "admin", self.client_params.env_api_key)

    '''
    Validates that when a user already logged in and reattempts and fails, the previous successful session is not removed
    '''

    @integration_test(True)
    def test_https_netrc_was_not_overwritten_when_login_failed_but_already_logged_in(self):

        successful_run = self.invoke_cli(self.cli_auth_params,
                                         ['login', '-i', 'admin', '-p', self.client_params.env_api_key])
        self.assertIn("Successfully logged in to Conjur", successful_run.strip())

        unsuccessful_run = self.invoke_cli(self.cli_auth_params,
                                           ['login', '-i', 'someinvaliduser', '-p', 'somewrongpassword'], exit_code=1)
        self.assertRegex(unsuccessful_run, "Reason: 401 Client Error: Unauthorized for")
        self.validate_netrc(f"{self.client_params.hostname}/authn", "admin", self.client_params.env_api_key)

    '''
    Validates login is successful for hosts
    
    Note we need to create the host first and rotate it's API key so that we can access it.
    There is currently no way to fetch a host's API key so this is a work around for the 
    purposes of this test
    '''
    @integration_test(True)
    def test_https_netrc_is_created_with_host(self):
        # Setup for fetching the API key of a host. To fetch we need to login
        self.write_to_netrc(f"{self.client_params.hostname}/authn", "admin", self.client_params.env_api_key)

        self.invoke_cli(self.cli_auth_params,
                        ['policy', 'replace', '-b', 'root', '-f',self.environment.path_provider.get_policy_path('conjur')])

        url = f"{self.client_params.hostname}/authn/{self.client_params.account}/admin/authenticate"
        headers = {
            'Content-Type': 'text/plain'
        }

        response = requests.request("POST", url, headers=headers, data=self.client_params.env_api_key,
                                    verify=self.environment.path_provider.certificate_path)
        access_token = base64.b64encode(response.content).decode("utf-8")

        headers = {
            'Authorization': f'Token token="{access_token}"'
        }
        url = f"{self.client_params.hostname}/authn/{self.client_params.account}/api_key?role=host:somehost"
        # We want to rotate the API key of the host so we will know the value
        host_api_key = requests.request("PUT", url, headers=headers, data=self.client_params.env_api_key,
                                        verify=self.environment.path_provider.certificate_path).text

        os.remove(DEFAULT_NETRC_FILE)

        output = self.invoke_cli(self.cli_auth_params,
                                 ['login', '-i', 'host/somehost', '-p', f'{host_api_key}'])

        self.validate_netrc(f"{self.client_params.hostname}/authn", "host/somehost", host_api_key)
        self.assertIn("Successfully logged in to Conjur", output.strip())

    '''
    Validates when a user can logout successfully
    '''
    @integration_test(True)
    def test_https_logout_successful(self):

        self.invoke_cli(self.cli_auth_params,
                        ['login', '-i', 'admin', '-p', self.client_params.env_api_key])
        assert os.path.exists(DEFAULT_NETRC_FILE) and os.path.getsize(DEFAULT_NETRC_FILE) != 0

        output = self.invoke_cli(self.cli_auth_params,
                                 ['logout'])

        self.assertIn('Successfully logged out from Conjur', output.strip())
        with open(DEFAULT_NETRC_FILE) as netrc_file:
            assert netrc_file.read().strip() == "", 'netrc file is not empty!'

    '''
    Validates when a user attempts to logout after an already 
    successful logout, will fail
    '''
    @integration_test(True)
    def test_https_logout_twice_returns_could_not_logout_message(self):

        self.invoke_cli(self.cli_auth_params,
                        ['login', '-i', 'admin', '-p', self.client_params.env_api_key])

        self.invoke_cli(self.cli_auth_params,
                        ['logout'])

        unsuccessful_logout = self.invoke_cli(self.cli_auth_params,
                                              ['logout'], exit_code=1)

        self.assertIn("Failed to log out. You are already logged out", unsuccessful_logout.strip())
        with open(DEFAULT_NETRC_FILE) as netrc_file:
            assert netrc_file.read().strip() == "", 'netrc file is not empty!'


    @integration_test(True)
    def test_no_netrc_and_logout_returns_successful_logout_message(self):
        try:
            os.remove(DEFAULT_NETRC_FILE)
        except OSError:
            pass
        logout = self.invoke_cli(self.cli_auth_params,
                                              ['logout'])
        self.assertIn("Successfully logged out from Conjur", logout.strip())

    '''
    Validates logout doesn't remove another entry not associated with Cyberark
    '''
    @integration_test(True)
    def test_https_netrc_does_not_remove_irrelevant_entry(self):

        with open(f"{DEFAULT_NETRC_FILE}", "w") as netrc_test:
            netrc_test.write(f"machine {self.client_params.hostname}/authn\n")
            netrc_test.write("login admin\n")
            netrc_test.write(f"password {self.client_params.env_api_key}\n")

            netrc_test.write("machine somemachine\n")
            netrc_test.write("login somelogin\n")
            netrc_test.write("password somepass\n")

        self.invoke_cli(self.cli_auth_params,
                        ['logout'])

        with open(DEFAULT_NETRC_FILE, 'r') as netrc:
            entries = netrc.readlines()
            assert f"machine {self.client_params.hostname}/authn" not in entries
            assert "login admin" not in entries
            assert f"password {self.client_params.env_api_key}" not in entries

            assert "machine somemachine\n" in entries
            assert "login somelogin\n" in entries
            assert "password somepass\n" in entries

    '''
    Validates that when the user does not log in and attempt
    to interface with the CLI, they will be prompted to
    '''
    @integration_test()
    @patch('builtins.input', return_value='someaccount')
    @patch('getpass.getpass', return_value='somepass')
    def test_user_runs_list_without_netrc_prompts_user_to_login(self, mock_pass, mock_input):

        list_attempt = self.invoke_cli(self.cli_auth_params,
                                       ['list'], exit_code=1)
        self.assertRegex(list_attempt.strip(), "Unable to authenticate with Conjur.")
