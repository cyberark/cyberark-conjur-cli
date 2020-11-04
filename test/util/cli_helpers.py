import io
import itertools
import sys
from contextlib import redirect_stdout
from functools import wraps

from unittest.mock import patch, MagicMock

from conjur.cli import Cli

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

def cli_test(cli_args=[], integration=False, get_many_output=None, list_output=None,
        policy_change_output={}, whoami_output={}):
    cli_command = 'cli {}'.format(' '.join(cli_args))

    def test_cli_decorator(original_function):
        @wraps(original_function)
        def test_wrapper_func(self, *inner_args, **inner_kwargs):
            capture_stream = io.StringIO()
            client_instance_mock = MagicMock()
            client_instance_mock.get_many.return_value = get_many_output
            client_instance_mock.list.return_value = list_output
            client_instance_mock.apply_policy_file.return_value = policy_change_output
            client_instance_mock.replace_policy_file.return_value = policy_change_output
            client_instance_mock.delete_policy_file.return_value = policy_change_output
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

def cli_arg_test(cli_args=[], **kwargs):
    cli_args += ['variable', 'get', 'foo']
    cli_command = 'cli {}'.format(' '.join(cli_args))

    default_args = {
        'account': None,
        'api_key': None,
        'ca_bundle': None,
        'debug': False,
        'login_id': None,
        'password': None,
        'ssl_verify': True,
        'url': None
    }
    expected_args = {**default_args, **kwargs}

    def test_cli_decorator(original_function):
        @wraps(original_function)
        def test_wrapper_func(self, *inner_args, **inner_kwargs):
            capture_stream = io.StringIO()
            client = None

            with self.assertRaises(SystemExit) as sys_exit:
                with redirect_stdout(capture_stream):
                    with patch.object(sys, 'argv', ["cli"] + cli_args), \
                            patch('conjur.cli.Client') as mock_client:
                        mock_client.return_value = MagicMock()
                        client = mock_client

                        Cli().run()

            self.assertEqual(sys_exit.exception.code, 0,
                "ERROR: CLI returned an unexpected error status code: '{}'".format(cli_command))

            client.assert_called_once_with(**expected_args)
            original_function(self)

        return test_wrapper_func
    return test_cli_decorator
