import io
import itertools
import sys
from contextlib import redirect_stdout
from functools import wraps

from unittest.mock import patch, MagicMock

from conjur_api_python3.cli import Cli

def invoke_cli(test_runner, *args):
    capture_stream = io.StringIO()
    cli_args = list(itertools.chain(*args))

    with test_runner.assertRaises(SystemExit) as sys_exit:
        with redirect_stdout(capture_stream):
            with patch.object(sys, 'argv', ["cli"] + cli_args):
                Cli().run()

    test_runner.assertEqual(sys_exit.exception.code, 0,
        "ERROR: CLI returned an unexpected error status code: '{}'".format(cli_args))
    return capture_stream.getvalue()

def integration_test(original_function):
    @wraps(original_function)
    def test_wrapper_func(self, *inner_args, **inner_kwargs):
        return original_function(self, *inner_args, **inner_kwargs)

    test_wrapper_func.integration = True

    return test_wrapper_func

def cli_test(cli_args=[], integration=False):
    cli_command = 'cli {}'.format(' '.join(cli_args))

    def test_cli_decorator(original_function):
        @wraps(original_function)
        def test_wrapper_func(self, *inner_args, **inner_kwargs):
            capture_stream = io.StringIO()
            client_instance_mock = MagicMock()

            with self.assertRaises(SystemExit) as sys_exit:
                with redirect_stdout(capture_stream):
                    with patch.object(sys, 'argv', ["cli"] + cli_args), \
                            patch('conjur_api_python3.cli.Client') as mock_client:
                        mock_client.return_value = client_instance_mock
                        Cli().run()

            self.assertEqual(sys_exit.exception.code, 0,
                "ERROR: CLI returned an unexpected error status code: '{}'".format(cli_command))
            original_function(self, cli_command, capture_stream.getvalue(), client_instance_mock)

        # Set integration flag if specified
        test_wrapper_func.integration = integration

        return test_wrapper_func
    return test_cli_decorator
