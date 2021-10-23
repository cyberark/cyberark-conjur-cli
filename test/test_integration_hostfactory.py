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

ACCOUNT = 'dev'
HOST_FACTORY_ID = 'hostfactory_policy/some_host_factory'
FULLY_QUALIFIED_HOST_FACTORY_ID = 'dev:host_factory:hostfactory_policy/some_host_factory'
INVALID_DURATION_ERROR_MSG = 'Failed to execute command. Reason: ' \
                             'Either \'duration-days\' / \'duration-hours\' / \'duration-minutes\' ' \
                             'are missing or not in the correct format. Solution: provide one of the required ' \
                             'parameters or make sure they are positive numbers'
BASIC_CREATE_HOST_RESPONSE_REGEX = '{\n    "annotations": \[\],\n    "api_key": ".*",\n    ' \
                                   f'"created_at": ".*",\n    "id": "{ACCOUNT}:host:.*",\n    ' \
                                   f'"owner": "{FULLY_QUALIFIED_HOST_FACTORY_ID}",\n    ' \
                                   '"permissions": \[\],\n    "restricted_to": \[\]\n}\n'
ERROR_PATTERN_422 = "Failed to execute command. Reason: 422 Client Error: Unprocessable Entity for url:.*"
ERROR_PATTERN_404 = 'Failed to execute command. Reason: 404 Client Error: Not Found for url:.*'
ERROR_PATTERN_401 = 'Failed to log in to Conjur. Unable to authenticate with Conjur. ' \
                    'Reason: 401 Client Error: Unauthorized for url:.*'


def one_hour_from_now():
    return time_iso_format_exclude_seconds(timedelta(hours=1))


def time_iso_format_exclude_seconds(duration: timedelta):
    return ''.join((datetime.utcnow().replace(microsecond=0) + duration).isoformat()[:-2])


def token_response_regex(cidr: str):
    return '\[\n    {\n        "cidr": \[\n' \
           f'            "{cidr}"\n' \
           '        \],\n        "expiration": "' \
           f'{one_hour_from_now()}\d\dZ",\n        "token": ".*"\n' \
           '    }\n\]\n'


def token_response_empty_cidr_regex(duration=one_hour_from_now()):
    return '\[\n    {\n        "cidr": \[\],\n' \
           '        "expiration": "' \
           f'{duration}\d\dZ",\n        "token": ".*"\n' \
           '    }\n\]\n'


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
        self.assertRegex(self._create_token(), token_response_empty_cidr_regex())

    @integration_test(True)
    def test_hostfactory_without_id_returns_menu(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token'],
                                 exit_code=1)
        self.assertRegex(output, ".*token - Creates a token for creating hosts with restrictions\n\nUsage:\n.*")

    @integration_test(True)
    def test_hostfactory_with_unknown_hostfactory_id_raises_404_error(self):
        self.assertRegex(self._create_token(host_factory='some-unknown-hostfactory', exit_code=1), ERROR_PATTERN_404)

    @integration_test(True)
    def test_hostfactory_with_no_cidr_returns_empty_cidr_list_in_response(self):
        self.assertRegex(self._create_token(), token_response_empty_cidr_regex())

    @integration_test(True)
    def test_hostfactory_with_single_cidr_returns_cidr_in_response(self):
        self.assertRegex(self.create_one_hour_token(cidr='1.2.3.4'),
                         token_response_regex('1.2.3.4/32'))

    @integration_test(True)
    def test_hostfactory_with_multiple_ciders_returns_cidrs_in_response(self):
        self.assertRegex(self.create_one_hour_token(cidr='1.2.3.4,2.2.2.2'),
                         token_response_regex('1.2.3.4/32",\n            "2.2.2.2/32'))

    @integration_test(True)
    def test_hostfactory_with_low_cidr_range_returns_cidrs_in_response(self):
        self.assertRegex(self.create_one_hour_token(cidr='1.2.0.0/16'), token_response_regex('1.2.0.0/16'))

    @integration_test(True)
    def test_hostfactory_wrong_cidr_format_raises_error(self):
        self.assertRegex(self.create_one_hour_token(cidr='1.2.3', exit_code=1), ERROR_PATTERN_422)

    @integration_test(True)
    def test_hostfactory_wrong_cidr_format_range_raises_error(self):
        self.assertRegex(self.create_one_hour_token(cidr='1.2.3/16', exit_code=1), ERROR_PATTERN_422)

    @integration_test(True)
    def test_hostfactory_with_valid_and_invalid_cidr_raises_error(self):
        self.assertRegex(self.create_one_hour_token(cidr='1.2.3.4,1.2.3', exit_code=1), ERROR_PATTERN_422)

    @integration_test(True)
    def test_hostfactory_with_all_duration_flags_returns_correct_response(self):
        duration = timedelta(days=1, hours=1, minutes=1)
        self.assertRegex(self._create_token(duration=duration),
                         token_response_empty_cidr_regex(duration=time_iso_format_exclude_seconds(duration)))

    @integration_test(True)
    def test_hostfactory_with_zero_value_duration_will_raise_error(self):
        self.assertRegex(self._create_token(duration=timedelta(days=0, hours=0, minutes=0), exit_code=1),
                         INVALID_DURATION_ERROR_MSG)

    @integration_test(True)
    def test_hostfactory_with_only_days_duration_flags_returns_correct_response(self):
        duration = timedelta(days=365, hours=0, minutes=0)
        self.assertRegex(self._create_token(duration=duration),
                         token_response_empty_cidr_regex(duration=time_iso_format_exclude_seconds(duration)))

    @integration_test(True)
    def test_hostfactory_with_only_hours_duration_flags_returns_correct_response(self):
        duration = timedelta(days=0, hours=24, minutes=0)
        self.assertRegex(self._create_token(duration=duration),
                         token_response_empty_cidr_regex(duration=time_iso_format_exclude_seconds(duration)))

    @integration_test(True)
    def test_hostfactory_with_only_minutes_duration_flags_returns_correct_response(self):
        duration = timedelta(days=0, hours=0, minutes=60)
        self.assertRegex(self._create_token(duration=duration),
                         token_response_empty_cidr_regex(duration=time_iso_format_exclude_seconds(duration)))

    @integration_test(True)
    def test_hostfactory_with_negative_duration_days_flags_raises_error(self):
        self.assertRegex(self._create_token(duration=timedelta(days=-1, hours=0, minutes=0), exit_code=1),
                         INVALID_DURATION_ERROR_MSG)

    @integration_test(True)
    def test_hostfactory_without_duration_raises_error(self):
        self.assertRegex(self._create_token(duration=timedelta(), exit_code=1),
                         INVALID_DURATION_ERROR_MSG)

    @integration_test(True)
    def test_hostfactory_create_host_returns_correct_response(self):
        output = self.create_host(self.create_token(), 'some_host' + str(random.randint(0, 1024)))
        self.assertRegex(output, BASIC_CREATE_HOST_RESPONSE_REGEX)

    @integration_test(True)
    def test_hostfactory_create_host_id_accepts_any_char(self):
        output = self.create_host(self.create_token(), 'DifferentTestingChars @#$%^&*()"{}[];\'<>?/.'
                                  + str(random.randint(0, 1024)))
        self.assertRegex(output, BASIC_CREATE_HOST_RESPONSE_REGEX)

    @integration_test(True)
    def test_hostfactory_invalid_token_raise_error(self):
        output = self.create_host('invalid_token', 'some_host', exit_code=1)
        self.assertRegex(output, ERROR_PATTERN_401)

    @integration_test(True)
    def test_hostfactory_empty_host_id_raise_error(self):
        self.assertRegex(self.create_host(self.create_token(), ' ', exit_code=1), ERROR_PATTERN_422)

    @integration_test(True)
    def test_hostfactory_revoke_token_returns_correct_response(self):
        self.assertRegex(self.revoke_token(self.create_token()), 'Token: \'.*\' has been revoked.\\n')

    @integration_test(True)
    def test_hostfactory_revoke_token_invalid_token_raise_404_error(self):
        self.assertRegex(self.revoke_token('non_exist', exit_code=1), ERROR_PATTERN_404)

    @integration_test(True)
    def test_hostfactory_create_host_with_revoked_token_should_raise_401_error(self):
        host_id = f'some_host_{str(random.randint(0, 1024))}'
        token = self.create_token()
        self.create_host(token, host_id)
        self.revoke_token(token)
        self.assertRegex(self.create_host(token, host_id, exit_code=1), ERROR_PATTERN_401)

    def revoke_token(self, token: str, exit_code=0):
        return self.invoke_cli(self.cli_auth_params, ['hostfactory', 'revoke', 'token', '-t', token],
                               exit_code=exit_code)

    def create_host(self, token: str, host: str, exit_code=0):
        return self.invoke_cli(self.cli_auth_params,
                               ['hostfactory', 'create', 'host', '-i', host,
                                '-t', token], exit_code=exit_code)

    def create_token(self):
        """
        Returns the token extracted from the response
        """
        return json.loads(self._create_token())[0]['token']

    @staticmethod
    def token_response_regex(duration: timedelta):
        return '\[\n    {\n        "cidr": \[\],\n' \
               '        "expiration": "' \
               f'{time_iso_format_exclude_seconds(duration=duration)}\d\dZ",\n        "token":.*'

    def _create_token(self, duration=timedelta(hours=1), host_factory=HOST_FACTORY_ID, exit_code=0):
        return self.invoke_cli(self.cli_auth_params,
                               ['hostfactory', 'create', 'token', '-i', host_factory,
                                '--duration-days', str(duration.days),
                                '--duration-hours', str(duration.seconds // 3600),
                                '--duration-minutes', str((duration.seconds // 60) % 60)], exit_code=exit_code)

    def create_one_hour_token(self, cidr: str, exit_code=0):
        return self.invoke_cli(self.cli_auth_params,
                               ['hostfactory', 'create', 'token', '-i', HOST_FACTORY_ID,
                                '--duration-hours', '1', '--cidr', cidr], exit_code=exit_code)


