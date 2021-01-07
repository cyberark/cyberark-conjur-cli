"""
extend the unitest TestCase class
"""

# Builtins
import io
import sys

# Third party
import itertools
from unittest import TestCase
from contextlib import redirect_stdout
import subprocess as sp
from unittest.mock import patch, MagicMock

# Internals
from conjur.cli import Cli
from test.util.test_runners.params import ClientParams, TestEnvironmentParams


class IntegrationTestCaseBase(TestCase):

    def __init__(self, testname, client_params: ClientParams = None,
                 environment_params: TestEnvironmentParams = None):
        """
        Base class that extends unittest TestCase
        used to setup tests environment
        """
        self.environment = TestEnvironmentParams() if environment_params is None else environment_params
        self.client_params = ClientParams() if client_params is None else client_params

        super(IntegrationTestCaseBase, self).__init__(testname)


    def invoke_cli(self, *args, exit_code=0) -> str:
        """
        Invoker for the integration tests.
        if self.environment.invoke_process == True
        than it will call the cli binaries to run the integration tests
        else it will use the Cli code to invoke
        """
        if self.environment.invoke_process:
            return invoke_cli_as_process(self, *args, exit_code=exit_code)
        return invoke_cli_as_code(self, *args, exit_code=exit_code)


def invoke_cli_as_code(test_runner, *args, exit_code=0):
    """
        Invoke cli command using python code as seen below.
        The usecase of this is when we run the tests
        on development environment (when you run from
        python ide or run this file as python script)
        @param test_runner:
        @param args: the cli args input
        @param exit_code:
        @return: the cli string response
        """
    capture_stream = io.StringIO()
    cli_args = list(itertools.chain(*args))
    with test_runner.assertRaises(SystemExit) as sys_exit:
        with redirect_stdout(capture_stream):
            with patch.object(sys, 'argv', ["cli"] + cli_args):
                Cli().run()

    test_runner.assertEqual(sys_exit.exception.code, exit_code,
                            "ERROR: CLI returned an unexpected error status code: '{}'".format(cli_args))
    return capture_stream.getvalue()


def invoke_cli_as_process(test_runner, *args, exit_code=0) -> str:
    """
    Invoke cli command using cli executable.
    The usecase of this is when we run the tests
    on tests environment. will help tests integration
    on Windows, macOS, RHEL
    @param test_runner:
    @param args: the cli args input
    @param exit_code:
    @return: the cli string response
    """
    cli_args = list(itertools.chain(*args))
    run_cli_cmd = f"{test_runner.environment.cli_to_test}"

    child = sp.Popen([run_cli_cmd] + cli_args, stdout=sp.PIPE)
    output = child.communicate()[0]
    process_exit_code = child.returncode

    test_runner.assertEqual(process_exit_code, exit_code,
                            "ERROR: CLI returned an unexpected error status code: '{}'".format(cli_args))
    return output.decode('utf-8')
