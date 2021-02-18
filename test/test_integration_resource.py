# -*- coding: utf-8 -*-

"""
CLI Resource Integration tests

This test file handles the main test flows for the user/host command
"""
# Builtins
import io
from contextlib import redirect_stderr
from unittest.mock import patch

# Internals
from conjur.constants import DEFAULT_NETRC_FILE
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

    def setup_cli_params(self, env_vars, *params):
        self.cli_auth_params = ['--debug']
        self.cli_auth_params += params

        return self.cli_auth_params

    def setUp(self):
        self.setup_cli_params({})
        # Need to configure the CLI and login to perform further commands
        utils.setup_cli(self)
        self.invoke_cli(self.cli_auth_params,
                        ['policy', 'replace', '-b', 'root', '-f', self.environment.path_provider.get_policy_path("resource")])

    # *************** TESTS ***************

    @integration_test()
    def test_resource_insecure_prints_warning_in_log(self):
        some_user_api_key = self.invoke_cli(self.cli_auth_params,
                                            ['user', 'rotate-api-key', '-i', 'someuser'])

        extract_api_key_from_message = some_user_api_key.split(":")[1].strip()
        self.invoke_cli(self.cli_auth_params,
                        ['login', '-i', 'someuser', '-p', extract_api_key_from_message])

        with self.assertLogs('', level='DEBUG') as mock_log:
            self.invoke_cli(self.cli_auth_params,
                            ['--insecure', 'user', 'rotate-api-key'])

            self.assertIn("Warning: Running the command with '--insecure' makes your system vulnerable to security attacks",
                          str(mock_log.output))

    @integration_test()
    def test_user_rotate_api_key_without_param_rotates_logged_in_user(self):
        some_user_api_key = self.invoke_cli(self.cli_auth_params,
                                            ['user', 'rotate-api-key', '-i', 'someuser'])
        # extract the API key from the returned message
        extract_api_key_from_message = some_user_api_key.split(":")[1].strip()

        self.invoke_cli(self.cli_auth_params,
                        ['login', '-i', 'someuser', '-p', extract_api_key_from_message])

        with open(f"{DEFAULT_NETRC_FILE}", "r") as netrc_test:
            for line in netrc_test.readlines():
                if line.strip().find('password') == 0:
                    # extract the password from the netrc
                    old_api_key = line.split(" ")[1]

        some_user_api_key = self.invoke_cli(self.cli_auth_params,
                                            ['user', 'rotate-api-key'])
        extract_api_key_from_message = some_user_api_key.split(":")[1].strip()

        assert old_api_key != extract_api_key_from_message, "the API keys are the same!"

        with open(f"{DEFAULT_NETRC_FILE}", "r") as netrc_test:
            for line in netrc_test.readlines():
                if line.strip().find('password') == 0:
                    new_api_key = line.split(" ")[1]

        assert new_api_key.strip() == extract_api_key_from_message, "the API keys are not the same!"

    @integration_test()
    def test_user_rotate_api_key_with_user_provided_rotates_user_api_key(self):
        some_user_api_key = self.invoke_cli(self.cli_auth_params,
                                            ['user', 'rotate-api-key', '-i', 'someuser'])
        extract_api_key_from_message = some_user_api_key.split(":")[1].strip()

        self.assertIn("Successfully rotated API key for 'someuser'", some_user_api_key)

        # verify user can login with their new API key
        self.invoke_cli(self.cli_auth_params,
                        ['login', '-i', 'someuser', '-p', extract_api_key_from_message])

    '''
    Validates that an unprivileged user cannot rotate another user's API key.
    1. Rotate user's API key (using the admin's access token) to be able to login as them
    2. Login as that user and attempt to rotate another's API key
    '''
    @integration_test()
    def test_unprivileged_user_cannot_rotate_anothers_api_key(self):
        unprivileged_api_key = self.invoke_cli(self.cli_auth_params,
                                               ['user', 'rotate-api-key', '-i', 'someunprivilegeduser'])
        # extract the API key we get from the CLI success message
        extract_api_key_from_message = unprivileged_api_key.split(":")[1].strip()
        print(extract_api_key_from_message)
        # verify user can login with their new API key
        self.invoke_cli(self.cli_auth_params,
                        ['login', '-i', 'someunprivilegeduser', '-p', extract_api_key_from_message])

        # Verify that an unprivileged user cannot rotate an another's API key
        attempt_to_rotate_user_key = self.invoke_cli(self.cli_auth_params,
                                                     ['user', 'rotate-api-key', '-i', 'someuser'], exit_code=1)
        self.assertIn("401 Client Error", attempt_to_rotate_user_key)

        # Verify that a user cannot rotate an admin's API key
        attempt_to_rotate_admin_key = self.invoke_cli(self.cli_auth_params,
                                                      ['user', 'rotate-api-key', '-i', 'admin'], exit_code=1)
        self.assertIn("500 Server Error", attempt_to_rotate_admin_key)

    @integration_test()
    def test_user_rotate_api_key_without_flag_returns_error(self):
        with redirect_stderr(self.capture_stream):
            self.invoke_cli(self.cli_auth_params,
                            ['user', 'rotate-api-key', 'someinput'], exit_code=1)
        self.assertIn('Error unrecognized arguments: someinput', self.capture_stream.getvalue())

    @integration_test()
    def test_user_rotate_api_key_flag_without_value_returns_error(self):
        with redirect_stderr(self.capture_stream):
            self.invoke_cli(self.cli_auth_params,
                            ['user', 'rotate-api-key', '-i'], exit_code=1)
        self.assertIn('Error argument -i/--id', self.capture_stream.getvalue())

    def test_logged_in_user_rotate_api_key_with_their_user_as_flag_returns_error(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['user', 'rotate-api-key', '-i', 'admin'])
        self.assertIn("Error: To rotate the API key of the currently logged-in user use this command without any flags or options", output)

    @integration_test()
    def test_user_change_password_does_not_provide_password_prompts_input(self):
        # Login as user to avoid changing admin password
        with patch('getpass.getpass', side_effect=['Mypassw0rD2\!']):
            some_user_api_key = self.invoke_cli(self.cli_auth_params,
                                                ['user', 'rotate-api-key', '-i', 'someuser'])

            extract_api_key_from_message = some_user_api_key.split(":")[1].strip()
            self.invoke_cli(self.cli_auth_params,
                            ['login', '-i', 'someuser', '-p', extract_api_key_from_message])
            output = self.invoke_cli(self.cli_auth_params,
                                     ['user', 'change-password'])
        self.assertIn("Successfully changed password for", output)

    @integration_test(True)
    def test_user_change_password_not_complex_enough_prompts_input(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['user', 'change-password', '-p', 'someinvalidpassword'], exit_code=1)
        self.assertIn("Error: Invalid password", output)

    @integration_test()
    def test_user_change_password_meets_password_complexity(self):
        # Login as user to avoid changing admin password
        some_user_api_key = self.invoke_cli(self.cli_auth_params,
                                            ['user', 'rotate-api-key', '-i', 'someuser'])

        extract_api_key_from_message = some_user_api_key.split(":")[1].strip()
        self.invoke_cli(self.cli_auth_params,
                        ['login', '-i', 'someuser', '-p', extract_api_key_from_message])
        output = self.invoke_cli(self.cli_auth_params,
                                 ['user', 'change-password', '-p', 'Mypassw0rD2\!'])
        self.assertIn("Successfully changed password for", output)

    @integration_test()
    def test_user_change_password_empty_password_provided_prompts_input(self):
        with self.assertLogs('', level='DEBUG') as mock_log:
            with patch('getpass.getpass', side_effect=['mypassword']):
                output = self.invoke_cli(self.cli_auth_params,
                                         ['user', 'change-password'], exit_code=1)

        self.assertIn("Error: Invalid password", str(mock_log.output))
        self.assertIn("Error: Invalid password", output)

    @integration_test(True)
    def test_host_rotate_api_key_without_host_prompts_input(self):
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
