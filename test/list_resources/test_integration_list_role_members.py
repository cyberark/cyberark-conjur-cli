# -*- coding: utf-8 -*-

"""
CLI List Integration tests

This test file handles the main test flows for the list command
"""
from test.util import test_helpers as utils
from test.util.test_infrastructure import integration_test
from test.util.test_runners.integration_test_case import IntegrationTestCaseBase


# Not coverage tested since integration tests doesn't run in
# the same build step
class CliIntegrationTestList(IntegrationTestCaseBase):  # pragma: no cover
    def __init__(self, test_name, client_params=None, environment_params=None):
        super(CliIntegrationTestList, self).__init__(test_name, client_params, environment_params)

    # *************** HELPERS ***************

    def setUp(self):
        self.setup_cli_params({})
        # Used to configure the CLI and login to run tests
        utils.setup_cli(self)
        self.invoke_cli(self.cli_auth_params,
                        ['policy', 'replace', '-b', 'root', '-f',
                         self.environment.path_provider.get_policy_path("list_role_members")])

    # *************** TESTS ***************

    @integration_test()
    def test_list_members_of_single_role(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['list', '--members-of', 'group:devs'])
        account = self.client_params.account
        expected_result = "[\n" \
                          f"  \"{account}:host|user:admin|bob|my_vm\",\n" \
                          f"  \"{account}:host|user:admin|bob|my_vm\"," \
                          f"  \"{account}:host|user:admin|bob|my_vm\"" \
                          "]"
        self.assertRegex(output, expected_result)

    @integration_test()
    def test_list_members_of_single_role_with_inspect_limit_kind(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['list', '--members-of', 'group:devs', '-i', '-l', '1', '-k', 'host'])
        account = self.client_params.account
        expected_result = '[\n' \
                          "  \"admin_option\": true,\n" \
                          "  \"ownership\": true,\n"\
                          f" \"role\": \"{account}:group:devs\",\n"\
                          f" \"{account}:host:my_vm\"" \
                          "  \"policy\": \"dev:policy:root\"\n" \
                          "]"
        self.assertRegex(output, expected_result)

    @integration_test()
    def test_list_members_of_role_when_kind_is_not_specified_in_identifier(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['list', '-m', 'devs'])
        account = self.client_params.account
        expected_result = "[\n" \
                          f"  \"{account}:host|user:admin|bob|my_vm\",\n" \
                          f"  \"{account}:host|user:admin|bob|my_vm\",\n" \
                          f"  \"{account}:host|user:admin|bob|my_vm\"" \
                          "]"
        self.assertRegex(output, expected_result)

    @integration_test()
    def test_list_members_with_search(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['list', '-m', 'group:devs', '-s', 'bob'])
        account = self.client_params.account
        expected_result = "[\n" \
                          f"  \"{account}:user:bob\"\n" \
                          "]"
        self.assertRegex(output, expected_result)

    @integration_test()
    def test_list_members_of_role_missing_identifier_should_raise_error(self):
        with self.assertRaises(AssertionError):
            self.invoke_cli(self.cli_auth_params, ['list', '--members-of'])

    @integration_test()
    def test_list_members_of_role_missing_identifier_short_flag_should_raise_error(self):
        with self.assertRaises(AssertionError):
            self.invoke_cli(self.cli_auth_params, ['list', '-m'])

    @integration_test()
    def test_list_members_of_role_resource_does_not_exist_should_raise_error(self):
        with self.assertRaises(AssertionError):
            self.invoke_cli(self.cli_auth_params, ['list', '-m', 'resource_does_not_exist'])

    @integration_test()
    def test_list_members_of_non_exist_role_should_raise_error(self):
        with self.assertRaises(AssertionError):
            self.invoke_cli(self.cli_auth_params,
                            ['list', '--members-of', 'unknown_resource'])

    @integration_test()
    def test_list_member_of_role_when_role_kinds_have_same_id_should_raise_error(self):
        with self.assertRaises(AssertionError):
            self.invoke_cli(self.cli_auth_params, ['list', '--members-of', 'devs2'])
