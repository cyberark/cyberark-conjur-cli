# -*- coding: utf-8 -*-

"""
CLI Hostfactory Integration tests

This test file handles the main test flows for the hostfactory command
"""

# Not coverage tested since integration tests doesn't run in
# the same build step
from datetime import datetime, timedelta

from test.util.test_infrastructure import integration_test
from test.util.test_runners.integration_test_case import IntegrationTestCaseBase
from test.util import test_helpers as utils


class CliIntegrationTestList(IntegrationTestCaseBase):  # pragma: no cover
    def __init__(self, testname, client_params=None, environment_params=None):
        super(CliIntegrationTestList, self).__init__(testname, client_params, environment_params)

    # *************** HELPERS ***************

    def setUp(self):
        self.setup_cli_params({})
        # Used to configure the CLI and login to run tests
        utils.setup_cli(self)
        self.invoke_cli(self.cli_auth_params,
                        ['policy', 'replace', '-b', 'root', '-f',
                         self.environment.path_provider.get_policy_path("hostfactory")])

    # *************** TESTS ***************

    @integration_test()
    def test_hostfactory_vanilla_returns_correct_response(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token', '-i', 'hostfactory_policy/some_host_factory'])

        self.assertIn('[\n    {\n        "cidr": [],\n'
                      f'        "expiration": "{(datetime.utcnow().replace(microsecond=0) + timedelta(hours=1)).isoformat()}Z",\n'
                      '        "token":', output)

    def test_hostfactory_without_id_returns_menu(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token'],
                                 exit_code=1)
        self.assertIn("Failed to execute command", output)

    def test_hostfactory_with_unknown_hostfactory_id_returns_error(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token', '-i', 'some-unknown-hostfactory'],
                                 exit_code=1)
        self.assertIn("Failed to execute command. Reason: 404 Client Error", output)

    def test_hostfactory_with_no_cidr_returns_empty_cidr_list_in_response(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token', '-i', 'hostfactory_policy/some_host_factory'])

        self.assertIn('[\n    {\n        "cidr": [],\n'
                      f'        "expiration": "{(datetime.utcnow().replace(microsecond=0) + timedelta(hours=1)).isoformat()}Z",\n'
                      '        "token":', output)

    def test_hostfactory_with_single_cidr_returns_cidr_in_response(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token', '-i', 'hostfactory_policy/some_host_factory',
                                  '--cidr', '1.2.3.4'])

        self.assertIn('[\n    {\n        "cidr": [\n            "1.2.3.4/32"\n        ],\n'
                      f'        "expiration": "{(datetime.utcnow().replace(microsecond=0) + timedelta(hours=1)).isoformat()}Z",\n'
                      '        "token":', output)

    def test_hostfactory_with_multiple_ciders_returns_cidrs_in_response(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token', '-i', 'hostfactory_policy/some_host_factory',
                                  '--cidr', '1.2.3.4,2.2.2.2'])

        self.assertIn('[\n    {\n        "cidr": [\n            "1.2.3.4/32",\n'
                      '            "2.2.2.2/32"\n        ],\n'
                      f'        "expiration": "{(datetime.utcnow().replace(microsecond=0) + timedelta(hours=1)).isoformat()}Z",\n'
                      '        "token":', output)

    def test_hostfactory_with_low_cidr_range_returns_cidrs_in_response(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token', '-i', 'hostfactory_policy/some_host_factory',
                                  '--cidr', '1.2.0.0/16'])

        self.assertIn('[\n    {\n        "cidr": [\n            "1.2.0.0/16"\n        ],\n'
                      f'        "expiration": "{(datetime.utcnow().replace(microsecond=0) + timedelta(hours=1)).isoformat()}Z",\n'
                      '        "token":', output)

    def test_hostfactory_wrong_cidr_format_raises_error(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token', '-i', 'hostfactory_policy/some_host_factory',
                                  '--cidr', '1.2.3'], exit_code=1)
        self.assertIn("Reason: 422", output)

    def test_hostfactory_wrong_cidr_format_range_raises_error(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token', '-i', 'hostfactory_policy/some_host_factory',
                                  '--cidr', '1.2.3/16'], exit_code=1)
        self.assertIn("Reason: 422", output)

    def test_hostfactory_with_valid_and_invalid_cidr_raises_error(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token', '-i', 'hostfactory_policy/some_host_factory',
                                  '--cidr', '1.2.3.4,1.2.3'], exit_code=1)
        self.assertIn("Reason: 422", output)
