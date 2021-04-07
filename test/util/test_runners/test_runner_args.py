from argparse import ArgumentParser


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
#
# The main reason for these limitations is that we run in debug mode and all items that are printed to the
# screen are captured.

class TestRunnerArgs:
    """
    DTO to hold the tests environment arguments
    """

    def __init__(self, run_oss_tests, url, account, login, password,
                 cli_to_test: str, files_folder: str,
                 test_name_identifier="integration"):
        self.run_oss_tests = run_oss_tests
        self.hostname = url
        self.account = account
        self.login = login
        self.password = password
        self.test_name_identifier = test_name_identifier
        # Tests
        self.invoke_cli_as_process = cli_to_test is not None and len(cli_to_test)>0
        if self.invoke_cli_as_process and test_name_identifier == 'integration':
            self.test_name_identifier = "test_with_process"
        self.cli_to_test = cli_to_test
        self.files_folder = files_folder

    @staticmethod
    def create_from_args():
        """
        --invoke-cli-as-process, required to run the CLI as a process

        Parameters like --url, --account, --login, --password, will used be to configure the CLI. These values
        are used before each test profile is run to configure the CLI and run the
        integration tests successfully

        --cli-to-test, path to the packed CLI executable to test against.

        --files-folder path to test assets (policy files, etc).
        You can find this folder under /test/test_config in the repo.
        Copy this executable into every OS you wish to run the CLI integration tests.

        --identifier the test method with this identifier will be run (`integration` by default).
        To run as a process, the identifier should be `test_with_process`
        """
        parser = ArgumentParser(description='Test arguments')

        # Add the arguments
        parser.add_argument('--oss', dest='run_oss_tests', action='store_true',
                            help='Added to run OSS-specific tests')
        parser.add_argument('-i', '--identifier', dest='test_name_identifier', action='store', default='integration',
                            help='the test method with this identifier will be run (integration by default).')
        parser.add_argument('-u', '--url', dest='url', action='store', default='https://conjur-https',
                            help='server host name')
        parser.add_argument('-a', '--account', dest='account', action='store', default='dev', help='account name')
        parser.add_argument('-l', '--login', dest='login', action='store', default='admin', help='user name')
        parser.add_argument('-p', '--password', dest='password', action='store', help='the user password')
        parser.add_argument('-c', '--cli-to-test', dest='cli_to_test', action='store',
                            help='the cli binaries to test')
        parser.add_argument('-f', '--files-folder', dest='files_folder', action='store', default='./test',
                            help='where the test assets are located')
        args = parser.parse_args()
        return TestRunnerArgs(**vars(args))
