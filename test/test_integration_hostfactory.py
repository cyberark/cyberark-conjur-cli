# -*- coding: utf-8 -*-

"""
CLI Hostfactory Integration tests

This test file handles the main test flows for the hostfactory command
"""

# Not coverage tested since integration tests doesn't run in
# the same build step
import json
import random
import string
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

    @integration_test(True)
    def test_hostfactory_vanilla_returns_correct_response(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token', '-i', 'hostfactory_policy/some_host_factory',
                                  '--duration-days', '1'])

        self.assertIn('[\n    {\n        "cidr": [],\n'
                      f'        "expiration": "{(datetime.utcnow().replace(microsecond=0) + timedelta(days=1)).isoformat()}Z",\n'
                      '        "token":', output)

    @integration_test(True)
    def test_hostfactory_without_id_returns_menu(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token'],
                                 exit_code=1)
        self.assertIn(" Name:\n  token - Creates a token for creating hosts with restrictions\n\nUsage:\n", output)

    @integration_test(True)
    def test_hostfactory_with_unknown_hostfactory_id_raises_error(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token', '-i', 'some-unknown-hostfactory', '--duration-days',
                                  '1'],
                                 exit_code=1)
        self.assertIn("Failed to execute command. Reason: 404 Client Error", output)

    @integration_test(True)
    def test_hostfactory_with_no_cidr_returns_empty_cidr_list_in_response(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token', '-i', 'hostfactory_policy/some_host_factory',
                                  '--duration-hours', '1'])

        self.assertIn('[\n    {\n        "cidr": [],\n'
                      f'        "expiration": "{(datetime.utcnow().replace(microsecond=0) + timedelta(hours=1)).isoformat()}Z",\n'
                      '        "token":', output)

    @integration_test(True)
    def test_hostfactory_with_single_cidr_returns_cidr_in_response(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token', '-i', 'hostfactory_policy/some_host_factory',
                                  '--duration-hours', '1', '--cidr', '1.2.3.4'])

        self.assertIn('[\n    {\n        "cidr": [\n            "1.2.3.4/32"\n        ],\n'
                      f'        "expiration": "{(datetime.utcnow().replace(microsecond=0) + timedelta(hours=1)).isoformat()}Z",\n'
                      '        "token":', output)

    @integration_test(True)
    def test_hostfactory_with_multiple_ciders_returns_cidrs_in_response(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token', '-i', 'hostfactory_policy/some_host_factory',
                                  '--duration-hours', '1', '--cidr', '1.2.3.4,2.2.2.2'])

        self.assertIn('[\n    {\n        "cidr": [\n            "1.2.3.4/32",\n            "2.2.2.2/32"\n        ],\n'
                      f'        "expiration": "{(datetime.utcnow().replace(microsecond=0) + timedelta(hours=1)).isoformat()}Z",\n'
                      '        "token":', output)

    @integration_test(True)
    def test_hostfactory_with_low_cidr_range_returns_cidrs_in_response(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token', '-i', 'hostfactory_policy/some_host_factory',
                                  '--duration-hours', '1', '--cidr', '1.2.0.0/16'])

        self.assertIn('[\n    {\n        "cidr": [\n            "1.2.0.0/16"\n        ],\n        "expiration": '
                      f'"{(datetime.utcnow().replace(microsecond=0) + timedelta(hours=1)).isoformat()}Z",\n'
                      '        "token":', output)

    @integration_test(True)
    def test_hostfactory_wrong_cidr_format_raises_error(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token', '-i', 'hostfactory_policy/some_host_factory',
                                  '--duration-hours', '1', '--cidr', '1.2.3'], exit_code=1)
        self.assertIn("Reason: 422", output)

    @integration_test(True)
    def test_hostfactory_wrong_cidr_format_range_raises_error(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token', '-i', 'hostfactory_policy/some_host_factory',
                                  '--duration-hours', '1', '--cidr', '1.2.3/16'], exit_code=1)
        self.assertIn("Reason: 422", output)

    @integration_test(True)
    def test_hostfactory_with_valid_and_invalid_cidr_raises_error(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token', '-i', 'hostfactory_policy/some_host_factory',
                                  '--duration-hours', '1', '--cidr', '1.2.3.4,1.2.3'], exit_code=1)
        self.assertIn("Reason: 422", output)

    @integration_test(True)
    def test_hostfactory_with_all_duration_flags_returns_correct_response(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token', '-i', 'hostfactory_policy/some_host_factory',
                                  '--duration-days', '1', '--duration-hours', '1', '--duration-minutes', '1'])

        self.assertIn('[\n    {\n        "cidr": [],\n'
                      f'        "expiration": "{(datetime.utcnow().replace(microsecond=0) + timedelta(days=1, hours=1, minutes=1)).isoformat()}Z",\n'
                      '        "token":', output)

    @integration_test(True)
    def test_hostfactory_with_zero_value_duration_will_raise_error(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token', '-i', 'hostfactory_policy/some_host_factory',
                                  '--duration-days', '0', '--duration-hours', '0', '--duration-minutes', '0'],
                                 exit_code=1)

        self.assertIn("Failed to execute command.", output)

    @integration_test(True)
    def test_hostfactory_with_only_days_duration_flags_returns_correct_response(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token', '-i', 'hostfactory_policy/some_host_factory',
                                  '--duration-days', '365'])

        self.assertIn('[\n    {\n        "cidr": [],\n'
                      f'        "expiration": "{(datetime.utcnow().replace(microsecond=0) + timedelta(days=365)).isoformat()}Z",\n'
                      '        "token":', output)

    @integration_test(True)
    def test_hostfactory_with_only_hours_duration_flags_returns_correct_response(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token', '-i', 'hostfactory_policy/some_host_factory',
                                  '--duration-hours', '24'])

        self.assertIn('[\n    {\n        "cidr": [],\n'
                      f'        "expiration": "{(datetime.utcnow().replace(microsecond=0) + timedelta(hours=24)).isoformat()}Z",\n'
                      '        "token":', output)

    @integration_test(True)
    def test_hostfactory_with_only_minutes_duration_flags_returns_correct_response(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token', '-i', 'hostfactory_policy/some_host_factory',
                                  '--duration-minutes', '60'])

        self.assertIn('[\n    {\n        "cidr": [],\n        "expiration": '
                      f'"{(datetime.utcnow().replace(microsecond=0) + timedelta(minutes=60)).isoformat()}Z",\n'
                      '        "token": ', output)

    @integration_test(True)
    def test_hostfactory_with_negative_duration_days_flags_raises_error(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token', '-i', 'hostfactory_policy/some_host_factory',
                                  '--duration-days', '-1'], exit_code=1)

        self.assertIn("Failed to execute command.", output)

    @integration_test(True)
    def test_hostfactory_without_duration_raises_error(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token', '-i', 'hostfactory_policy/some_host_factory'],
                                 exit_code=1)
        self.assertIn("Failed to execute command. Reason: Either", output)

    @integration_test(True)
    def test_hostfactory_create_host_returns_correct_response(self):
        random_host_id = ''.join(random.choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k=12))
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'host', '-i', random_host_id,
                                  '-t', f"{self.create_token()}"])
        json_output = json.loads(output)
        api_key = json_output['api_key']
        created_at = json_output['created_at']

        self.assertIn(output,
                      '{\n    "annotations": [],\n    '
                      f'"api_key": "{api_key}",\n    "created_at": "{created_at}",\n    '
                      f'"id": "dev:host:{random_host_id}",\n    '
                      '"owner": "dev:host_factory:hostfactory_policy/some_host_factory",\n    '
                      '"permissions": [],\n    "restricted_to": []\n}\n')

    @integration_test(True)
    def test_hostfactory_create_host_id_accepts_any_char(self):
        random_host_id = ''.join(random.choices(string.ascii_uppercase + string.digits + string.ascii_lowercase, k=12))
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'host', '-i',
                                  'DifferentTestingChars @#$%^&*()"{}[];\'<>?/.' + random_host_id,
                                  '-t', f"{self.create_token()}"])
        self.assertEqual(json.loads(output)['id'],
                         'dev:host:DifferentTestingChars @#$%^&*()"{}[];\'<>?/.' + random_host_id)

    @integration_test(True)
    def test_hostfactory_invalid_token_raise_error(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'host', '-i', 'some_host',
                                  '-t', 'invalid_token'], exit_code=1)

        self.assertIn("Failed to log in to Conjur. Unable to authenticate with Conjur. Reason: 401 Client Error: "
                      "Unauthorized for url:", output)

    @integration_test(True)
    def test_hostfactory_empty_host_id_raise_error(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'host', '-i', ' ',
                                  '-t', f"{self.create_token()}"], exit_code=1)

        self.assertIn("Failed to execute command. Reason: 422 Client Error: Unprocessable Entity for url: ", output)

    @integration_test(True)
    def test_hostfactory_revoke_token_returns_correct_response(self):
        token = self.create_token()
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'revoke', 'token', '-t', token])

        self.assertIn(f'Token: \'{token}\' has been revoked.\n', output)

    @integration_test(True)
    def test_hostfactory_revoke_token_invalid_token_raise_404_error(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'revoke', 'token', '-t', 'non_exist'], exit_code=1)

        self.assertIn("Failed to execute command. Reason: 404 Client Error: Not Found for url: ", output)

    def create_token(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token', '-i', 'hostfactory_policy/some_host_factory',
                                  '--duration-days', '1'])
        response = json.loads(output)
        return response[0]['token']

    @integration_test(True)
    def test_hostfactory_create_host_with_revoked_token_should_raise_401_error(self):
        token = self.create_token()
        self.invoke_cli(self.cli_auth_params,
                        ['hostfactory', 'create', 'host', '-i', 'some_host',
                         '-t', token])
        self.invoke_cli(self.cli_auth_params, ['hostfactory', 'revoke', 'token', '-t', token])
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'host', '-i', 'some_host',
                                  '-t', token], exit_code=1)
        self.assertIn('Failed to log in to Conjur. Unable to authenticate with Conjur. Reason: '
                      '401 Client Error: Unauthorized for url: ', output)
