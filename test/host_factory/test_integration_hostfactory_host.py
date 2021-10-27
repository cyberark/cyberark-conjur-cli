# -*- coding: utf-8 -*-

"""
CLI Hostfactory Integration tests

This test file handles the main test flows for the hostfactory command
"""

# Not coverage tested since integration tests doesn't run in
# the same build step
import json
import random
from datetime import timedelta

from test.host_factory.test_integration_hostfactory import CliIntegrationTestHostFactory, \
    HOST_FACTORY_ID, FULLY_QUALIFIED_HOST_FACTORY_ID, ERROR_PATTERN_401, ERROR_PATTERN_422
from test.util.test_infrastructure import integration_test


class CliIntegrationTestHostFactoryHost(CliIntegrationTestHostFactory):  # pragma: no cover

    def __init__(self, test_name, client_params=None, environment_params=None):
        super(CliIntegrationTestHostFactory, self).__init__(test_name, client_params, environment_params)

    # *************** TESTS ***************

    @integration_test(True)
    def test_hostfactory_create_host_returns_correct_response(self):
        host_id = 'some_host' + str(random.randint(0, 1024))
        output = self.create_host(self.create_token(), host_id)
        self.assertRegex(output, self.get_basic_create_host_response_regex(host_id))

    @integration_test(True)
    def test_hostfactory_create_host_id_accepts_any_char(self):
        host_id = 'DifferentTestingChars @#$%^&*()"{}[];\'<>?/.' \
                  + str(random.randint(0, 1024))
        output = self.create_host(self.create_token(), host_id)
        self.assertRegex(output, self.get_basic_create_host_response_regex('.*'))

    @integration_test(True)
    def test_hostfactory_invalid_token_raise_error(self):
        output = self.create_host('invalid_token', 'some_host', exit_code=1)
        self.assertRegex(output, ERROR_PATTERN_401)

    @integration_test(True)
    def test_hostfactory_empty_host_id_raise_error(self):
        self.assertRegex(self.create_host(self.create_token(), ' ', exit_code=1), ERROR_PATTERN_422)

    @integration_test(True)
    def test_hostfactory_create_host_with_revoked_token_should_raise_401_error(self):
        host_id = f'some_host_{str(random.randint(0, 1024))}'
        token = self.create_token()
        self.create_host(token, host_id)
        self.revoke_token(token)
        self.assertRegex(self.create_host(token, host_id, exit_code=1), ERROR_PATTERN_401)

    def create_host(self, token: str, host: str, exit_code=0):
        return self.invoke_cli(self.cli_auth_params,
                               ['hostfactory', 'create', 'host', '-i', host,
                                '-t', token], exit_code=exit_code)

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

    def create_one_hour_token(self, cidr: str, exit_code=0):
        return self.cli_create_token('--duration-hours', '1', '--cidr', cidr, exit_code=exit_code)

    def create_token_with_args(self, *args, host_factory=HOST_FACTORY_ID, exit_code=0):
        return self.invoke_cli(self.cli_auth_params, ['hostfactory', 'create', 'token', '-i', host_factory, *args],
                               exit_code=exit_code)

    def get_basic_create_host_response_regex(self, host: str):
        return '{\n    "annotations": \[\],\n    "api_key": ".*",\n    ' \
               f'"created_at": ".*",\n    ' \
               f'"id": "{self.client_params.account}:host:{host}",\n    ' \
               f'"owner": "{FULLY_QUALIFIED_HOST_FACTORY_ID.format(self.client_params.account)}",\n    ' \
               '"permissions": \[\],\n    "restricted_to": \[\]\n}\n'
