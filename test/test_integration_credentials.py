# -*- coding: utf-8 -*-

"""
CLI Integration Credentials tests

This test file handles the login/logout test flows when running
`conjur login`/`conjur logout`
"""
import base64
import os
import shutil
import string
import unittest
from unittest.mock import patch

import requests

from .util.cli_helpers import integration_test, invoke_cli

from conjur.constants import DEFAULT_NETRC_FILE, DEFAULT_CONFIG_FILE, DEFAULT_CERTIFICATE_FILE, TEST_HOSTNAME

class CliIntegrationTestCredentials(unittest.TestCase):
    # *************** HELPERS ***************

    def setup_cli_params(self, env_vars, *params):
        self.cli_auth_params = ['--debug']
        self.cli_auth_params += params

        return self.cli_auth_params

    def setUp(self):
        self.setup_cli_params({})
        try:
            os.remove(DEFAULT_NETRC_FILE)
            os.remove(DEFAULT_CONFIG_FILE)
            os.remove(DEFAULT_CERTIFICATE_FILE)
        except OSError:
            pass

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
    @integration_test
    @patch('builtins.input', return_value='yes')
    def test_https_netrc_is_created_with_all_parameters_given(self,mock_input):
        shutil.copy('./test/test_config/conjurrc', f'{DEFAULT_CONFIG_FILE}')
        invoke_cli(self, self.cli_auth_params,
            ['login', '-n', 'admin', '-p', os.environ['CONJUR_AUTHN_API_KEY']], exit_code=0)

        # Load in new user
        invoke_cli(self, self.cli_auth_params,
           ['policy', 'replace', 'root', 'test/test_config/conjur_policy.yml'], exit_code=0)

        # Get admin's access token to be able to use it to change the user's password
        headers = {
          'Content-Type': 'text/plain'
        }
        response = requests.request("POST", f"{TEST_HOSTNAME}/authn/dev/admin/authenticate",
                                    headers=headers, data=os.environ['CONJUR_AUTHN_API_KEY'],
                                    verify="test/test_config/https/ca.crt")
        access_token = base64.b64encode(response.content).decode("utf-8")
        headers = {
          'Authorization': f'Token token="{access_token}"'
        }

        # We want to rotate the API key of the host so we will know the value
        user_api_key = requests.request("PUT", f"{TEST_HOSTNAME}/authn/dev/api_key?role=user:someuser",
                                        headers=headers, data=os.environ['CONJUR_AUTHN_API_KEY'],
                                        verify="test/test_config/https/ca.crt").text

        # Creates a password that meets Conjur-specific criteria
        password = string.hexdigits + "$!@"
        combo = base64.b64encode(f"someuser:{user_api_key}".encode("utf-8"))
        headers = {
          'Authorization': f'Basic {str(combo, "utf-8")}',
          'Content-Type': 'text/plain'
        }
        requests.request("PUT", f"{TEST_HOSTNAME}/authn/dev/password",
                         headers=headers, data=password,
                         verify="/opt/conjur-api-python3/test/test_config/https/ca.crt")

        # Need to remove the netrc because we are attempting to login as a user with their new password
        os.remove(DEFAULT_NETRC_FILE)
        output = invoke_cli(self, self.cli_auth_params,
            ['login', '-n', 'someuser', '-p', password], exit_code=0)

        self.assertEquals(output.strip(), "Successfully logged in to Conjur")
        self.validate_netrc(f"{TEST_HOSTNAME}/authn", "someuser", user_api_key)

    '''
    Validates interactively provided params create netrc
    '''
    @integration_test
    @patch('builtins.input', return_value='admin')
    @patch('getpass.getpass', return_value=os.environ['CONJUR_AUTHN_API_KEY'])
    def test_https_netrc_is_created_with_all_parameters_given_interactively(self, mock_pass, mock_input):
        shutil.copy('./test/test_config/conjurrc', f'{DEFAULT_CONFIG_FILE}')

        output = invoke_cli(self, self.cli_auth_params,
            ['login'], exit_code=0)

        assert os.path.exists(DEFAULT_NETRC_FILE) and os.path.getsize(DEFAULT_NETRC_FILE) != 0
        self.assertEquals(output.strip(), "Successfully logged in to Conjur")
        self.validate_netrc(f"{TEST_HOSTNAME}/authn", "admin", os.environ['CONJUR_AUTHN_API_KEY'])

    '''
    Validates a wrong username will raise Unauthorized error
    '''
    @integration_test
    @patch('builtins.input', return_value='somebaduser')
    @patch('getpass.getpass', return_value=os.environ['CONJUR_AUTHN_API_KEY'])
    def test_https_netrc_raises_error_with_wrong_user(self, mock_pass, mock_input):
        shutil.copy('./test/test_config/conjurrc', f'{DEFAULT_CONFIG_FILE}')

        output = invoke_cli(self, self.cli_auth_params,
            ['login'], exit_code=1)

        self.assertRegex(output, "Reason: 401")
        assert not os.path.exists(DEFAULT_NETRC_FILE)

    '''
    Validates a wrong password will raise Unauthorized error
    '''
    @integration_test
    @patch('builtins.input', return_value='admin')
    @patch('getpass.getpass', return_value='somewrongpass')
    def test_https_netrc_with_wrong_password(self, mock_pass, mock_input):
        shutil.copy('./test/test_config/conjurrc', f'{DEFAULT_CONFIG_FILE}')

        output = invoke_cli(self, self.cli_auth_params,
            ['login'], exit_code=1)

        self.assertRegex(output, "Reason: 401")
        assert not os.path.exists(DEFAULT_NETRC_FILE)

    @integration_test
    @patch('builtins.input', return_value='admin')
    @patch('getpass.getpass', return_value=os.environ['CONJUR_AUTHN_API_KEY'])
    def test_https_netrc_is_created_when_provided_user_api_key(self, mock_pass, mock_input):
        shutil.copy('./test/test_config/conjurrc', f'{DEFAULT_CONFIG_FILE}')

        output = invoke_cli(self, self.cli_auth_params,
            ['login'], exit_code=0)

        assert os.path.exists(DEFAULT_NETRC_FILE) and os.path.getsize(DEFAULT_NETRC_FILE) != 0
        self.assertEquals(output.strip(), "Successfully logged in to Conjur")

        self.validate_netrc(f"{TEST_HOSTNAME}/authn", "admin", os.environ['CONJUR_AUTHN_API_KEY'])

    '''
    Validates that when a user already logged in and reattempts and fails, the previous successful session is not removed
    '''
    @integration_test
    def test_https_netrc_was_not_overwritten_when_login_failed_but_already_logged_in(self):
        shutil.copy('./test/test_config/conjurrc', f'{DEFAULT_CONFIG_FILE}')

        successful_run = invoke_cli(self, self.cli_auth_params,
            ['login', '-n', 'admin', '-p', os.environ['CONJUR_AUTHN_API_KEY']], exit_code=0)
        self.assertEquals(successful_run.strip(), "Successfully logged in to Conjur")

        unsuccessful_run = invoke_cli(self, self.cli_auth_params,
            ['login', '-n', 'someinvaliduser', '-p', 'somewrongpassword'], exit_code=1)
        self.assertRegex(unsuccessful_run, "Reason: 401 Client Error: Unauthorized for")
        self.validate_netrc(f"{TEST_HOSTNAME}/authn", "admin", os.environ['CONJUR_AUTHN_API_KEY'])

    '''
    Validates login is successful for hosts
    
    Note we need to create the host first and rotate it's API key so that we can access it.
    There is currently no way to fetch a host's API key so this is a work around for the 
    purposes of this test
    '''
    @integration_test
    def test_https_netrc_is_created_with_host(self):
        # Setup for fetching the API key of a host. To fetch we need to login
        shutil.copy('./test/test_config/conjurrc', f'{DEFAULT_CONFIG_FILE}')

        self.write_to_netrc(f"{TEST_HOSTNAME}/authn", "admin", os.environ['CONJUR_AUTHN_API_KEY'] )

        invoke_cli(self, self.cli_auth_params,
                   ['policy', 'replace', 'root', 'test/test_config/conjur_policy.yml'], exit_code=0)

        url = f"{TEST_HOSTNAME}/authn/dev/admin/authenticate"
        headers = {
          'Content-Type': 'text/plain'
        }
        response = requests.request("POST", url, headers=headers, data=os.environ['CONJUR_AUTHN_API_KEY'], verify="test/test_config/https/ca.crt")
        access_token = base64.b64encode(response.content).decode("utf-8")

        headers = {
          'Authorization': f'Token token="{access_token}"'
        }
        url = f"{TEST_HOSTNAME}/authn/dev/api_key?role=host:somehost"
        # We want to rotate the API key of the host so we will know the value
        host_api_key = requests.request("PUT", url, headers=headers, data=os.environ['CONJUR_AUTHN_API_KEY'], verify="test/test_config/https/ca.crt").text

        os.remove(DEFAULT_NETRC_FILE)

        output = invoke_cli(self, self.cli_auth_params,
            ['login', '-n', 'host/somehost', '-p', f'{host_api_key}'], exit_code=0)

        self.validate_netrc(f"{TEST_HOSTNAME}/authn", "host/somehost", host_api_key)
        self.assertEquals(output.strip(), "Successfully logged in to Conjur")

    '''
    Validates when a user can logout successfully
    '''
    @integration_test
    def test_https_logout_successful(self):
        shutil.copy('./test/test_config/conjurrc', f'{DEFAULT_CONFIG_FILE}')
        invoke_cli(self, self.cli_auth_params,
            ['login', '-n', 'admin', '-p', os.environ['CONJUR_AUTHN_API_KEY']], exit_code=0)
        assert os.path.exists(DEFAULT_NETRC_FILE) and os.path.getsize(DEFAULT_NETRC_FILE) != 0

        output = invoke_cli(self, self.cli_auth_params,
            ['logout'], exit_code=0)

        self.assertEquals(output.strip(), 'Logged out of Conjur')
        assert os.path.getsize(DEFAULT_NETRC_FILE) == 1

    '''
    Validates when a user attempts to logout after an already 
    successful logout, will fail
    '''
    @integration_test
    def test_https_logout_twice_returns_could_not_logout_message(self):
        shutil.copy('./test/test_config/conjurrc', f'{DEFAULT_CONFIG_FILE}')

        invoke_cli(self, self.cli_auth_params,
            ['login', '-n', 'admin', '-p', os.environ['CONJUR_AUTHN_API_KEY']], exit_code=0)

        invoke_cli(self, self.cli_auth_params,
            ['logout'], exit_code=0)

        unsuccessful_logout = invoke_cli(self, self.cli_auth_params,
            ['logout'], exit_code=1)

        self.assertEquals(unsuccessful_logout.strip(), "Failed to log out. Please log in.")
        assert os.path.getsize(DEFAULT_NETRC_FILE) == 1

    @integration_test
    def test_no_netrc_and_logout_returns_could_not_logout_message(self):
        try:
            os.remove(DEFAULT_NETRC_FILE)
        except OSError:
            pass
        unsuccessful_logout = invoke_cli(self, self.cli_auth_params,
            ['logout'], exit_code=1)
        self.assertEquals(unsuccessful_logout.strip(), "Failed to log out. Please log in.")

    '''
    Validates logout doesn't remove another entry not associated with Cyberark
    '''
    @integration_test
    def test_https_netrc_does_not_remove_irrelevant_entry(self):
        shutil.copy('./test/test_config/conjurrc', f'{DEFAULT_CONFIG_FILE}')
        with open(f"{DEFAULT_NETRC_FILE}", "w") as netrc_test:
            netrc_test.write(f"machine {TEST_HOSTNAME}/authn\n")
            netrc_test.write("login admin\n")
            netrc_test.write(f"password {os.environ['CONJUR_AUTHN_API_KEY']}\n")

            netrc_test.write("machine somemachine\n")
            netrc_test.write("login somelogin\n")
            netrc_test.write("password somepass\n")

        invoke_cli(self, self.cli_auth_params,
                   ['logout'], exit_code=0)

        with open(DEFAULT_NETRC_FILE, 'r') as netrc:
            entries = netrc.readlines()
            assert f"machine {TEST_HOSTNAME}/authn" not in entries
            assert "login admin" not in entries
            assert f"password {os.environ['CONJUR_AUTHN_API_KEY']}" not in entries

            assert "machine somemachine\n" in entries
            assert "login somelogin\n" in entries
            assert "password somepass\n" in entries
    '''
    Validates that when the user does not log in and attempt
    to interface with the CLI, they will be prompted to
    '''
    @integration_test
    @patch('builtins.input', return_value='someaccount')
    @patch('getpass.getpass', return_value='somepass')
    def test_user_runs_list_without_netrc_prompts_user_to_login(self, mock_pass, mock_input):
        shutil.copy('./test/test_config/conjurrc', f'{DEFAULT_CONFIG_FILE}')

        list_attempt = invoke_cli(self, self.cli_auth_params,
            ['list'], exit_code=1)
        self.assertRegex(list_attempt.strip(), "Unable to authenticate with Conjur.")
