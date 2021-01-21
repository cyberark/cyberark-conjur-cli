# Builtins
import io
import sys

# Third party
from contextlib import redirect_stdout
from functools import wraps

# Internals
from unittest.mock import patch, MagicMock
from conjur.cli import Cli


def integration_test(should_run_as_process=False):
    def function_decorator(original_function):
        @wraps(original_function)
        def test_wrapper_func(self, *inner_args, **inner_kwargs):
            return original_function(self, *inner_args, **inner_kwargs)

        if should_run_as_process:
            test_wrapper_func.test_with_process = True
        test_wrapper_func.integration = True

        return test_wrapper_func

    return function_decorator


def cli_test(cli_args=[], integration=False, get_many_output=None, get_output=None, list_output=None,
             policy_change_output={}, whoami_output={}):
    cli_command = 'cli {}'.format(' '.join(cli_args))

    def test_cli_decorator(original_function):
        @wraps(original_function)
        def test_wrapper_func(self, *inner_args, **inner_kwargs):
            capture_stream = io.StringIO()
            client_instance_mock = MagicMock()
            client_instance_mock.get.return_value = get_output
            client_instance_mock.get_many.return_value = get_many_output
            client_instance_mock.list.return_value = list_output
            client_instance_mock.load_policy_file.return_value = policy_change_output
            client_instance_mock.replace_policy_file.return_value = policy_change_output
            client_instance_mock.update_policy_file.return_value = policy_change_output
            client_instance_mock.whoami.return_value = whoami_output
            with self.assertRaises(SystemExit) as sys_exit:
                with redirect_stdout(capture_stream):
                    with patch.object(sys, 'argv', ["cli"] + cli_args), \
                         patch('conjur.cli.Client') as mock_client:
                        mock_client.return_value = client_instance_mock
                        Cli().run()

            self.assertEqual(sys_exit.exception.code, 0,
                             "ERROR: CLI returned an unexpected error status code: '{}'".format(cli_command))
            original_function(self, cli_command, capture_stream.getvalue(), client_instance_mock)

        # Set integration flag if specified
        test_wrapper_func.integration = integration

        return test_wrapper_func

    return test_cli_decorator


def cli_arg_test(cli_args=None, **kwargs):
    if cli_args is None:
        cli_args = []
    cli_args += ['variable', 'get', '-i', 'foo']
    cli_command = 'cli {}'.format(' '.join(cli_args))
    default_args = {'debug': False}
    expected_args = {**default_args, **kwargs}

    def test_cli_decorator(original_function):
        @wraps(original_function)
        def test_wrapper_func(self, *inner_args, **inner_kwargs):
            capture_stream = io.StringIO()
            client_instance_mock = MagicMock()
            client_instance_mock.get.return_value = b'foo'

            client = None
            with self.assertRaises(SystemExit) as sys_exit:
                with redirect_stdout(capture_stream):
                    with patch.object(sys, 'argv', ["cli"] + cli_args), \
                         patch('conjur.cli.Client') as mock_client:
                        mock_client.return_value = client_instance_mock
                        client = mock_client

                        Cli().run()

            self.assertEqual(sys_exit.exception.code, 0,
                             "ERROR: CLI returned an unexpected error status code: '{}'".format(cli_command))

            client.assert_called_once_with(**expected_args)
            original_function(self)

        return test_wrapper_func

    return test_cli_decorator
