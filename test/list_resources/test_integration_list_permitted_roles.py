# -*- coding: utf-8 -*-

"""
CLI List Integration tests

This test file handles the main test flows for the list command
"""
import json

from test.util import test_helpers as utils
from test.util.test_infrastructure import integration_test
from test.util.test_runners.integration_test_case import IntegrationTestCaseBase


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
                       ['policy', 'replace', '-b', 'root', '-f', self.environment.path_provider.get_policy_path("list_permitted_roles")])

    # *************** TESTS ***************

    @integration_test()
    def test_list_permitted_roles_without_identifier_return_error(self):
        with self.assertRaises(AssertionError):
            self.invoke_cli(self.cli_auth_params, ['list', '--permitted-roles'])

    @integration_test()
    def test_list_permitted_roles_without_privilege_flag_return_error(self):
        with self.assertRaises(AssertionError):
            self.invoke_cli(self.cli_auth_params, ['list', '--permitted-roles', 'one/password'])

    @integration_test()
    def test_list_permitted_roles_without_privilege_value_return_error(self):
        with self.assertRaises(AssertionError):
            self.invoke_cli(self.cli_auth_params, ['list', '--permitted-roles', 'one/password', '--privilege'])

    @integration_test()
    def test_list_permitted_roles_without_kind_value_return_error(self):
        with self.assertRaises(AssertionError):
            self.invoke_cli(self.cli_auth_params,
                            ['list', '--permitted-roles', 'one/password', '--privilege', 'read', '--kind'])

    @integration_test()
    def test_list_permitted_roles_for_unknown_resource_without_kind_return_error(self):
        with self.assertRaises(AssertionError):
            self.invoke_cli(self.cli_auth_params,
                            ['list', '--permitted-roles', 'unknown_resource', '--privilege', 'read'])

    @integration_test()
    def test_list_permitted_roles_for_distinct_resource_without_kind_return_success(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['list', '--permitted-roles', 'one/password', '--privilege', 'read'])
        json_result = json.loads(output)
        expected_result = [f"{self.client_params.account}:user:someuser", f"{self.client_params.account}:user:admin"]
        self.assertCountEqual(expected_result, json_result)

    @integration_test()
    def test_list_permitted_roles_for_ambiguous_resource_without_kind_return_error(self):
        with self.assertRaises(AssertionError):
            self.invoke_cli(self.cli_auth_params, ['list', '--permitted-roles', 'service', '--privilege', 'read'])

    @integration_test()
    def test_list_permitted_roles_with_kind_in_identifier_return_success(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['list', '--permitted-roles', 'variable:one/password', '--privilege', 'read'])
        json_result = json.loads(output)
        expected_result = [f"{self.client_params.account}:user:someuser", f"{self.client_params.account}:user:admin"]
        self.assertCountEqual(expected_result, json_result)

    @integration_test()
    def test_list_permitted_roles_for_ambiguous_resource_with_kind_param_return_error(self):
        with self.assertRaises(AssertionError):
            self.invoke_cli(self.cli_auth_params,
                            ['list', '--permitted-roles', 'service', '--privilege', 'read', '--kind', 'webservice'])

    @integration_test()
    def test_list_permitted_roles_with_all_flags_in_short_version_return_success(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['list', '-pr', 'variable:one/password', '-p', 'read'])
        json_result = json.loads(output)
        expected_result = [f"{self.client_params.account}:user:someuser", f"{self.client_params.account}:user:admin"]
        self.assertCountEqual(expected_result, json_result)
