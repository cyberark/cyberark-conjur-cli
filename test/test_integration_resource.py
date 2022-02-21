# -*- coding: utf-8 -*-

"""
CLI Resource Integration tests

This test file handles the main test flows for the user/host command
"""
# Builtins
import io
import json
from contextlib import redirect_stderr
from unittest.mock import patch

# Internals
from conjur.data_object import ConjurrcData
from conjur.logic.credential_provider import CredentialStoreFactory
from test.util.test_infrastructure import integration_test
from test.util.test_runners.integration_test_case import IntegrationTestCaseBase
from test.util import test_helpers as utils

# Not coverage tested since integration tests doesn't run in
# the same build step
class CliIntegrationResourceTest(IntegrationTestCaseBase):  # pragma: no cover
    capture_stream = io.StringIO()
    def __init__(self, testname, client_params=None, environment_params=None):
        super(CliIntegrationResourceTest, self).__init__(testname, client_params, environment_params)

    # *************** HELPERS ***************

    def setUp(self):
        self.setup_cli_params({})
        utils.delete_credentials()
        # Need to configure the CLI and login to perform further commands
        utils.setup_cli(self)
        self.invoke_cli(self.cli_auth_params,
                        ['policy', 'replace', '-b', 'root', '-f', self.environment.path_provider.get_policy_path("resource")])

    # *************** TESTS ***************

#    @integration_test()
#    def test_resource_insecure_prints_warning_in_log(self):
#        some_user_api_key = self.invoke_cli(self.cli_auth_params,
#                                            ['user', 'rotate-api-key', '-i', 'someuser'])

#        extract_api_key_from_message = some_user_api_key.split(":")[1].strip()
#        self.invoke_cli(self.cli_auth_params,
#                        ['login', '-i', 'someuser', '-p', extract_api_key_from_message])

#        with self.assertLogs('', level='DEBUG') as mock_log:
#            self.invoke_cli(self.cli_auth_params,
#                            ['--insecure', 'user', 'rotate-api-key'])

#            self.assertIn("Warning: Running the command with '--insecure' makes your system vulnerable to security attacks",
#                          str(mock_log.output))

    @integration_test(True)
    def test_host_rotate_api_key_without_host_prompts_input(self):
        with patch('builtins.input', side_effect=['somehost']):
            output = self.invoke_cli(self.cli_auth_params,
                                     ['host', 'rotate-api-key'])
            self.assertIn("Successfully rotated API key for 'somehost'", output)

    @integration_test(True)
    def test_host_insecure_rotate_api_key_without_host_prompts_input(self):
        self.setup_insecure()
        with patch('builtins.input', side_effect=['somehost']):
            output = self.invoke_cli(self.cli_auth_params,
                                     ['host', 'rotate-api-key'])
            self.assertIn("Successfully rotated API key for 'somehost'", output)

    @integration_test(True)
    def test_host_rotate_api_key_with_host_provided_rotates_host_api_key(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['host', 'rotate-api-key', '-i', 'somehost'])
        self.assertIn("Successfully rotated API key for 'somehost'", output)

    @integration_test()
    def test_host_rotate_api_key_without_flag_returns_error(self):
        with redirect_stderr(self.capture_stream):
            self.invoke_cli(self.cli_auth_params,
                            ['host', 'rotate-api-key', 'someinput'], exit_code=1)
        self.assertIn('Error unrecognized arguments: someinput', self.capture_stream.getvalue())

    @integration_test()
    def test_host_rotate_api_key_flag_without_value_returns_error(self):
        with redirect_stderr(self.capture_stream):
            self.invoke_cli(self.cli_auth_params,
                            ['host', 'rotate-api-key', '-i'], exit_code=1)
        self.assertIn('Error', self.capture_stream.getvalue())
