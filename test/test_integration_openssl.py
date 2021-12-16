# -*- coding: utf-8 -*-

"""
CLI OpenSSL Integration tests
This test file handles the main test flows for the variable command
"""

from test.util.test_infrastructure import integration_test
from test.util.test_runners.integration_test_case import IntegrationTestCaseBase
from test.util import test_helpers as utils


class CliIntegrationTestOpenSSL(IntegrationTestCaseBase):  # pragma: no cover

    def __init__(self, testname, client_params=None, environment_params=None):
        super(CliIntegrationTestOpenSSL, self).__init__(testname, client_params, environment_params)

    # *************** HELPERS ***************

    def setUp(self):
        self.setup_cli_params({})
        # Used to configure the CLI and login to run tests
        utils.setup_cli(self)
        return self.invoke_cli(self.cli_auth_params,
                               ['policy', 'replace', '-b', 'root', '-f',
                                self.environment.path_provider.get_policy_path("initial")])

    # *************** TESTS ***************

    @integration_test()
    def test_open_ssl_version_is_sufficient(self):
        import ssl
        version = ssl.OPENSSL_VERSION.split(' ')[1]
        result = version in ['1.1.1k', '1.1.1l']
        self.assertTrue(result,
                        f"Insufficient OpenSSL version, 1.1.1k and above is expected got '{ssl.OPENSSL_VERSION}'")

    test_open_ssl_version_is_sufficient.id1 = True
