# -*- coding: utf-8 -*-

"""
CLI List Integration tests

This test file handles the main test flows for the list command
"""
import io
import os
import shutil
from contextlib import redirect_stderr

from conjur.constants import DEFAULT_CONFIG_FILE
from test.util.test_infrastructure import integration_test
from test.util.test_runners.integration_test_case import IntegrationTestCaseBase
from test.util import test_helpers as utils


# Not coverage tested since integration tests doesn't run in
# the same build step
class CliIntegrationTestList(IntegrationTestCaseBase):  # pragma: no cover
    def __init__(self, testname, client_params=None, environment_params=None):
        super(CliIntegrationTestList, self).__init__(testname, client_params, environment_params)

    # *************** HELPERS ***************

    def setUp(self):
        self.setup_cli_params({})
        # Used to configure the CLI and login to run tests
        utils.setup_cli(self)
        self.invoke_cli(self.cli_auth_params,
                       ['policy', 'replace', '-b', 'root', '-f', self.environment.path_provider.get_policy_path("list")])

    # *************** TESTS ***************

    @integration_test()
    def test_list_without_valid_conjurrc_raises_config_exception(self):
        os.remove(DEFAULT_CONFIG_FILE)
        shutil.copy(self.environment.path_provider.test_missing_account_conjurrc, self.environment.path_provider.conjurrc_path)

        with self.assertRaises(AssertionError):
            self.invoke_cli(self.cli_auth_params, ['list'])

    @integration_test()
    def test_list_returns_resources(self):
        output = self.invoke_cli(self.cli_auth_params, ['list'])
        self.assertIn(f'[\n    "{self.client_params.account}:policy:root",\n'
                      f'    "{self.client_params.account}:user:someuser",\n'
                      f'    "{self.client_params.account}:layer:somelayer",\n'
                      f'    "{self.client_params.account}:group:somegroup",\n'
                      f'    "{self.client_params.account}:host:anotherhost",\n'
                      f'    "{self.client_params.account}:variable:one/password",\n'
                      f'    "{self.client_params.account}:webservice:somewebservice"\n]\n', output)

    @integration_test(True)
    def test_list_help_returns_help_screen(self):
        output = self.invoke_cli(self.cli_auth_params, ['list', '-h'])
        self.assertIn("Name:\n  list", output)

    @integration_test(True)
    def test_list_inspect_user_returns_info_on_user(self):
        self.invoke_cli(self.cli_auth_params,
               ['policy', 'replace', '-b', 'root', '-f', self.environment.path_provider.get_policy_path("conjur")])
        output = self.invoke_cli(self.cli_auth_params, ['list', '--inspect', '--kind', 'user'])
        self.assertIn(f'        "id": "{self.client_params.account}:user:someuser",\n'
                      f'        "owner": "{self.client_params.account}:user:admin",\n'
                      f'        "policy": "{self.client_params.account}:policy:root",\n'
                      f'        "permissions": [],\n'
                      f'        "annotations": [],\n'
                      f'        "restricted_to": []\n'
                      f'    }}\n'
                      f']\n', output)

    @integration_test()
    def test_list_kind_layer_returns_layers(self):
        with self.assertLogs('', level='DEBUG') as mock_log:
            output = self.invoke_cli(self.cli_auth_params, ['list', '-k', 'layer'])
            self.assertIn(f'[\n    "{self.client_params.account}:layer:somelayer"\n]\n',output)
            self.assertIn("Executing list command with the following constraints: {'kind': 'layer'}",
                          str(mock_log.output))

    @integration_test(True)
    def test_list_kind_user_returns_users(self):
        output = self.invoke_cli(self.cli_auth_params, ['list', '-k', 'user'])
        self.assertIn(f'[\n    "{self.client_params.account}:user:someuser"\n]\n', output)

    @integration_test(True)
    def test_list_kind_nonexistent_returns_empty_list(self):
        output = self.invoke_cli(self.cli_auth_params, ['list', '-k', 'nonexistentkind'])
        self.assertIn(f'[]\n', output)

    @integration_test(True)
    def test_list_kind_variable_returns_variables(self):
        output = self.invoke_cli(self.cli_auth_params, ['list', '-k', 'variable'])
        self.assertIn(f'[\n    "{self.client_params.account}:variable:one/password"\n]\n', output)

    @integration_test(True)
    def test_list_kind_group_returns_groups(self):
        output = self.invoke_cli(self.cli_auth_params, ['list', '-k', 'group'])
        self.assertIn(f'[\n    "{self.client_params.account}:group:somegroup"\n]\n', output)

    @integration_test()
    def test_list_kind_policy_returns_policies(self):
        output = self.invoke_cli(self.cli_auth_params, ['list', '-k', 'policy'])
        self.assertIn(f'[\n    "{self.client_params.account}:policy:root"\n]\n', output)

    @integration_test()
    def test_list_kind_policy_returns_policies_insecure(self):
        self.setup_insecure()
        output = self.invoke_cli(self.cli_auth_params, ['list', '-k', 'policy'])
        self.assertIn(f'[\n    "{self.client_params.account}:policy:root"\n]\n', output)

    @integration_test()
    def test_list_kind_policy_returns_policies_insecure(self):
        self.setup_insecure()
        output = self.invoke_cli(self.cli_auth_params, ['list', '-k', 'policy'])
        self.assertIn(f'[\n    "{self.client_params.account}:policy:root"\n]\n', output)

    @integration_test(True)
    def test_list_kind_short_host_returns_hosts(self):
        output = self.invoke_cli(self.cli_auth_params, ['list', '-k', 'host'])
        self.assertIn(f'[\n    "{self.client_params.account}:host:anotherhost"\n]\n', output)

    @integration_test(True)
    def test_list_kind_long_host_returns_hosts(self):
        output = self.invoke_cli(self.cli_auth_params, ['list', '--kind=host'])
        self.assertIn(f'[\n    "{self.client_params.account}:host:anotherhost"\n]\n', output)

    @integration_test(True)
    def test_list_kind_webservice_returns_webservices(self):
        output = self.invoke_cli(self.cli_auth_params, ['list', '-k', 'webservice'])
        self.assertIn(f'[\n    "{self.client_params.account}:webservice:somewebservice"\n]\n', output)

    @integration_test()
    def test_list_insecure_list_prints_warning_in_log(self):
        with self.assertLogs('', level='DEBUG') as mock_log:
            self.invoke_cli(self.cli_auth_params, ['--insecure', 'list'])
            self.assertIn("Warning: Running the command with '--insecure' makes your system vulnerable to security attacks",
                str(mock_log.output))

    @integration_test()
    def test_list_limit_short_returns_same_number_of_resources(self):
        output = self.invoke_cli(self.cli_auth_params, ['list', '-l', '5'])
        self.assertIn(f'[\n    "{self.client_params.account}:group:somegroup",\n'
                      f'    "{self.client_params.account}:host:anotherhost",\n'
                      f'    "{self.client_params.account}:layer:somelayer",\n'
                      f'    "{self.client_params.account}:policy:root",\n'
                      f'    "{self.client_params.account}:user:someuser"\n]\n', output)

    @integration_test()
    def test_list_limit_long_returns_same_number_of_resources(self):
        output = self.invoke_cli(self.cli_auth_params, ['list', '--limit=5'])
        self.assertIn(f'[\n    "{self.client_params.account}:group:somegroup",\n'
                          f'    "{self.client_params.account}:host:anotherhost",\n'
                          f'    "{self.client_params.account}:layer:somelayer",\n'
                          f'    "{self.client_params.account}:policy:root",\n'
                          f'    "{self.client_params.account}:user:someuser"\n]\n', output)

    @integration_test(True)
    def test_list_limit_invalid_param_returns_empty_list(self):
        output = self.invoke_cli(self.cli_auth_params, ['list', '-l', '0'], exit_code=1)
        self.assertIn("500 Server Error", output)

    @integration_test(True)
    def test_list_limit_string_raises_error(self):
        output = self.invoke_cli(self.cli_auth_params, ['list', '-l', 'somestring'], exit_code=1)
        self.assertIn("500 Server Error", output)

    '''
    Validates that an invalid input (a negative number) raises an error 
    '''
    @integration_test(True)
    def test_list_limit_invalid_negative_param_raises_error(self):
        output = self.invoke_cli(self.cli_auth_params, ['list', '-l', '-5'], exit_code=1)
        self.assertIn("500 Server Error", output)

    @integration_test()
    def test_list_random_input_raises_error(self):
        capture_stream = io.StringIO()
        with redirect_stderr(capture_stream):
            self.invoke_cli(self.cli_auth_params, ['list', 'someinput'], exit_code=1)
        self.assertIn("Error unrecognized arguments", capture_stream.getvalue())

    @integration_test(True)
    def test_list_offset_short_returns_list_starting_at_param(self):
        output = self.invoke_cli(self.cli_auth_params, ['list', '-o', '2'])
        self.assertIn(f'[\n    "{self.client_params.account}:layer:somelayer",\n'
                      f'    "{self.client_params.account}:policy:root",\n'
                      f'    "{self.client_params.account}:user:someuser",\n'
                      f'    "{self.client_params.account}:variable:one/password",\n'
                      f'    "{self.client_params.account}:webservice:somewebservice"\n]\n', output)

    @integration_test()
    def test_list_offset_long_returns_list_starting_at_param(self):
        output = self.invoke_cli(self.cli_auth_params, ['list', '--offset=2'])
        self.assertIn(f'[\n    "{self.client_params.account}:layer:somelayer",\n'
                      f'    "{self.client_params.account}:policy:root",\n'
                      f'    "{self.client_params.account}:user:someuser",\n'
                      f'    "{self.client_params.account}:variable:one/password",\n'
                      f'    "{self.client_params.account}:webservice:somewebservice"\n]\n', output)

    @integration_test()
    def test_list_offset_returns_list_of_all_resources(self):
        output = self.invoke_cli(self.cli_auth_params, ['list', '-o', '0'])
        self.assertIn(f'[\n    "{self.client_params.account}:group:somegroup",\n'
                      f'    "{self.client_params.account}:host:anotherhost",\n'
                      f'    "{self.client_params.account}:layer:somelayer",\n'
                      f'    "{self.client_params.account}:policy:root",\n'
                      f'    "{self.client_params.account}:user:someuser",\n'
                      f'    "{self.client_params.account}:variable:one/password",\n'
                      f'    "{self.client_params.account}:webservice:somewebservice"\n]\n', output)

    @integration_test(True)
    def test_list_offset_negative_raises_error(self):
        output = self.invoke_cli(self.cli_auth_params, ['list', '-o', '-1'], exit_code=1)
        self.assertIn("500 Server Error", output)

    # This tests is commented out because of a bug in server (https://github.com/cyberark/conjur/issues/1997)
    # where a string is considered valid input for offset. For example, when offset=somestring a list
    # of Conjur resources are returned instead of a 500 internal server error
    # @integration_test(True)
    # def test_list_string_offset_raises_error(self):
    #     output = self.invoke_cli(self.cli_auth_params, ['list', '-o', 'somestring'])
    #     self.assertIn(output,
    #                       f'[\n    "{self.client_params.account}:group:somegroup",\n'
    #                       f'    "{self.client_params.account}:host:anotherhost",\n'
    #                       f'    "{self.client_params.account}:layer:somelayer",\n'
    #                       f'    "{self.client_params.account}:policy:root",\n'
    #                       f'    "{self.client_params.account}:user:someuser",\n'
    #                       f'    "{self.client_params.account}:variable:one/password",\n'
    #                       f'    "{self.client_params.account}:webservice:somewebservice"\n]\n')

    @integration_test(True)
    def test_list_short_search_returns_list_with_param(self):
        output = self.invoke_cli(self.cli_auth_params, ['list', '-s', 'someuser'])
        self.assertIn(f'[\n    "{self.client_params.account}:user:someuser"\n]\n', output)

    @integration_test(True)
    def test_list_long_search_returns_list_with_param(self):
        output = self.invoke_cli(self.cli_auth_params, ['list', '--search=someuser'])
        self.assertIn(f'[\n    "{self.client_params.account}:user:someuser"\n]\n', output)

    @integration_test(True)
    def test_list_search_nonexistent_resource_returns_empty_list(self):
        output = self.invoke_cli(self.cli_auth_params, ['list', '-s', 'some'])
        self.assertIn(f'[]\n', output)

    @integration_test(True)
    def test_list_role_short_user_returns_resources_that_can_be_viewed(self):
        output = self.invoke_cli(self.cli_auth_params, ['list', '-r', f'{self.client_params.account}:user:someuser'])
        self.assertIn(f'[\n    "{self.client_params.account}:variable:one/password"\n]\n', output)

    @integration_test(True)
    def test_list_role_long_user_returns_resources_that_can_be_viewed(self):
        output = self.invoke_cli(self.cli_auth_params, ['list', f'--role={self.client_params.account}:user:someuser'])
        self.assertIn(f'[\n    "{self.client_params.account}:variable:one/password"\n]\n', output)

    @integration_test(True)
    def test_list_role_nonexistent_user_returns_forbidden(self):
        output = self.invoke_cli(self.cli_auth_params, ['list', '-r', f'{self.client_params.account}:user:nonexistinguser'], exit_code=1)
        self.assertRegex(output, '403 Client Error')

    @integration_test(True)
    def test_list_combo_limit_and_kind_returns_specified_kind(self):
        self.invoke_cli(self.cli_auth_params,
               ['policy', 'load', '-b', 'root', '-f', self.environment.path_provider.get_policy_path("conjur")])
        output = self.invoke_cli(self.cli_auth_params, ['list', '-l', '2', '-k', 'host'])
        self.assertIn(f'[\n    "{self.client_params.account}:host:anotherhost",\n'
                      f'    "{self.client_params.account}:host:somehost"\n]\n', output)

    @integration_test()
    def test_list_combo_limit_and_offset_returns_specified_list(self):
        self.invoke_cli(self.cli_auth_params,
               ['policy', 'load', '-b', 'root', '-f', self.environment.path_provider.get_policy_path("conjur")])
        output = self.invoke_cli(self.cli_auth_params, ['list', '-o', '2', '-l', '3'])
        self.assertIn(f'[\n    "{self.client_params.account}:host:somehost",\n'
                      f'    "{self.client_params.account}:layer:somelayer",\n'
                      f'    "{self.client_params.account}:policy:root"\n]\n', output)
