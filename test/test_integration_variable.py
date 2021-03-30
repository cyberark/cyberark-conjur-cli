# -*- coding: utf-8 -*-

"""
CLI Variable Integration tests
This test file handles the main test flows for the variable command
"""
import io
import json
import os
import tempfile
import uuid
from contextlib import redirect_stderr
from unittest.mock import patch

from conjur.constants import DEFAULT_NETRC_FILE
from test.util.test_infrastructure import integration_test
from test.util.test_runners.integration_test_case import IntegrationTestCaseBase
from test.util import test_helpers as utils


# Not coverage tested since integration tests don't run in
# the same build step
class CliIntegrationTestVariable(IntegrationTestCaseBase):  # pragma: no cover
    DEFINED_VARIABLE_ID = 'one/password'
    capture_stream = io.StringIO()
    def __init__(self, testname, client_params=None, environment_params=None):
        super(CliIntegrationTestVariable, self).__init__(testname, client_params, environment_params)

    # *************** HELPERS ***************

    def setup_cli_params(self, env_vars, *params):
        self.cli_auth_params = ['--debug']
        self.cli_auth_params += params
        return self.cli_auth_params

    def setUp(self):
        self.setup_cli_params({})
        # Used to configure the CLI and login to run tests
        utils.setup_cli(self)
        return self.invoke_cli(self.cli_auth_params,
                               ['policy', 'replace', '-b', 'root', '-f', self.environment.path_provider.get_policy_path("initial")])

    # *************** TESTS ***************

    @integration_test()
    def test_variable_get_insecure_prints_warning_in_log(self):
        with self.assertLogs('', level='DEBUG') as mock_log:
            expected_value = uuid.uuid4().hex
            utils.set_variable(self, 'one/password', expected_value)
            self.invoke_cli(self.cli_auth_params,
                                     ['--insecure', 'variable', 'get', '-i', 'one/password'])
            self.assertIn("Warning: Running the command with '--insecure' makes your system vulnerable to security attacks",
                          str(mock_log.output))

    @integration_test()
    def test_variable_long_version_return_latest_value(self):
        """
        Note about version tests, the Conjur server only keeps a certain number of versions.
        With each run of the integration tests, version tests are resetting variable values
        making, after a certain number of runs, version=1 not valid and fail
        Therefore, the variable name needs to be a random string so that the version
        will still be accessible
        """
        variable_name = "someversionedvar" + uuid.uuid4().hex
        policy = f"- !variable {variable_name}"
        utils.load_policy_from_string(self, policy)

        expected_value = "anothersecret"
        utils.set_variable(self, variable_name, expected_value)
        output = self.invoke_cli(self.cli_auth_params,
                                 ['variable', 'get', '-i', variable_name, '--version', '1'])
        self.assertIn(expected_value, output.strip())

    @integration_test()
    def test_variable_different_version_calls_returns_different_versions(self):
        variable_name = "someversionedsecret" + uuid.uuid4().hex
        policy = f"- !variable {variable_name}"
        utils.load_policy_from_string(self, policy)

        first_version = "first_secret"
        utils.set_variable(self, variable_name, first_version)

        output = self.invoke_cli(self.cli_auth_params,
                                 ['variable', 'get', '-i', variable_name, '--version', '1'])
        self.assertIn(first_version, output.strip())

        second_version = "second_secret"
        utils.set_variable(self, variable_name, second_version)
        output = self.invoke_cli(self.cli_auth_params,
                                 ['variable', 'get', '-i', variable_name, '--version', '2'])
        self.assertIn(second_version, output.strip())

    @integration_test()
    def test_variable_set_insecure_prints_warning_in_log(self):
        with self.assertLogs('', level='DEBUG') as mock_log:
            expected_value = uuid.uuid4().hex
            self.invoke_cli(self.cli_auth_params,
                       ['--insecure', 'variable', 'set', '-i',  'one/password', '-v', expected_value])

            self.assertIn("Warning: Running the command with '--insecure' makes your system vulnerable to security attacks",
                          str(mock_log.output))

    @integration_test(True)
    def test_variable_without_subcommand_returns_help(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['variable'])
        self.assertIn("Usage:\n  conjur [global options] <command> <subcommand> [options] [args]", output)

    @integration_test(True)
    def test_variable_short_with_help_returns_variable_help(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['variable', '-h'])
        self.assertIn("Name:\n  variable", output)

    @integration_test(True)
    def test_variable_long_with_help_returns_variable_help(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['variable', '--help'])
        self.assertIn("Name:\n  variable", output)

    # Note that the redirect_stderr won't work with process testing, as we redirect err into STDOUT
    @integration_test()
    def test_variable_get_variable_without_subcommand_raises_error(self):
        with redirect_stderr(self.capture_stream):
            output = self.invoke_cli(self.cli_auth_params,
                                     ['variable', '-i', 'somevariable'], exit_code=1)

        self.assertIn("Error argument action: invalid choice: 'somevariable'", self.capture_stream.getvalue())
        self.assertIn("Name:\n  variable", output)

    @integration_test(True)
    def test_variable_get_long_variable_returns_variable_value(self):
        expected_value = uuid.uuid4().hex
        utils.set_variable(self, 'one/password', expected_value)
        output = self.invoke_cli(self.cli_auth_params,
                                 ['variable', 'get', '--id=one/password'])
        self.assertIn(expected_value, output)

    @integration_test(True)
    def test_variable_get_short_variable_returns_variable_value(self):
        expected_value = uuid.uuid4().hex
        utils.set_variable(self, 'one/password', expected_value)
        output = self.invoke_cli(self.cli_auth_params,
                                 ['variable', 'get', '-i', 'one/password'])
        self.assertIn(expected_value, output)

    @integration_test(True)
    def test_variable_get_with_special_chars_returns_special_chars(self):
        self.invoke_cli(self.cli_auth_params,
                       ['policy', 'replace', '-b', 'root', '-f', self.environment.path_provider.get_policy_path("variable")])
        utils.set_variable(self, 'variablespecialchars', '"[]{}#@^&<>~\/''\/?\;\';\'"')
        output = utils.get_variable(self, 'variablespecialchars')
        self.assertIn('"[]{}#@^&<>~\/''\/?\;\';\'"', output.strip())

    @integration_test(True)
    def test_variable_get_variable_has_spaces_returns_variable_value(self):
        self.invoke_cli(self.cli_auth_params,
                       ['policy', 'replace', '-b', 'root', '-f', self.environment.path_provider.get_policy_path("variable")])
        utils.assert_set_and_get(self, "some variable with spaces")

    @integration_test(True)
    def test_unknown_variable_raises_not_found_error(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['variable', 'get', '-i', 'unknown'], exit_code=1)
        self.assertRegex(output, "404 Client Error: Not Found for url:")

    @integration_test()
    def test_cli_can_batch_get_multiple_variables(self):
        policy, variables = utils.generate_policy_string()
        file_name=os.path.join(tempfile.gettempdir(), os.urandom(24).hex())
        with open(file_name, 'w+b') as temp_policy_file:
            temp_policy_file.write(policy.encode('utf-8'))
            temp_policy_file.flush()

            utils.load_policy(self, temp_policy_file.name)
        value_map = {}
        for variable in variables:
            value = uuid.uuid4().hex
            utils.set_variable(self, variable, value)
            value_map[variable] = value

        batch_result_string = utils.get_variable(self, *variables)
        batch_result = json.loads(batch_result_string)

        for variable_name, variable_value in value_map.items():
            self.assertIn(batch_result[variable_name], variable_value)

        os.remove(file_name)

    @integration_test(True)
    def test_batch_existing_and_nonexistent_variable_raises_error(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['variable', 'get', '-i', 'one/password', 'unknown'], exit_code=1)
        self.assertIn("404 Client Error", output)

    @integration_test(True)
    def test_batch_existing_and_nonexistent_variable_with_spaces_raises_error(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['variable', 'get', '-i', 'one/password', '"unknown password"'], exit_code=1)
        self.assertIn("404 Client Error", output)

    @integration_test(True)
    def test_subcommand_get_short_help_returns_help(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['variable', 'get', '-h'])
        self.assertIn("Name:\n  get", output)

    @integration_test(True)
    def test_subcommand_get_long_help_returns_help(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['variable', 'get', '--help'])
        self.assertIn("Name:\n  get", output)

    @integration_test()
    def test_variable_get_without_id_returns_help(self):
        with redirect_stderr(self.capture_stream):
            self.invoke_cli(self.cli_auth_params,
                            ['variable', 'get'], exit_code=1)
        self.assertIn("Error the following arguments are required:", self.capture_stream.getvalue())

    @integration_test()
    def test_variable_set_without_id_returns_help(self):
        with redirect_stderr(self.capture_stream):
            self.invoke_cli(self.cli_auth_params,
                            ['variable', 'set'], exit_code=1)
        self.assertIn("Error the following arguments are required:", self.capture_stream.getvalue())

    @integration_test()
    def test_subcommand_set_long_help_returns_help(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['variable', 'set', '--help'])
        self.assertIn("Name:\n  set", output)

    @integration_test(True)
    def test_subcommand_set_short_help_returns_help(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['variable', 'set', '-h'])
        self.assertIn("Name:\n  set", output)

    @integration_test()
    def test_subcommand_set_variable_without_value_returns_help(self):
        with redirect_stderr(self.capture_stream):
            self.invoke_cli(self.cli_auth_params,
                            ['variable', 'set', '-i', 'one/password'], exit_code=1)
        self.assertIn("Error the following arguments are required:", self.capture_stream.getvalue())

    @integration_test()
    def test_subcommand_set_variable_with_values_returns_help(self):
        with redirect_stderr(self.capture_stream):
            self.invoke_cli(self.cli_auth_params,
                            ['variable', 'set', '-i', 'one/password', '-v', 'somevalue', 'someothervalue'], exit_code=1)
        self.assertIn("Error unrecognized arguments: someothervalue", self.capture_stream.getvalue())

    '''
    Validates that when the user isn't logged in and makes a request,
    they are prompted to login first and then the command is executed
    '''
    @integration_test()
    @patch('builtins.input', return_value='admin')
    def test_variable_get_without_user_logged_in_prompts_login_and_performs_get(self, mock_input):
        # TEST_ENV is set to False so we will purposely be prompted to login
        os.environ['TEST_ENV'] = 'False'
        try:
            utils.delete_credentials()
        except OSError:
            pass

        with patch('getpass.getpass', return_value=self.client_params.env_api_key):
            output = self.invoke_cli(self.cli_auth_params,
                                     ['variable', 'set', '-i', 'one/password', '-v', 'somevalue'])

            self.assertIn("Error: You have not logged in", output)
            self.assertIn("Successfully logged in to Conjur", output)
            self.assertIn('Successfully set value for variable \'one/password\'', output)
        os.environ['TEST_ENV'] = 'True'

    @integration_test(True)
    def test_https_cli_can_set_and_get_a_defined_variable_if_verification_disabled(self):
        self.setup_cli_params({}, '--insecure')
        utils.assert_set_and_get(self, self.DEFINED_VARIABLE_ID)
