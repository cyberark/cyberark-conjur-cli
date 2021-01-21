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

from .util.cli_helpers import integration_test
from test.util.test_runners.integration_test_case import IntegrationTestCaseBase
from Utils import py_utils as utils

from conjur.constants import DEFAULT_CONFIG_FILE, DEFAULT_CERTIFICATE_FILE, TEST_HOSTNAME, DEFAULT_NETRC_FILE
from test.util.models.configfile import ConfigFile


class CliIntegrationTestOSS(IntegrationTestCaseBase):
    def __init__(self, testname, client_params=None, environment_params=None):
        super(CliIntegrationTestOSS, self).__init__(testname, client_params, environment_params)

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
    Validates that when passed as commandline arguments, the configuration
    data is written properly to conjurrc. 

    Note that this test should return a warning because we are working against 
    OSS that doesn't have the /info endpoint
    '''

    @integration_test(True)
    def test_https_conjurrc_is_created_with_no_parameters_given(self):
        with patch('builtins.input', side_effect=[self.client_params.hostname, 'yes', 'someotheraccount']):
            self.setup_cli_params({})
            self.invoke_cli(self.cli_auth_params,
                            ['init'])

            with open(f"{DEFAULT_CONFIG_FILE}", 'r') as conjurrc:
                lines = conjurrc.readlines()
                assert "---" in lines[0]
                assert "account: someotheraccount" in lines[1]
                assert f"appliance_url: {self.client_params.hostname}" in lines[2]
