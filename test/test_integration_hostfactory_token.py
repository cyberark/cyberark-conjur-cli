# -*- coding: utf-8 -*-

"""
CLI Hostfactory Integration tests

This test file handles the main test flows for the hostfactory command
"""

# Not coverage tested since integration tests doesn't run in
# the same build step
from datetime import timedelta
from test.util.test_infrastructure import integration_test
from test.test_integration_hostfactory import CliIntegrationTestHostFactory, \
    ERROR_PATTERN_404, ERROR_PATTERN_422, INVALID_DURATION_ERROR_MSG

# Helper methods
token_response_empty_cidr_regex = CliIntegrationTestHostFactory.token_response_empty_cidr_regex
one_hour_from_now = CliIntegrationTestHostFactory.one_hour_from_now
token_response_regex = CliIntegrationTestHostFactory.token_response_regex
time_iso_format_exclude_seconds = CliIntegrationTestHostFactory.time_iso_format_exclude_seconds


class CliIntegrationTestHostFactoryToken(CliIntegrationTestHostFactory):  # pragma: no cover

    def __init__(self, test_name, client_params=None, environment_params=None):
        super(CliIntegrationTestHostFactoryToken, self).__init__(test_name, client_params, environment_params)

    # *************** TESTS ***************

    @integration_test(True)
    def test_hostfactory_create_token_returns_correct_response(self):
        self.assertRegex(self._create_token(), token_response_empty_cidr_regex(one_hour_from_now()))

    @integration_test(True)
    def test_hostfactory_create_token_without_id_returns_menu(self):
        output = self.invoke_cli(self.cli_auth_params,
                                 ['hostfactory', 'create', 'token'],
                                 exit_code=1)
        self.assertRegex(output, ".*token - Creates a token for creating hosts with restrictions\n\nUsage:\n.*")

    @integration_test(True)
    def test_hostfactory_create_token_with_unknown_hostfactory_id_raises_404_error(self):
        self.assertRegex(self._create_token(host_factory='some-unknown-hostfactory', exit_code=1), ERROR_PATTERN_404)

    @integration_test(True)
    def test_hostfactory_create_token_with_no_cidr_returns_empty_cidr_list_in_response(self):
        self.assertRegex(self._create_token(), token_response_empty_cidr_regex(one_hour_from_now()))

    @integration_test(True)
    def test_hostfactory_create_token_with_single_cidr_returns_cidr_in_response(self):
        self.assertRegex(self.create_one_hour_token(cidr='1.2.3.4'),
                         token_response_regex('1.2.3.4/32'))

    @integration_test(True)
    def test_hostfactory_create_token_with_multiple_ciders_returns_cidrs_in_response(self):
        self.assertRegex(self.create_one_hour_token(cidr='1.2.3.4,2.2.2.2'),
                         token_response_regex('1.2.3.4/32",\n            "2.2.2.2/32'))

    @integration_test(True)
    def test_hostfactory_create_token_with_low_cidr_range_returns_cidrs_in_response(self):
        self.assertRegex(self.create_one_hour_token(cidr='1.2.0.0/16'), token_response_regex('1.2.0.0/16'))

    @integration_test(True)
    def test_hostfactory_create_token_wrong_cidr_format_raises_error(self):
        self.assertRegex(self.create_one_hour_token(cidr='1.2.3', exit_code=1), ERROR_PATTERN_422)

    @integration_test(True)
    def test_hostfactory_create_token_wrong_cidr_format_range_raises_error(self):
        self.assertRegex(self.create_one_hour_token(cidr='1.2.3/16', exit_code=1), ERROR_PATTERN_422)

    test_hostfactory_create_token_wrong_cidr_format_range_raises_error.id1 = True

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
        self.assertRegex(self._create_token(duration=duration),
                         token_response_empty_cidr_regex(duration=time_iso_format_exclude_seconds(duration)))

    @integration_test(True)
    def test_hostfactory_create_token_with_only_days_duration_flags_returns_correct_response(self):
        self.assertRegex(self.cli_create_token('--duration-days', '365'),
                         token_response_empty_cidr_regex(
                             duration=time_iso_format_exclude_seconds(timedelta(days=365, hours=0, minutes=0))))

    @integration_test(True)
    def test_hostfactory_create_token_with_only_hours_duration_flags_returns_correct_response(self):
        self.assertRegex(self.cli_create_token('--duration-hours', '24'),
                         token_response_empty_cidr_regex(duration=time_iso_format_exclude_seconds(
                             timedelta(days=0, hours=24, minutes=0))))

    @integration_test(True)
    def test_hostfactory_create_token_with_only_minutes_duration_flags_returns_correct_response(self):
        self.assertRegex(self.cli_create_token('--duration-minutes', '60'),
                         token_response_empty_cidr_regex(duration=time_iso_format_exclude_seconds(
                             timedelta(days=0, hours=0, minutes=60))))

    @integration_test(True)
    def test_hostfactory_create_token_with_negative_duration_days_flags_raises_error(self):
        self.assertRegex(self.cli_create_token('--duration-days', '-1', exit_code=1),
                         INVALID_DURATION_ERROR_MSG)

    @integration_test(True)
    def test_hostfactory_create_token_without_duration_raises_error(self):
        self.assertRegex(self.cli_create_token(exit_code=1),
                         INVALID_DURATION_ERROR_MSG)
