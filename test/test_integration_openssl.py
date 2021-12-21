# -*- coding: utf-8 -*-

"""
CLI OpenSSL Integration tests
This test file handles the main test flows for the variable command
"""
import ssl

from test.util.test_infrastructure import integration_test
from test.util.test_runners.integration_test_case import IntegrationTestCaseBase
from test.util import test_helpers as utils


class CliIntegrationTestOpenSSL(IntegrationTestCaseBase):  # pragma: no cover

    def __init__(self, testname, client_params=None, environment_params=None):
        super(CliIntegrationTestOpenSSL, self).__init__(testname, client_params, environment_params)

    # *************** HELPERS ***************

    def setUp(self):
        pass

    @integration_test(True)
    def test_open_ssl_version_is_sufficient(self):
        version = ssl.OPENSSL_VERSION.split(' ')[1]
        self.assertGreaterEqual(version, "1.1.1k",
                                f"Insufficient OpenSSL version, 1.1.1k and above is expected got '{ssl.OPENSSL_VERSION}'")
