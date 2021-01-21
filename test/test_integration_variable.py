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

import Utils
from conjur.constants import DEFAULT_NETRC_FILE
from test.util.cli_helpers import integration_test
from test.util.test_runners.integration_test_case import IntegrationTestCaseBase
from Utils import py_utils as utils

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
        Utils.setup_cli(self)
        return self.invoke_cli(self.cli_auth_params,
                               ['policy', 'replace', '-b', 'root', '-f', self.environment.path_provider.get_policy_path("initial")])

    # *************** TESTS ***************
    # note: this will not work with a process as the log redirect will not work
    @integration_test()
    def test_variable_get_insecure_prints_warning_in_log(self):
        with self.assertLogs('', level='DEBUG') as mock_log:
            expected_value = uuid.uuid4().hex
            Utils.set_variable(self, 'one/password', expected_value)
            self.invoke_cli(self.cli_auth_params,
                                     ['--insecure', 'variable', 'get', '-i', 'one/password'])
            self.assertIn("Warning: Running the command with '--insecure' makes your system vulnerable to security attacks",
                          str(mock_log.output))
    @integration_test(True)
    def test_variable_short_version_return_latest_value(self):
        policy = "- !variable someversionedsecret"
        Utils.load_policy_from_string(self, policy)

        expected_value = "somesecret"
        Utils.set_variable(self, 'someversionedsecret', expected_value)
        output = self.invoke_cli(self.cli_auth_params,
                                 ['variable', 'get', '-i', 'someversionedsecret', '-v', '1'])
        self.assertIn(expected_value, output)

    # TODO why it's not pass when running as a process
    @integration_test()
    def test_variable_long_version_return_latest_value(self):
        policy = "- !variable someotherversionedsecret"
        Utils.load_policy_from_string(self, policy)

        expected_value = "somesecret"
        Utils.set_variable(self, 'someotherversionedsecret', expected_value)
        output = self.invoke_cli(self.cli_auth_params,
                                 ['variable', 'get', '-i', 'someotherversionedsecret', '--version', '1'])
        self.assertIn(expected_value, output)

    @integration_test()
    def test_variable_different_version_calls_returns_different_versions(self):
        policy = "- !variable someotherversionedsecret"
        Utils.load_policy_from_string(self, policy)

        first_version = "first_secret"
        Utils.set_variable(self, 'someotherversionedsecret', first_version)

        second_version = "second_secret"
        Utils.set_variable(self, 'someotherversionedsecret', second_version)
        output = self.invoke_cli(self.cli_auth_params,
                                 ['variable', 'get', '-i', 'someotherversionedsecret', '--version', '1'])
        self.assertIn(first_version, output)
        output = self.invoke_cli(self.cli_auth_params,
                                 ['variable', 'get', '-i', 'someotherversionedsecret', '--version', '2'])
        self.assertIn(second_version, output)

    # note: this will not work with a process as the log redirect will not work
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

    # TODO This will need to be changed when UX is finalized
    @integration_test(True)
    def test_variable_short_with_help_returns_variable_help(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['variable', '-h'])
        self.assertIn("usage:  variable", output)

    # TODO This will need to be changed when UX is finalized
    @integration_test(True)
    def test_variable_long_with_help_returns_variable_help(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['variable', '--help'])
        self.assertIn("usage:  variable", output)

    # note that the redirect_stderr won't work with process testing, as we redirect err into stdout
    @integration_test()
    def test_variable_get_variable_without_subcommand_raises_error(self):
        with redirect_stderr(self.capture_stream):
            output = self.invoke_cli(self.cli_auth_params,
                                     ['variable', '-i', 'somevariable'], exit_code=1)

        self.assertIn("Error argument action: invalid choice: 'somevariable'", self.capture_stream.getvalue())
        self.assertIn("usage:  variable", output)

    @integration_test(True)
    def test_variable_get_long_variable_returns_variable_value(self):
        expected_value = uuid.uuid4().hex
        Utils.set_variable(self, 'one/password', expected_value)
        output = self.invoke_cli(self.cli_auth_params,
                                 ['variable', 'get', '--id=one/password'])
        self.assertIn(expected_value, output)

    @integration_test(True)
    def test_variable_get_short_variable_returns_variable_value(self):
        expected_value = uuid.uuid4().hex
        Utils.set_variable(self, 'one/password', expected_value)
        output = self.invoke_cli(self.cli_auth_params,
                                 ['variable', 'get', '-i', 'one/password'])
        self.assertIn(expected_value, output)

    @integration_test(True)
    def test_variable_get_with_special_chars_returns_special_chars(self):
        self.invoke_cli(self.cli_auth_params,
                       ['policy', 'replace', '-b', 'root', '-f', self.environment.path_provider.get_policy_path("variable")])
        Utils.set_variable(self, 'variablespecialchars', '"[]{}#@^&<>~\/''\/?\;\';\'"')
        output = Utils.get_variable(self, 'variablespecialchars')
        self.assertIn( '"[]{}#@^&<>~\/''\/?\;\';\'"',output)

    @integration_test(True)
    def test_variable_get_variable_has_spaces_returns_variable_value(self):
        self.invoke_cli(self.cli_auth_params,
                       ['policy', 'replace', '-b', 'root', '-f', self.environment.path_provider.get_policy_path("variable")])
        Utils.assert_set_and_get(self, "some variable with spaces")

    @integration_test(True)
    def test_unknown_variable_raises_not_found_error(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['variable', 'get', '-i', 'unknown'], exit_code=1)
        self.assertRegex(output, "404 Client Error: Not Found for url:")

    #todo: why can't with process
    @integration_test()
    def test_cli_can_batch_get_multiple_variables(self):
        policy, variables = Utils.generate_policy_string(self)
        file_name=os.path.join(tempfile.gettempdir(), os.urandom(24).hex())
        with open(file_name, 'w+b') as temp_policy_file:
            temp_policy_file.write(policy.encode('utf-8'))
            temp_policy_file.flush()

            Utils.load_policy(self, temp_policy_file.name)
        value_map = {}
        for variable in variables:
            value = uuid.uuid4().hex
            Utils.set_variable(self, variable, value)
            value_map[variable] = value

        batch_result_string = Utils.get_variable(self, *variables)
        batch_result = json.loads(batch_result_string)

        for variable_name, variable_value in value_map.items():
            self.assertEquals(variable_value, batch_result[variable_name])

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

    # TODO This will need to be changed when UX is finalized
    @integration_test(True)
    def test_subcommand_get_short_help_returns_help(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['variable', 'get', '-h'])
        self.assertIn("usage: variable", output)

    # TODO This will need to be changed when UX is finalized
    @integration_test(True)
    def test_subcommand_get_long_help_returns_help(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['variable', 'get', '--help'])
        self.assertIn("usage: variable", output)

    # note that the redirect_stderr won't work with process testing, as we redirect err into stdout
    @integration_test()
    def test_variable_get_without_id_returns_help(self):
        with redirect_stderr(self.capture_stream):
            self.invoke_cli(self.cli_auth_params,
                            ['variable', 'get'], exit_code=1)
        self.assertIn("Error the following arguments are required:", self.capture_stream.getvalue())

    # note that the redirect_stderr won't work with process testing, as we redirect err into stdout
    @integration_test()
    def test_variable_set_without_id_returns_help(self):
        with redirect_stderr(self.capture_stream):
            self.invoke_cli(self.cli_auth_params,
                            ['variable', 'set'], exit_code=1)
        self.assertIn("Error the following arguments are required:", self.capture_stream.getvalue())

    # TODO This will need to be changed when UX is finalized
    # Todo check why fail with a process
    @integration_test()
    def test_subcommand_set_long_help_returns_help(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['variable', 'set', '--help'])
        self.assertIn("usage: variable set", output)

    # TODO This will need to be changed when UX is finalized
    @integration_test(True)
    def test_subcommand_set_short_help_returns_help(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['variable', 'set', '-h'])
        self.assertIn("usage: variable set", output)

    # note that the redirect_stderr won't work with process testing, as we redirect err into stdout
    # TODO This will need to be changed when UX is finalized
    @integration_test()
    def test_subcommand_set_variable_without_value_returns_help(self):
        with redirect_stderr(self.capture_stream):
            self.invoke_cli(self.cli_auth_params,
                            ['variable', 'set', '-i', 'one/password'], exit_code=1)
        self.assertIn("Error the following arguments are required:", self.capture_stream.getvalue())

    # note that the redirect_stderr won't work with process testing, as we redirect err into stdout
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
            utils.remove_file(DEFAULT_NETRC_FILE)
        except OSError:
            pass

        with patch('getpass.getpass', return_value=self.client_params.env_api_key):
            output = self.invoke_cli(self.cli_auth_params,
                                     ['variable', 'set', '-i', 'one/password', '-v', 'somevalue'])

            self.assertIn("Error: You have not logged in", output)
            self.assertIn("Successfully logged in to Conjur", output)
            self.assertIn('Successfully set value for variable \'one/password\'', output)
        os.environ['TEST_ENV'] = 'True'

    # todo why --insecure not working with process
    @integration_test(True)
    def test_https_cli_can_set_and_get_a_defined_variable_if_verification_disabled(self):
        self.setup_cli_params({}, '--insecure')
        Utils.assert_set_and_get(self, self.DEFINED_VARIABLE_ID)
