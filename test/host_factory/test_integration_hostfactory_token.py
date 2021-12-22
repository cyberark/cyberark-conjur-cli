# -*- coding: utf-8 -*-

"""
CLI Hostfactory Integration tests

This test file handles the main test flows for the hostfactory command
"""

# Not coverage tested since integration tests doesn't run in
# the same build step
import json
from datetime import timedelta, datetime
from test.util.test_infrastructure import integration_test
from test.host_factory.test_integration_hostfactory import CliIntegrationTestHostFactory, ERROR_PATTERN_404, \
    ERROR_PATTERN_422, INVALID_DURATION_ERROR_MSG


class CliIntegrationTestHostFactoryToken(CliIntegrationTestHostFactory):  # pragma: no cover

    def __init__(self, test_name, client_params=None, environment_params=None):
        super(CliIntegrationTestHostFactoryToken, self).__init__(test_name, client_params, environment_params)

    def assert_create_token_response(self,
                                     create_token_response: str,
                                     expected_cidrs: list = [],
                                     expected_expiration_duration: timedelta = timedelta(hours=1)):
        create_token_response_json = json.loads(create_token_response)
        self.assertEquals(1, len(create_token_response_json))
        response_token = create_token_response_json[0]

        self.assertEquals(expected_cidrs, response_token['cidr'])

        self.assertIsNotNone(response_token['expiration'])
        expiration_time = datetime.fromisoformat(response_token['expiration'].rstrip('Z'))
        expiration_duration = expiration_time - datetime.utcnow()
        self.assertAlmostEquals(expected_expiration_duration.total_seconds(),
                                expiration_duration.total_seconds(),
                                delta=10)  # delta=10 means that the time diff can't be more than 10 seconds.

        self.assertIsNotNone(response_token['token'])

    # *************** TESTS ***************

    @integration_test(True)
    def test_hostfactory_create_token_without_id_returns_menu(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token'],
                                 exit_code=1)
        self.assertRegex(output, ".*token - Generate a Host Factory token for " \
                                    "creating hosts with restrictions\n\nUsage:\n.*")

    @integration_test(True)
    def test_hostfactory_create_token_with_unknown_hostfactory_id_raises_404_error(self):
        self.assertRegex(self._create_token(host_factory='some-unknown-hostfactory', exit_code=1), ERROR_PATTERN_404)

    @integration_test(True)
    def test_hostfactory_create_token_with_no_cidr_returns_empty_cidr_list_in_response(self):
        response = self._create_token()
        self.assert_create_token_response(response)

    @integration_test(True)
    def test_hostfactory_create_token_with_single_cidr_returns_cidr_in_response(self):
        response = self.create_one_hour_token(cidr='1.2.3.4')
        self.assert_create_token_response(response, expected_cidrs=['1.2.3.4/32'])

    @integration_test(True)
    def test_hostfactory_create_token_with_multiple_ciders_returns_cidrs_in_response(self):
        response = self.create_one_hour_token(cidr='1.2.3.4,2.2.2.2')
        self.assert_create_token_response(response, expected_cidrs=['1.2.3.4/32', '2.2.2.2/32'])

    @integration_test(True)
    def test_hostfactory_create_token_with_low_cidr_range_returns_cidrs_in_response(self):
        response = self.create_one_hour_token(cidr='1.2.0.0/16')
        self.assert_create_token_response(response, expected_cidrs=['1.2.0.0/16'])

    @integration_test(True)
    def test_hostfactory_create_token_wrong_cidr_format_raises_error(self):
        self.assertRegex(self.create_one_hour_token(cidr='1.2.3', exit_code=1), ERROR_PATTERN_422)

    @integration_test(True)
    def test_hostfactory_create_token_wrong_cidr_format_range_raises_error(self):
        self.assertRegex(self.create_one_hour_token(cidr='1.2.3/16', exit_code=1), ERROR_PATTERN_422)

    @integration_test(True)
    def test_hostfactory_create_token_with_valid_and_invalid_cidr_raises_error(self):
        self.assertRegex(self.create_one_hour_token(cidr='1.2.3.4,1.2.3', exit_code=1), ERROR_PATTERN_422)

    @integration_test(True)
    def test_hostfactory_create_token_with_zero_value_duration_will_raise_error(self):
        self.assertRegex(self._create_token(duration=timedelta(days=0, hours=0, minutes=0), exit_code=1),
                         INVALID_DURATION_ERROR_MSG)

    @integration_test(True)
    def test_hostfactory_create_token_with_all_duration_flags_returns_correct_response(self):
        duration = timedelta(days=1, hours=1, minutes=1)
        response = self._create_token(duration=duration)
        self.assert_create_token_response(response, expected_expiration_duration=duration)

    @integration_test(True)
    def test_hostfactory_create_token_with_only_days_duration_flags_returns_correct_response(self):
        duration = timedelta(days=365)
        response = self.cli_create_token('--duration-days', str(duration.days))
        self.assert_create_token_response(response, expected_expiration_duration=duration)

    @integration_test(True)
    def test_hostfactory_create_token_with_only_hours_duration_flags_returns_correct_response(self):
        duration_hours = 24
        response = self.cli_create_token('--duration-hours', str(duration_hours))
        self.assert_create_token_response(response, expected_expiration_duration=timedelta(hours=duration_hours))

    @integration_test(True)
    def test_hostfactory_create_token_with_only_minutes_duration_flags_returns_correct_response(self):
        duration_minutes = 60
        response = self.cli_create_token('--duration-minutes', str(duration_minutes))
        self.assert_create_token_response(response, expected_expiration_duration=timedelta(minutes=duration_minutes))

    @integration_test(True)
    def test_hostfactory_create_token_with_negative_duration_days_flags_raises_error(self):
        self.assertRegex(self.cli_create_token('--duration-days', '-1', exit_code=1),
                         INVALID_DURATION_ERROR_MSG)

    @integration_test(True)
    def test_hostfactory_create_token_without_duration_raises_error(self):
        self.assertRegex(self.cli_create_token(exit_code=1),
                         INVALID_DURATION_ERROR_MSG)

    @integration_test(True)
    def test_hostfactory_revoke_token_returns_correct_response(self):
        self.assertRegex(self.revoke_token(self.create_token()), 'Token \'.*\' has been revoked.\\n')

    @integration_test(True)
    def test_hostfactory_revoke_token_empty_token_raise_404_error(self):
        self.assertRegex(self.revoke_token('', exit_code=1), ERROR_PATTERN_404)

    @integration_test(True)
    def test_hostfactory_revoke_token_invalid_token_raise_404_error(self):
        self.assertRegex(self.revoke_token('non_exist', exit_code=1), ERROR_PATTERN_404)
