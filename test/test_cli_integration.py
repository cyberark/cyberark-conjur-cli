import unittest

from .util.cli_helpers import cli_test

from conjur_api_python3.version import __version__

class CliTest(unittest.TestCase):
    @cli_test(["variable", "set", "one/password", "onepasswordvalue"], integration=True)
    def test_cli_can_set_a_variable(self, output):
        self.assertEquals("aaa", "bbb")

    @cli_test(["variable", "get", "one/password"], integration=True)
    def test_cli_can_get_a_variable(self, output):
        self.assertEquals("onepasswordvalue", output)
