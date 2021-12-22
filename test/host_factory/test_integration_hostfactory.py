# -*- coding: utf-8 -*-

"""
CLI Hostfactory Integration tests base class

This test file handles the main test flows for the hostfactory command
"""

# Not coverage tested since integration tests doesn't run in
# the same build step
import json
from datetime import datetime, timedelta

from test.util.test_runners.integration_test_case import IntegrationTestCaseBase
from test.util import test_helpers as utils

HOST_FACTORY_ID = 'hostfactory_policy/some_host_factory'
FULLY_QUALIFIED_HOST_FACTORY_ID = '{}:host_factory:hostfactory_policy/some_host_factory'
INVALID_DURATION_ERROR_MSG = 'Failed to execute command. Reason: ' \
                             'Either \'duration-days\' / \'duration-hours\' / \'duration-minutes\' ' \
                             'are missing or not in the correct format. Solution: provide one of the required ' \
                             'parameters or make sure they are positive numbers'
ERROR_PATTERN_422 = r"Failed to execute command. Reason: 422 \(Unprocessable Entity\) for url:.*"
ERROR_PATTERN_404 = r'Failed to execute command. Reason: 404 \(Not Found\) for url:.*'
ERROR_PATTERN_401 = 'Failed to log in to Conjur. Unable to authenticate with Conjur. ' \
                    r'Reason: 401 \(Unauthorized\) for url:.*'


class CliIntegrationTestHostFactory(IntegrationTestCaseBase):  # pragma: no cover

    def __init__(self, test_name, client_params=None, environment_params=None):
        super(CliIntegrationTestHostFactory, self).__init__(test_name, client_params, environment_params)

    def setUp(self):
        self.setup_cli_params({})
        # Used to configure the CLI and login to run tests
        utils.setup_cli(self)
        self.invoke_cli(self.cli_auth_params,
                        ['policy', 'replace', '-b', 'root', '-f',
                         self.environment.path_provider.get_policy_path("hostfactory")])

    def revoke_token(self, token: str, exit_code=0):
        return self.invoke_cli(self.cli_auth_params, ['hostfactory', 'revoke', 'token', '-t', token],
                               exit_code=exit_code)

    def create_host(self, token: str, host: str, exit_code=0):
        return self.cli_create_host('-i', host, '-t', token, exit_code=exit_code)

    def _create_token(self, duration=timedelta(hours=1), host_factory=HOST_FACTORY_ID, exit_code=0):
        return self.cli_create_token(
            '--duration-days', str(duration.days),
            '--duration-hours', str(duration.seconds // 3600),
            '--duration-minutes', str((duration.seconds // 60) % 60),
            host_factory=host_factory,
            exit_code=exit_code)

    def create_token(self):
        """
        Returns the token extracted from the response
        """
        return json.loads(self.cli_create_token('--duration-hours', '1'))[0]['token']

    def create_one_hour_token(self, cidr=None, exit_code=0):
        return self.cli_create_token('--duration-hours', '1', '--cidr', cidr,
                                     exit_code=exit_code)

    def cli_create_token(self, *args, host_factory=HOST_FACTORY_ID, exit_code=0):
        return self.cli_create('token', '-i', host_factory, *args, exit_code=exit_code)

    def cli_create_host(self, *args, exit_code=0):
        return self.cli_create('host', *args, exit_code=exit_code)

    def cli_create(self, *args, exit_code=0):
        return self._invoke_cli('create', *args, exit_code=exit_code)

    def _invoke_cli(self, *args, exit_code=0):
        return self.invoke_cli(self.cli_auth_params, ['hostfactory', *args],
                               exit_code=exit_code)

    def get_basic_create_host_response_regex(self, host: str):
        return '{\n    "annotations": \[\],\n    "api_key": ".*",\n    ' \
               f'"created_at": ".*",\n    ' \
               f'"id": "{self.client_params.account}:host:{host}",\n    ' \
               f'"owner": "{FULLY_QUALIFIED_HOST_FACTORY_ID.format(self.client_params.account)}",\n    ' \
               '"permissions": \[\],\n    "restricted_to": \[\]\n}\n'
