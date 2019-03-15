import io
import sys
from contextlib import redirect_stdout
from functools import wraps

from unittest.mock import patch

from conjur_api_python3.cli import Cli

def cli_test(cli_args=[], integration=False):
    def test_cli_decorator(original_function):
        @wraps(original_function)
        def test_wrapper_func(self, *inner_args, **inner_kwargs):
            capture_stream = io.StringIO()
            with self.assertRaises(SystemExit) as sys_exit:
                with redirect_stdout(capture_stream):
                    with patch.object(sys, 'argv', ["cli"] + cli_args):
                        Cli().run()

            self.assertEqual(sys_exit.exception.code, 0)
            original_function(self, capture_stream.getvalue())

        # Set integration flag if specified
        test_wrapper_func.integration = integration

        return test_wrapper_func
    return test_cli_decorator
