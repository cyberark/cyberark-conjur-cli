# -*- coding: utf-8 -*-

"""
CLI Integration Configuration tests

This test file handles the configuration test flows when running
`conjur init`
"""
import os
from unittest.mock import patch

import requests

from .util.cli_helpers import integration_test
from test.util.test_runners.integration_test_case import IntegrationTestCaseBase
from Utils import py_utils as utils

from conjur.constants import DEFAULT_CONFIG_FILE, DEFAULT_CERTIFICATE_FILE, TEST_HOSTNAME, DEFAULT_NETRC_FILE
from test.util.models.configfile import ConfigFile


class CliIntegrationTestConfigurations(IntegrationTestCaseBase):
    def __init__(self, testname, client_params=None, environment_params=None):
        super(CliIntegrationTestConfigurations, self).__init__(testname, client_params, environment_params)

    # *************** HELPERS ***************

    def setup_cli_params(self, env_vars, *params):
        self.cli_auth_params = ['--debug']
        self.cli_auth_params += params

        return self.cli_auth_params

    def setUp(self):
        self.setup_cli_params({})
        utils.remove_file(DEFAULT_CONFIG_FILE)
        utils.remove_file(DEFAULT_CERTIFICATE_FILE)

    def print_instead_of_raise_error(self, error_class, error_message_regex, exit_code):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['list'], exit_code=exit_code)
        self.assertRegex(output, error_message_regex)

    def evoke_list(self, exit_code=0):
        return self.invoke_cli(self.cli_auth_params,
                               ['list'], exit_code=exit_code)

    # *************** INITIAL INIT CONFIGURATION TESTS ***************

    '''
    Validates that the conjurrc was created on the machine
    '''

    @integration_test
    @patch('builtins.input', return_value='yes')
    def test_https_conjurrc_is_created_with_all_parameters_given(self, mock_input):
        self.setup_cli_params({})
        self.invoke_cli(self.cli_auth_params,
                        ['init', '--url', self.client_params.hostname, '--account', 'someaccount'])

        assert os.path.isfile(DEFAULT_CERTIFICATE_FILE)

    '''
    Validates that if user does not trust the certificate,
    the conjurrc is not be created on the user's machine
    '''

    @integration_test
    def test_https_conjurrc_user_does_not_trust_cert(self):
        with patch('builtins.input', side_effect=[self.client_params.hostname, 'no']):
            self.setup_cli_params({})
            output = self.invoke_cli(self.cli_auth_params,
                                     ['init'], exit_code=1)

            self.assertRegex(output, "You decided not to trust the certificate")
            assert not os.path.isfile(DEFAULT_CERTIFICATE_FILE)

    '''
    Validates that when the user adds the force flag,
    no confirmation is required
    '''

    @integration_test
    # The additional side effects here ('somesideffect') would prompt the CLI to
    # request for confirmation which would fail the test
    @patch('builtins.input', side_effect=['yes', 'somesideeffect', 'somesideeffect'])
    def test_https_conjurrc_user_forces_overwrite_does_not_request_confirmation(self, mock_input):
        self.setup_cli_params({})
        output = self.invoke_cli(self.cli_auth_params,
                                 ['init', '--url', self.client_params.hostname, '--account', self.client_params.login,
                                  '--force'])

        assert "Not overwriting" not in output

    @integration_test
    def test_https_cli_fails_if_cert_is_bad(self):
        # bad conjurrc
        conjurrc = ConfigFile(account=self.client_params.login, appliance_url=self.client_params.hostname,
                              cert_file=self.environment.path_provider.nginx_conf_path)
        conjurrc.dump_to_file()
        with open(f"{DEFAULT_NETRC_FILE}", "w") as netrc_test:
            netrc_test.write(f"machine {self.client_params.hostname}/authn\n")
            netrc_test.write("login admin\n")
            netrc_test.write(f"password {self.client_params.env_api_key}\n")
        self.setup_cli_params({})

        self.print_instead_of_raise_error(requests.exceptions.SSLError, "SSLError", exit_code=1)

    @integration_test
    def test_https_cli_fails_if_cert_is_not_provided(self):
        conjurrc = ConfigFile(account=self.client_params.login, appliance_url=self.client_params.hostname,
                              cert_file="")
        conjurrc.dump_to_file()
        with open(f"{DEFAULT_NETRC_FILE}", "w") as netrc_test:
            netrc_test.write(f"machine {self.client_params.hostname}/authn\n")
            netrc_test.write("login admin\n")
            netrc_test.write(f"password {self.client_params.env_api_key}\n")
        self.setup_cli_params({})

        self.print_instead_of_raise_error(requests.exceptions.SSLError, "SSLError", exit_code=1)
