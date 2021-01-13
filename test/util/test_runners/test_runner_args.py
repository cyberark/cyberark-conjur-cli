from argparse import ArgumentParser


class TestRunnerArgs:
    """
    DTO to hold the tests environment arguments
    """

    def __init__(self, run_oss_tests, url, account, login, password, invoke_cli_as_process,
                 working_cli_path_only_for_init: str,
                 cli_to_test: str, files_folder: str, allow_same_binaries=False,
                 test_name_identifier="integration"):
        self.run_oss_tests = run_oss_tests
        self.hostname = url
        self.account = account
        self.login = login
        self.password = password
        self.test_name_identifier = test_name_identifier
        self.invoke_cli_as_process = invoke_cli_as_process
        self.working_cli_path_only_for_init = working_cli_path_only_for_init
        self.cli_to_test = cli_to_test
        self.files_folder = files_folder
        # will throw if the user test the same known working binaries
        if cli_to_test is not None and not allow_same_binaries and working_cli_path_only_for_init.lower() == cli_to_test.lower():
            raise RuntimeError("cli to start enviroment and tested cli are on the same path")

    @staticmethod
    def create_from_args():
        """
        --invoke_cli_as_process , required to run the CLI as a process
        --working_cli_path the path to a working CLI executable.
        This path is needed for initial configuration of the CLI.
        You can find this executable under /test/test_config/binaries/config
        in the repo. Copy this executable into every OS you wish to run the
        CLI integration tests.
        Parameters like -u, -a, -l, -p, will configure the conjurrc and netrc
        needed to run the integration tests successfully.
        --cli_to_test path to the CLI executable to test against.
        --files_folder path to test assets (policy files, etc).
        You can find this folder under /test/test_config in the repo.
        Copy this executable into every OS you wish to run the CLI integration tests.
        --identifier the test method with this identifier will be run (integration by default).
        """
        parser = ArgumentParser(description='Test arguments')

        # Add the arguments
        parser.add_argument('--oss', dest='run_oss_tests', action='store_true',
                            help='Added to run OSS-specific tests')
        parser.add_argument('-p_invoke', '--invoke_cli_as_process', action='store_true', default=True,
                            help='If added, integration tests will run as a process executable. Otherwise it will run '
                                 'as code, requiring Python')
        parser.add_argument('-i', '--identifier', dest='test_name_identifier', action='store', default='integration',
                            help='the test method with this identifier will be run (integration by default).')
        parser.add_argument('-u', '--url', dest='url', action='store', default='https://conjur-https',
                            help='server host name')
        parser.add_argument('-a', '--account', dest='account', action='store', default='dev', help='account name')
        parser.add_argument('-l', '--login', dest='login', action='store', default='admin', help='user name')
        parser.add_argument('-p', '--password', dest='password', action='store', help='the user password')
        parser.add_argument('-w', '--working_cli', dest='working_cli_path_only_for_init', action='store',
                            help='the cli path using to set up the enviorment')
        parser.add_argument('-c', '--cli_to_test', dest='cli_to_test', action='store',
                            help='the cli binaries to test')
        parser.add_argument('-f', '--files_folder', dest='files_folder', action='store', default='./test',
                            help='where the test assets are located')
        parser.add_argument('-s', '--same', dest='allow_same_binaries', action='store_true',
                            help='If added cli_to_test and working_cli can address the same path')
        args = parser.parse_args()
        return TestRunnerArgs(**vars(args))
