# -*- coding: utf-8 -*-

"""
CLI Integration Credentials tests

This test file handles the login/logout test flows when running
`conjur login`/`conjur logout`
"""
import os
import shutil
from unittest.mock import patch

from conjur.logic.credential_provider import CredentialStoreFactory
from conjur.logic.credential_provider.CredentialProviderTypes import CredentialProviderTypes
from test.util.test_infrastructure import integration_test
from test.util.test_runners.integration_test_case import IntegrationTestCaseBase
from test.util import test_helpers as utils

from conjur.constants import DEFAULT_NETRC_FILE, DEFAULT_CONFIG_FILE, DEFAULT_CERTIFICATE_FILE


class CliIntegrationTestCredentialsNetrc(IntegrationTestCaseBase):
    # *************** HELPERS ***************
    def __init__(self, testname, client_params=None, environment_params=None):
        super(CliIntegrationTestCredentialsNetrc, self).__init__(testname, client_params, environment_params)

    def __del__(self):
        CredentialStoreFactory().override_usage(CredentialProviderTypes.NONE)

    def setup_cli_params(self, env_vars, *params):
        CredentialStoreFactory().override_usage(CredentialProviderTypes.NETRC)
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

    # *************** LOGIN CREDENTIALS TESTS ***************

    '''
    Validates that if a user configures the CLI in insecure mode and runs the command not in 
    insecure mode, then they will fail
    '''

    @integration_test(True)
    def test_cli_configured_in_insecure_mode_but_run_in_secure_mode_raises_error(self):
        shutil.copy(self.environment.path_provider.test_insecure_conjurrc_file_path,
                    self.environment.path_provider.conjurrc_path)
        output = self.invoke_cli(self.cli_auth_params,
                                 ['login', '-i', 'admin', '-p', self.client_params.env_api_key], exit_code=1)
        self.assertIn("The client was initialized without", output)

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
        self.validate_netrc(f"{self.client_params.hostname}", "admin", self.client_params.env_api_key)

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
                                 ['logout'], exit_code=1)
        self.assertIn("You are already logged out", logout.strip())

    '''
    Validates logout doesn't remove another entry not associated with Cyberark
    '''

    @integration_test(True)
    def test_https_netrc_does_not_remove_irrelevant_entry(self):

        with open(f"{DEFAULT_NETRC_FILE}", "w") as netrc_test:
            netrc_test.write(f"machine {self.client_params.hostname}\n")
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


