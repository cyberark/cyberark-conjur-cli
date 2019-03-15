import unittest

from .util.cli_helpers import cli_test

from conjur_api_python3.version import __version__

class CliTest(unittest.TestCase):
    @cli_test()
    def test_cli_without_args_shows_help(self, cli_invocation, output):
        self.assertIn("usage: cli", output)

    @cli_test(["-h"])
    def test_cli_shows_help_with_short_help_flag(self, cli_invocation, output):
        self.assertIn("usage: cli", output)

    @cli_test(["--help"])
    def test_cli_shows_help_with_long_help_flag(self, cli_invocation, output):
        self.assertIn("usage: cli", output)

    @cli_test(["-v"])
    def test_cli_shows_version_with_short_version_flag(self, cli_invocation, output):
        self.assertEquals("cli v{}\n".format(__version__), output)

    @cli_test(["--version"])
    def test_cli_shows_version_with_long_version_flag(self, cli_invocation, output):
        self.assertEquals("cli v{}\n".format(__version__), output)