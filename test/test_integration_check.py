# -*- coding: utf-8 -*-

"""
CLI Check Integration tests
This test file handles the main test flows for the check command
"""
from contextlib import redirect_stderr
import io
import os
from unittest.mock import patch

import sys
from conjur.constants import LOGIN_IS_REQUIRED
from test.util.test_infrastructure import integration_test
from test.util.test_runners.integration_test_case import IntegrationTestCaseBase
from test.util import test_helpers as utils


# Not coverage tested since integration tests don't run in
# the same build step
class CliIntegrationTestCheck(IntegrationTestCaseBase):  # pragma: no cover
    capture_stream = io.StringIO()

    def __init__(self, testname, client_params=None, environment_params=None):
        super(CliIntegrationTestCheck, self).__init__(testname, client_params, environment_params)

    # *************** HELPERS ***************

    def setUp(self):
        self.setup_cli_params({})
        # Used to configure the CLI and login to run tests
        utils.setup_cli(self)
        return self.invoke_cli(self.cli_auth_params,
                               ['policy', 'replace', '-b', 'root', '-f', self.environment.path_provider.get_policy_path("check")])

    # *************** TESTS ***************

    @integration_test()
    def test_check_default_role_get_insecure_prints_warning_in_log(self):
        with self.assertLogs('', level='DEBUG') as mock_log:
            self.invoke_cli(self.cli_auth_params,
                                     ['--insecure', 'check', '-i', 'dev:variable:somevariable', '-p', 'read'])
            self.assertIn("Warning: Running the command with '--insecure' makes your system vulnerable to security attacks",
                          str(mock_log.output))

    @integration_test()
    def test_check_specified_role_get_insecure_prints_warning_in_log(self):
        with self.assertLogs('', level='DEBUG') as mock_log:
            self.invoke_cli(self.cli_auth_params,
                                     ['--insecure', 'check', '-i', 'dev:variable:somevariable', '-p', 'read', '-r', 'dev:user:permitted_user'])
            self.assertIn("Warning: Running the command with '--insecure' makes your system vulnerable to security attacks",
                          str(mock_log.output))

    @integration_test()
    def test_check_without_id_returns_help(self):
        with redirect_stderr(self.capture_stream):
            self.invoke_cli(self.cli_auth_params,
                            ['check'], exit_code=1)
        self.assertIn("Error the following arguments are required:", self.capture_stream.getvalue())

    @integration_test(True)
    def test_check_short_with_help_returns_check_help(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['check', '-h'])
        self.assertIn("Name:\n  check", output)

    @integration_test(True)
    def test_check_long_with_help_returns_check_help(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['check', '--help'])
        self.assertIn("Name:\n  check", output)

    '''
    Tests to check for a privilege on a resource with a default role
    '''
    @integration_test()
    def test_check_privilege_on_a_resource_with_unprivileged_default_nonadmin_user(self):
        # log in as an unprivileged non-admin default user
        unprivileged_api_key = self.invoke_cli(self.cli_auth_params,
                                               ['user', 'rotate-api-key', '-i', 'unprivileged_nonadmin_user'])
        extract_api_key_from_message = unprivileged_api_key.split(":")[1].strip()
        self.invoke_cli(self.cli_auth_params,
                        ['login', '-i', 'unprivileged_nonadmin_user', '-p', extract_api_key_from_message])

        # verify that a nonadmin, unprivileged user does not have read access on resource
        output1 = self.invoke_cli(self.cli_auth_params,
                                 ['check', '-i', 'dev:variable:somevariable', '-p', 'read'])
        self.assertIn(output1, "false\n")

        # verify that a nonadmin, unprivileged user does not have [non-existent] access on resource 
        output2 = self.invoke_cli(self.cli_auth_params,
                                 ['check', '-i', 'dev:variable:somevariable', '-p', 'fakeprivilege'])
        self.assertIn(output2, "false\n")

    @integration_test()
    def test_check_privilege_on_a_resource_with_privileged_default_nonadmin_user(self):
        # log in as a privileged non-admin default user
        privileged_api_key = self.invoke_cli(self.cli_auth_params,
                                               ['user', 'rotate-api-key', '-i', 'privileged_nonadmin_user'])
        extract_api_key_from_message = privileged_api_key.split(":")[1].strip()
        self.invoke_cli(self.cli_auth_params,
                        ['login', '-i', 'privileged_nonadmin_user', '-p', extract_api_key_from_message])

        # verify that a nonadmin, privileged user has read access on resource
        output1 = self.invoke_cli(self.cli_auth_params,
                                 ['check', '-i', 'dev:variable:somevariable', '-p', 'read'])
        self.assertIn(output1, "true\n")

        # verify that a nonadmin, privileged user does not have [non-existent] access on resource 
        output2 = self.invoke_cli(self.cli_auth_params,
                                 ['check', '-i', 'dev:variable:somevariable', '-p', 'fakeprivilege'])
        self.assertIn(output2, "false\n")

    '''
    Tests to check for a privilege on a resource with a specified role
    '''
    @integration_test(True)
    def test_check_privilege_on_resource_with_specified_role(self):
        # verify that a permitted specified role has read access on resource
        output1 = self.invoke_cli(self.cli_auth_params,
                                 ['check', '-i', 'dev:variable:somevariable', '-p', 'read', '-r', 'dev:user:permitted_user'])
        self.assertIn(output1, "true\n")

        # verify that a permitted specified role does not have [non-existent] access on resource
        output2 = self.invoke_cli(self.cli_auth_params,
                                 ['check', '-i', 'dev:variable:somevariable', '-p', 'fakeprivilege', '-r', 'dev:host:permitted_host'])
        self.assertIn(output2, "false\n")

        # verify that a non permitted specified role does not have read access on resource
        output3 = self.invoke_cli(self.cli_auth_params,
                                 ['check', '-i', 'dev:variable:somevariable', '-p', 'read', '-r', 'dev:user:non_permitted_user'])
        self.assertIn(output3, "false\n")

    '''
    Validates that when the user isn't logged in and makes a request,
    they are prompted to login first and then the command is executed
    '''
    @integration_test()
    @patch('builtins.input', return_value='admin')
    def test_check_without_user_logged_in_prompts_login_and_performs_check_with_valid_commands(self, mock_input):
        # TEST_ENV is set to False so we will purposely be prompted to login
        os.environ['TEST_ENV'] = 'False'
        try:
            utils.delete_credentials()
        except OSError:
            pass

        with patch('getpass.getpass', return_value=self.client_params.env_api_key):
            output = self.invoke_cli(self.cli_auth_params,
                                     ['check', '-i', 'dev:variable:somevariable', '-p', 'read'])

            self.assertIn(LOGIN_IS_REQUIRED, output)
            self.assertIn("Successfully logged in to Conjur", output)
            expected_output = 'To start using the CLI, log in to Conjur\nSuccessfully logged in to Conjur\ntrue\n'
            self.assertIn(output, expected_output)
        os.environ['TEST_ENV'] = 'True'
