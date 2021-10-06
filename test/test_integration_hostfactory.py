# -*- coding: utf-8 -*-

"""
CLI Hostfactory Integration tests

This test file handles the main test flows for the hostfactory command
"""

# Not coverage tested since integration tests doesn't run in
# the same build step
import json
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

    def extract_from_json(self, output, property):
        values = []
        output_to_dict = json.loads(output)
        for entry in output_to_dict:
            values.append(entry[property])
        return values

    # *************** TESTS ***************

    @integration_test()
    def test_hostfactory_vanilla_returns_correct_response(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token', '-i', 'hostfactory_policy/some_host_factory', '--duration-days', '1'])

        self.assertIn('[\n    {\n        "cidr": [],\n'
                      f'        "expiration": "{(datetime.utcnow().replace(microsecond=0) + timedelta(days=1)).isoformat()}Z",\n'
                      '        "token":', output)

    def test_hostfactory_without_id_returns_menu(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token'],
                                 exit_code=1)
        self.assertIn("Failed to execute command", output)

    def test_hostfactory_with_unknown_hostfactory_id_raises_error(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token', '-i', 'some-unknown-hostfactory', '--duration-days', '1'],
                                 exit_code=1)
        self.assertIn("Failed to execute command. Reason: 404 Client Error", output)

    def test_hostfactory_with_no_cidr_returns_empty_cidr_list_in_response(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token', '-i', 'hostfactory_policy/some_host_factory', '--duration-hours', '1'])

        self.assertIn('[\n    {\n        "cidr": [],\n'
                      f'        "expiration": "{(datetime.utcnow().replace(microsecond=0) + timedelta(hours=1)).isoformat()}Z",\n'
                      '        "token":', output)

    def test_hostfactory_with_single_cidr_returns_cidr_in_response(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token', '-i', 'hostfactory_policy/some_host_factory', '--duration-hours', '1',
                                  '--cidr', '1.2.3.4'])

        self.assertIn('[\n    {\n        "cidr": [\n            "1.2.3.4/32"\n        ],\n'
                      f'        "expiration": "{(datetime.utcnow().replace(microsecond=0) + timedelta(hours=1)).isoformat()}Z",\n'
                      '        "token":', output)

    def test_hostfactory_with_multiple_ciders_returns_cidrs_in_response(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token', '-i', 'hostfactory_policy/some_host_factory', '--duration-hours', '1'
                                  '--cidr', '1.2.3.4,2.2.2.2'])

        self.assertIn('[\n    {\n        "cidr": [\n            "1.2.3.4/32",\n'
                      '            "2.2.2.2/32"\n        ],\n'
                      f'        "expiration": "{(datetime.utcnow().replace(microsecond=0) + timedelta(hours=1)).isoformat()}Z",\n'
                      '        "token":', output)

    def test_hostfactory_with_low_cidr_range_returns_cidrs_in_response(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token', '-i', 'hostfactory_policy/some_host_factory', '--duration-hours', '1'
                                  '--cidr', '1.2.0.0/16'])

        self.assertIn('[\n    {\n        "cidr": [\n            "1.2.0.0/16"\n        ],\n'
                      f'        "expiration": "{(datetime.utcnow().replace(microsecond=0) + timedelta(hours=1)).isoformat()}Z",\n'
                      '        "token":', output)

    def test_hostfactory_wrong_cidr_format_raises_error(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token', '-i', 'hostfactory_policy/some_host_factory', '--duration-hours', '1'
                                  '--cidr', '1.2.3'], exit_code=1)
        self.assertIn("Reason: 422", output)

    def test_hostfactory_wrong_cidr_format_range_raises_error(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token', '-i', 'hostfactory_policy/some_host_factory', '--duration-hours', '1'
                                  '--cidr', '1.2.3/16'], exit_code=1)
        self.assertIn("Reason: 422", output)

    def test_hostfactory_with_valid_and_invalid_cidr_raises_error(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token', '-i', 'hostfactory_policy/some_host_factory', '--duration-hours', '1'
                                  '--cidr', '1.2.3.4,1.2.3'], exit_code=1)
        self.assertIn("Reason: 422", output)

    def test_hostfactory_with_all_duration_flags_returns_correct_response(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token', '-i', 'hostfactory_policy/some_host_factory',
                                  '--duration-days', '1', '--duration-hours', '1', '--duration-minutes', '1'])

        self.assertIn('[\n    {\n        "cidr": [],\n'
                      f'        "expiration": "{(datetime.utcnow().replace(microsecond=0) + timedelta(days=1, hours=1, minutes=1)).isoformat()}Z",\n'
                      '        "token":', output)

    def test_hostfactory_with_zero_value_duration_will_raise_error(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token', '-i', 'hostfactory_policy/some_host_factory',
                                  '--duration-days', '0', '--duration-hours', '0', '--duration-minutes', '0'])

        self.assertIn("Failed to execute command. Reason: Parameter", output)

    def test_hostfactory_with_only_days_duration_flags_returns_correct_response(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token', '-i', 'hostfactory_policy/some_host_factory',
                                  '--duration-days', '365'])

        self.assertIn('[\n    {\n        "cidr": [],\n'
                      f'        "expiration": "{(datetime.utcnow().replace(microsecond=0) + timedelta(days=365)).isoformat()}Z",\n'
                      '        "token":', output)

    def test_hostfactory_with_only_hours_duration_flags_returns_correct_response(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token', '-i', 'hostfactory_policy/some_host_factory',
                                  '--duration-hours', '24'])

        self.assertIn('[\n    {\n        "cidr": [],\n'
                      f'        "expiration": "{(datetime.utcnow().replace(microsecond=0) + timedelta(hours=24)).isoformat()}Z",\n'
                      '        "token":', output)

    def test_hostfactory_with_only_minutes_duration_flags_returns_correct_response(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token', '-i', 'hostfactory_policy/some_host_factory',
                                  '--duration-minutes', '60'])

        self.assertIn('[\n    {\n        "cidr": [],\n'
                      f'        "expiration": "{(datetime.utcnow().replace(microsecond=0) + timedelta(minutes=60)).isoformat()}Z",\n'
                      '        "token":', output)

    def test_hostfactory_with_negative_duration_days_flags_raises_error(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token', '-i', 'hostfactory_policy/some_host_factory',
                                  '--duration-days', '-1'], exit_code=1)

        self.assertIn("Failed to execute command. Reason: Parameter", output)

    def test_hostfactory_without_duration_raises_error(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token', '-i', 'hostfactory_policy/some_host_factory',
                                  '--duration-minutes', '1'], exit_code=1)
        self.assertIn("Failed to execute command. Reason: Parameter", output)


    def test_hostfactory_with_count_returns_correct_response(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token', '-i', 'hostfactory_policy/some_host_factory', '--duration-minutes', '1',
                                  '--count', '3'])
        token_values = self.extract_from_json(output, "token")

        self.assertIn('[\n    {\n        "cidr": [],\n'
                      f'        "expiration": "{(datetime.utcnow().replace(microsecond=0) + timedelta(hours=1)).isoformat()}Z",\n'
                      f'        "token": "{token_values[0]}"\n    }},'
                      '\n    {\n        "cidr": [],\n'
                      f'        "expiration": "{(datetime.utcnow().replace(microsecond=0) + timedelta(hours=1)).isoformat()}Z",\n'
                      f'        "token": "{token_values[1]}"\n    }},'
                      '\n    {\n        "cidr": [],\n'
                      f'        "expiration": "{(datetime.utcnow().replace(microsecond=0) + timedelta(hours=1)).isoformat()}Z",\n'
                      f'        "token": "{token_values[2]}"\n    }}\n]\n'
                      , output)

    def test_hostfactory_with_negative_count_raises_error(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token', '-i', 'hostfactory_policy/some_host_factory', '--duration-minutes', '1'
                                  '--count', '-1'], exit_code=1)
        self.assertIn("Failed to execute command. Reason: Missing required", output)

    def test_hostfactory_with_zero_count_raises_error(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token', '-i', 'hostfactory_policy/some_host_factory', '--duration-minutes', '1'
                                  '--count', '0'], exit_code=1)
        self.assertIn("Failed to execute command. Reason: Missing required", output)