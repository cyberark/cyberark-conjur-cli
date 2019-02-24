import io
import os
import sys
from contextlib import redirect_stdout
from functools import wraps

import unittest
from unittest.mock import MagicMock, patch

from conjur_api_python3.cli import Cli
from conjur_api_python3.version import __version__

class CliTest(unittest.TestCase):

    def cli_test(cli_args, *args, **kwargs):
        def test_cli_decorator(original_function):
            @wraps(original_function)
            def test_wrapper_func(self, *inner_args, **inner_kwargs):
                capture_stream = io.StringIO()
                with self.assertRaises(SystemExit) as sys_exit:
                    with redirect_stdout(capture_stream):
                        with patch.object(sys, 'argv', cli_args):
                            Cli().run()

                self.assertEqual(sys_exit.exception.code, 0)
                original_function(self, capture_stream.getvalue())

            return test_wrapper_func
        return test_cli_decorator

    @cli_test(["cli"])
    def test_cli_without_args_shows_help(self, output):
        self.assertIn("usage: cli", output)

    @cli_test(["cli", "-h"])
    def test_cli_shows_help_with_short_help_flag(self, output):
        self.assertIn("usage: cli", output)

    @cli_test(["cli", "--help"])
    def test_cli_shows_help_with_long_help_flag(self, output):
        self.assertIn("usage: cli", output)

    @cli_test(["cli", "-v"])
    def test_cli_shows_version_with_short_version_flag(self, output):
        self.assertEquals("cli v{}\n".format(__version__), output)

    @cli_test(["cli", "--version"])
    def test_cli_shows_version_with_long_version_flag(self, output):
        self.assertEquals("cli v{}\n".format(__version__), output)

    # TODO: Test variable get
    # TODO: Test variable set
