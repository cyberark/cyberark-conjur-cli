# -*- coding: utf-8 -*-

"""
CLI Integration Configuration tests

This test file handles the configuration test flows when running
`conjur init`
"""
import os
import shutil
import unittest
from unittest.mock import patch

import requests

from .util.cli_helpers import integration_test, invoke_cli

from conjur.constants import DEFAULT_CONFIG_FILE, DEFAULT_CERTIFICATE_FILE, TEST_HOSTNAME, DEFAULT_NETRC_FILE


class CliIntegrationTestConfigurations(unittest.TestCase):

    # *************** HELPERS ***************

    def setup_cli_params(self, env_vars, *params):
        self.cli_auth_params = ['--debug']
        self.cli_auth_params += params

        return self.cli_auth_params

    def setUp(self):
        self.setup_cli_params({})
        os.system(f'rm -f {DEFAULT_CONFIG_FILE}')
        os.system(f'rm -f {DEFAULT_CERTIFICATE_FILE}')

    def print_instead_of_raise_error(self, error_class, error_message_regex, exit_code):
        output = invoke_cli(self, self.cli_auth_params,
            ['list'], exit_code=exit_code)
        self.assertRegex(output, error_message_regex)

    def evoke_list(self, exit_code=0):
        return invoke_cli(self, self.cli_auth_params,
            ['list'], exit_code=exit_code)

    # *************** INITIAL INIT CONFIGURATION TESTS ***************

    '''
    Validates that the conjurrc was created on the machine
    '''
    @integration_test
    @patch('builtins.input', return_value='yes')
    def test_https_conjurrc_is_created_with_all_parameters_given(self, mock_input):
        self.setup_cli_params({})
        invoke_cli(self, self.cli_auth_params,
            ['init', '--url', TEST_HOSTNAME, '--account', 'someaccount'], exit_code=0)

        assert os.path.isfile(DEFAULT_CERTIFICATE_FILE)

    '''
    Validates that when passed as commandline arguments, the configuration
    data is written properly to conjurrc. 
    
    Note that this test should return a warning because we are working against 
    OSS that doesn't have the /info endpoint
    '''
    @integration_test
    @patch('builtins.input', side_effect=[TEST_HOSTNAME, 'yes', 'someotheraccount'])
    def test_https_conjurrc_is_created_with_no_parameters_given(self, mock_input):
        self.setup_cli_params({})
        invoke_cli(self, self.cli_auth_params,
            ['init'], exit_code=0)

        with open(f"{DEFAULT_CONFIG_FILE}", 'r') as conjurrc:
            lines = conjurrc.readlines()
            assert "---" in lines[0]
            assert "account: someotheraccount" in lines[1]
            assert f"appliance_url: {TEST_HOSTNAME}" in lines[2]

    '''
    Validates that if user does not trust the certificate,
    the conjurrc is not be created on the user's machine
    '''
    @integration_test
    @patch('builtins.input', side_effect=[TEST_HOSTNAME, 'no'])
    def test_https_conjurrc_user_does_not_trust_cert(self, mock_input):
        self.setup_cli_params({})
        output = invoke_cli(self, self.cli_auth_params,
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
        output = invoke_cli(self, self.cli_auth_params,
            ['init', '--url', TEST_HOSTNAME, '--account', 'dev', '--force'], exit_code=0)

        assert "Not overwriting" not in output

    @integration_test
    def test_https_cli_fails_if_cert_is_bad(self):
        shutil.copy('./test/test_config/bad_cert_conjurrc', f'{DEFAULT_CONFIG_FILE}')
        with open(f"{DEFAULT_NETRC_FILE}", "w") as netrc_test:
            netrc_test.write(f"machine {TEST_HOSTNAME}/authn\n")
            netrc_test.write("login admin\n")
            netrc_test.write(f"password {os.environ['CONJUR_AUTHN_API_KEY']}\n")
        self.setup_cli_params({})

        self.print_instead_of_raise_error(requests.exceptions.SSLError, "SSLError", exit_code=1)

    @integration_test
    def test_https_cli_fails_if_cert_is_not_provided(self):
        shutil.copy('./test/test_config/no_cert_conjurrc', f'{DEFAULT_CONFIG_FILE}')
        with open(f"{DEFAULT_NETRC_FILE}", "w") as netrc_test:
            netrc_test.write(f"machine {TEST_HOSTNAME}/authn\n")
            netrc_test.write("login admin\n")
            netrc_test.write(f"password {os.environ['CONJUR_AUTHN_API_KEY']}\n")
        self.setup_cli_params({})

        self.print_instead_of_raise_error(requests.exceptions.SSLError, "SSLError", exit_code=1)
