# -*- coding: utf-8 -*-

"""
CLI Show Integration tests
This test file handles the main test flows for the role command
"""
from contextlib import redirect_stderr
import io
import os
from unittest.mock import patch

from conjur.constants import LOGIN_IS_REQUIRED
from test.util.test_infrastructure import integration_test
from test.util.test_runners.integration_test_case import IntegrationTestCaseBase
from test.util import test_helpers as utils


# Not coverage tested since integration tests don't run in
# the same build step
class CliIntegrationTestShow(IntegrationTestCaseBase):  # pragma: no cover
    capture_stream = io.StringIO()

    def __init__(self, testname, client_params=None, environment_params=None):
        super(CliIntegrationTestShow, self).__init__(testname, client_params, environment_params)

    # *************** HELPERS ***************

    def setUp(self):
        self.setup_cli_params({})
        # Used to configure the CLI and login to run tests
        utils.setup_cli(self)
        return self.invoke_cli(self.cli_auth_params,
                               ['policy', 'replace', '-b', 'root', '-f', self.environment.path_provider.get_policy_path("list")])

    # *************** TESTS ***************

    @integration_test()
    def test_role_exists_insecure_prints_warning_in_log(self):
        with self.assertLogs('', level='DEBUG') as mock_log:
            self.invoke_cli(self.cli_auth_params,
                                     ['--insecure', 'role', 'exists', '-i', 'user:someuser'])
            self.assertIn("Warning: Running the command with '--insecure' makes your system vulnerable to security attacks",
                          str(mock_log.output))

    @integration_test()
    def test_role_without_action_returns_usage(self):
        output = self.invoke_cli(self.cli_auth_params,
                            ['role'])
        self.assertIn("Usage:\n  conjur", output)

    @integration_test(True)
    def test_role_short_with_help_returns_role_help(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['role', '-h'])
        self.assertIn("Name:\n  role", output)

    @integration_test(True)
    def test_role_long_with_help_returns_role_help(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['role', '--help'])
        self.assertIn("Name:\n  role", output)

    @integration_test(True)
    def test_role_exists_short_with_help_returns_role_exists_help(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['role', 'exists', '-h'])
        self.assertIn("Name:\n  exists", output)

    @integration_test(True)
    def test_role_exists_long_with_help_returns_role_exists_help(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['role', 'exists', '--help'])
        self.assertIn("Name:\n  exists", output)

    @integration_test()
    def test_role_exists_without_id_returns_help(self):
        with redirect_stderr(self.capture_stream):
            self.invoke_cli(self.cli_auth_params,
                            ['role', 'exists'], exit_code=1)
        self.assertIn("Error the following arguments are required:", self.capture_stream.getvalue())

    @integration_test()
    def test_role_exists_without_prefix_returns_help(self):
        with redirect_stderr(self.capture_stream):
            self.invoke_cli(self.cli_auth_params,
                            ['role', 'exists', '-i', 'someuser'], exit_code=1)
        self.assertIn("Error the following arguments are required:", self.capture_stream.getvalue())

    @integration_test(True)
    def test_role_exists_long_role_id_returns_result(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['role', 'exists', '--id=user:someuser'])
        self.assertIn('true', output)

    @integration_test(True)
    def test_role_exists_short_options_returns_result(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['role', 'exists', '-i', 'user:someuser'])
        self.assertIn('true', output)

    @integration_test(True)
    def test_role_exists_returns_false_if_not_exist(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['role', 'exists', '-i', 'user:fakeuser'])
        self.assertIn('false', output)

    @integration_test(True)
    def test_role_exists_host_returns_result(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['role', 'exists', '-i', 'host:anotherhost'])
        self.assertIn('true', output)

    @integration_test(True)
    def test_role_exists_layer_returns_result(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['role', 'exists', '-i', 'layer:somelayer'])
        self.assertIn('true', output)

    @integration_test(True)
    def test_role_exists_group_returns_result(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['role', 'exists', '-i', 'group:somegroup'])
        self.assertIn('true', output)

    @integration_test(True)
    def test_role_exists_policy_returns_result(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['role', 'exists', '-i', 'policy:root'])
        self.assertIn('true', output)


    '''
    Validates that when the user isn't logged in and makes a request,
    they are prompted to login first and then the command is executed
    '''
    @integration_test()
    @patch('builtins.input', return_value='admin')
    def test_role_exists_without_user_logged_in_prompts_login_and_performs_role_exists(self, mock_input):
        # TEST_ENV is set to False so we will purposely be prompted to login
        os.environ['TEST_ENV'] = 'False'
        try:
            utils.delete_credentials()
        except OSError:
            pass

        with patch('getpass.getpass', return_value=self.client_params.env_api_key):
            output = self.invoke_cli(self.cli_auth_params,
                                     ['role', 'exists', '-i', 'user:someuser'])

            self.assertIn(LOGIN_IS_REQUIRED, output)
            self.assertIn("Successfully logged in to Conjur", output)
            self.assertIn('true', output)
        os.environ['TEST_ENV'] = 'True'
