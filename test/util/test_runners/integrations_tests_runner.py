"""
This is a runner module for all integration tests.
The purpose of this file is to be a cross platform tests runner
for all integration tests
"""

# *************** DEVELOPER NOTE ***************
# We have the ability to run our tests as a process which means we can run our tests as a user would,
# without Python on the machine, using the Conjur CLI exec a customer would. Currently, some tests still
# cannot run as a process. Tests that meet the following criteria cannot be run as a process and are given
# the integration_test() decorator:
# 1. any test that contains of error/stderr
# 2. any test that runs a command that uses getpass (login and user commands)
# 3. any test that has assertEquals. All new tests should use assertIn
# 4. any test that uses a tmp file (policy command)
# 5. any test that uses contents returned from invoke_cli
# 6. any test that depends on keyring disable (mainly in CliIntegrationTestCredentialsNetrc)
#
# The main reason for these limitations is that we run in debug mode and all items that are printed to the
# screen are captured.

# Builtins
import sys
import os

sys.path.append('.')
sys.path.append('..')

# Third party
import unittest.mock
import unittest
import base64
import requests
import logging

# NOTE do not delete this import even though it seems to not be used. This used to
# run the integration tests as a process. Otherwise this dependency will not be available
# once the test module is packed
import uuid

# Internals
from test.test_integration_policy import CliIntegrationPolicy
from test.test_integration_variable import CliIntegrationTestVariable
from test.test_integration_configurations import CliIntegrationTestConfigurations
from test.test_integration_credentials_keyring import CliIntegrationTestCredentialsKeyring
from test.test_integration_list import CliIntegrationTestList
from test.test_integration_credentials_netrc import CliIntegrationTestCredentialsNetrc
from test.test_integration_oss import CliIntegrationTestOSS
from test.test_integration_resource import CliIntegrationResourceTest
from test.util.test_runners.integration_test_case import IntegrationTestCaseBase
from test.util.test_runners.test_runner_args import TestRunnerArgs
from test.util.test_runners.params import ClientParams, TestEnvironmentParams
from test.util.test_path_provider import TestRunnerPathProvider
from conjur.constants import *


def main():
    args = TestRunnerArgs.create_from_args()
    runner = TestRunner(args)
    test_to_run_list = [
        CliIntegrationTestCredentialsKeyring,
        CliIntegrationTestCredentialsNetrc,
        CliIntegrationTestConfigurations,
        CliIntegrationTestVariable,
        CliIntegrationResourceTest,
        CliIntegrationTestList,
        CliIntegrationPolicy
    ]
    if args.run_oss_tests:
        test_to_run_list.append(CliIntegrationTestOSS)
    runner.run_tests(test_modules=test_to_run_list)


class TestRunner:  # pragma: no cover

    def __init__(self, args: TestRunnerArgs):
        self.runner_args = args
        self.api_key = self.__get_api_key()
        self.start_env()

    def run_tests(self, test_modules: list):
        """
        @param test_modules: the tests classes wanted to run
        """
        res = []
        for test_module in test_modules:
            res.append(self.__run_test_cases(test_module))
        exit_code = not all(res)
        if exit_code == 0:
            print("All tests passed")
        else:
            print("Not all tests passed")

        sys.exit(exit_code)

    def start_env(self):
        """
        set up the test environment
        Test environment setup will be in the following order:
        1) Run conjur init to initialize the CLI and get the certificate and conjurrc files
        2) Run login a login to CLI and generate netrc file
        """

        path_provider = TestRunnerPathProvider(file_helper_dir=self.runner_args.files_folder)
        self.env_params = TestEnvironmentParams(self.runner_args.cli_to_test, self.runner_args.invoke_cli_as_process,
                                                path_provider)
        self.client_params = ClientParams(url=self.runner_args.hostname, account=self.runner_args.account,
                                          login=self.runner_args.login, api_key=self.api_key)
        if (os.getenv('TEST_ENV') is None):
            os.environ['TEST_ENV'] = 'True'

    def __get_api_key(self):
        url = f"{self.runner_args.hostname}/authn/{self.runner_args.account}/login"
        encode = base64.b64encode(f"{self.runner_args.login}:{self.runner_args.password}".encode('utf-8')).decode(
            'utf-8')
        headers = {'Authorization': f'Basic {encode}'}

        response = requests.request("GET", url, headers=headers, data={},
                                    verify=False)  # verify=False == like --insecure

        return response.text

    def __run_test_cases(self, test_cases_class: IntegrationTestCaseBase):
        """
        Run class tests.
         @type test_cases_class: IntegrationTestCaseBase
        """
        test_names = self.__get_relevant_tests_for_class(test_cases_class)  # we filter by test_name_identifier
        suite = unittest.TestSuite()
        print("Now running: ", test_cases_class.__name__)
        for test_name in test_names:
            specific_test = test_cases_class(test_name, self.client_params, self.env_params)
            suite.addTest(specific_test)
        result = unittest.TextTestRunner().run(suite)
        print("Failed: ", "\n".join([str(f[0]).split(" ")[0] for f in result.failures]))
        return result.wasSuccessful()

    def __get_relevant_tests_for_class(self, class_name: IntegrationTestCaseBase) -> list:
        """
        filter out only tests with property named like test_name_identifier
        this mimics nose2's filtering strategy
        @param class_name: the class to take the tests from
        @return: list of all relevant tests
        """
        import inspect
        ret = []
        all_test_definitions = inspect.getmembers(class_name, predicate=inspect.isfunction)
        for test_definition in all_test_definitions:
            test_name = test_definition[0]
            test_obj = test_definition[1]
            if getattr(test_obj, self.runner_args.test_name_identifier, None):
                ret.append(str(test_name))
        return ret


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    main()
