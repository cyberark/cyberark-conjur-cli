import unittest
from unittest.mock import patch

from test.util.cli_helpers import cli_test, cli_arg_test
from conjur.version import __version__
from conjur.cli import Cli

RESOURCE_LIST = [
    'some_id1',
    'some_id2',
]
WHOAMI_RESPONSE = {
    "account": "myaccount"
}

class CliTest(unittest.TestCase):
    @cli_test()
    def test_cli_without_args_shows_help(self, cli_invocation, output, client):
        self.assertIn("Usage:", output)

    @patch('conjur.cli.Cli')
    def test_cli_is_run_when_launch_is_invoked(self, cli_instance):
        Cli.launch()

        cli_instance.return_value.run.assert_called_once_with()

    @cli_test(["-h"])
    def test_cli_shows_help_with_short_help_flag(self, cli_invocation, output, client):
        self.assertIn("Usage:", output)

    @cli_test(["--help"])
    def test_cli_shows_help_with_long_help_flag(self, cli_invocation, output, client):
        self.assertIn("Usage:", output)

    @cli_test(["-v"])
    def test_cli_check_copyright_short_version_flag(self, cli_invocation, output, client):
        self.assertIn(f'''Conjur CLI version {format(__version__)}

Copyright (c) 2020 CyberArk Software Ltd. All rights reserved.
<www.cyberark.com>
''', str(output))

    @cli_test(["--version"])
    def test_cli_check_copyright_long_version_flag(self, cli_invocation, output, client):
        self.assertIn(f'''Conjur CLI version {format(__version__)}

Copyright (c) 2020 CyberArk Software Ltd. All rights reserved.
<www.cyberark.com>
''', str(output))

    # SSL Verify
    @cli_arg_test(["--insecure"], ssl_verify=False)
    def test_cli_passes_insecure_flag_to_client(self): pass

    # Main method invocations
    @cli_test(["variable", "set", "-i", "foo", "-v", "bar"])
    def test_cli_invokes_variable_set_correctly(self, cli_invocation, output, client):
        client.set.assert_called_once_with('foo', 'bar')

    @cli_test(["variable"])
    def test_cli_variable_parser_doesnt_break_without_action(self, cli_invocation, output, client):
        self.assertIn("Usage", output)

    @cli_test(["variable", "get", "-i", "foo"], get_output=b'A')
    def test_cli_invokes_variable_get_correctly(self, cli_invocation, output, client):
        client.get.assert_called_once_with("foo", None)

    @cli_test(["variable", "get", "-i", "foo", "bar"], get_many_output={"foo": "A", "bar": "B"})
    def test_cli_invokes_variable_get_correctly_with_multiple_vars(self, cli_invocation, output, client):
        client.get_many.assert_called_once_with('foo', 'bar')

    @cli_test(["variable", "get", "-i", "foo", "bar"], get_many_output={})
    def test_cli_variable_get_with_multiple_vars_doesnt_break_on_empty_input(self, cli_invocation, output, client):
        self.assertEquals('{}\n', output)

    @cli_test(["variable", "get", "-i", "foo", "bar"], get_many_output={"foo": "A", "bar": "B"})
    def test_cli_variable_get_with_multiple_vars_outputs_formatted_json(self, cli_invocation, output, client):
        self.assertEquals('{\n    "foo": "A",\n    "bar": "B"\n}\n', output)

    @cli_test(["policy"])
    def test_cli_policy_parser_doesnt_break_without_action(self, cli_invocation, output, client):
        self.assertIn("Usage:", output)

    # TODO will change when UX is finalized
    @cli_test(["policy", "--help"])
    def test_cli_policy_long_help_returns_help(self, cli_invocation, output, client):
        self.assertIn("usage:", output)

    # TODO will change when UX is finalized
    @cli_test(["policy", "-h"])
    def test_cli_policy_short_help_returns_help(self, cli_invocation, output, client):
        self.assertIn("usage:", output)

    # TODO will change when UX is finalized
    @cli_test(["policy", "load", "--help"])
    def test_cli_policy_load_long_help_returns_help(self, cli_invocation, output, client):
        self.assertIn("usage:", output)

    # TODO will change when UX is finalized
    @cli_test(["policy", "load", "-h"])
    def test_cli_policy_load_short_help_returns_help(self, cli_invocation, output, client):
        self.assertIn("usage:", output)

    # TODO will change when UX is finalized
    @cli_test(["policy", "replace", "-h"])
    def test_cli_policy_replace_short_returns_help(self, cli_invocation, output, client):
        self.assertIn("usage:", output)

    # TODO will change when UX is finalized
    @cli_test(["policy", "replace", "--help"])
    def test_cli_policy_replace_long_returns_help(self, cli_invocation, output, client):
        self.assertIn("usage:", output)

    # TODO will change when UX is finalized
    @cli_test(["policy", "update", "-h"])
    def test_cli_policy_update_short_returns_help(self, cli_invocation, output, client):
        self.assertIn("usage:", output)

    # TODO will change when UX is finalized
    @cli_test(["policy", "update", "--help"])
    def test_cli_policy_update_long_returns_help(self, cli_invocation, output, client):
        self.assertIn("usage:", output)

    @cli_test(["policy", "load", "-b", "foo", "-f", "foopolicy"])
    def test_cli_invokes_policy_load_correctly(self, cli_invocation, output, client):
        client.load_policy_file.assert_called_once_with('foo', 'foopolicy')

    @cli_test(["policy", "load", "-b", "foo", "-f", "foopolicy"], policy_change_output={})
    def test_cli_policy_load_doesnt_break_on_empty_input(self, cli_invocation, output, client):
        self.assertEquals('{}\n', output)

    @cli_test(["policy", "load", "-b", "foo", "-f", "foopolicy"], policy_change_output={"foo": "A", "bar": "B"})
    def test_cli_policy_load_outputs_formatted_json(self, cli_invocation, output, client):
        self.assertEquals('{\n    "foo": "A",\n    "bar": "B"\n}\n', output)

    @cli_test(["policy", "replace", "-b", "foo", "-f", "foopolicy"])
    def test_cli_invokes_policy_replace_correctly(self, cli_invocation, output, client):
        client.replace_policy_file.assert_called_once_with('foo', 'foopolicy')

    @cli_test(["policy", "replace", "-b", "foo", "-f", "foopolicy"], policy_change_output={})
    def test_cli_policy_replace_doesnt_break_on_empty_input(self, cli_invocation, output, client):
        self.assertEquals('{}\n', output)

    @cli_test(["policy", "replace", "-b", "foo", "-f", "foopolicy"], policy_change_output={"foo": "A", "bar": "B"})
    def test_cli_policy_replace_outputs_formatted_json(self, cli_invocation, output, client):
        self.assertEquals('{\n    "foo": "A",\n    "bar": "B"\n}\n', output)

    @cli_test(["policy", "update", "-b", "foo", "-f", "foopolicy"])
    def test_cli_invokes_policy_update_correctly(self, cli_invocation, output, client):
        client.update_policy_file.assert_called_once_with('foo', 'foopolicy')

    @cli_test(["policy", "update", "-b", "foo", "-f", "foopolicy"], policy_change_output={})
    def test_cli_policy_update_doesnt_break_on_empty_input(self, cli_invocation, output, client):
        self.assertEquals('{}\n', output)

    @cli_test(["policy", "update", "-b", "foo", "-f", "foopolicy"], policy_change_output={"foo": "A", "bar": "B"})
    def test_cli_policy_update_outputs_formatted_json(self, cli_invocation, output, client):
        self.assertEquals('{\n    "foo": "A",\n    "bar": "B"\n}\n', output)

    @cli_test(["list"], list_output=RESOURCE_LIST)
    def test_cli_invokes_resource_listing_correctly(self, cli_invocation, output, client):
        client.list.assert_called_once_with({})

    @cli_test(["list"], list_output=RESOURCE_LIST)
    def test_cli_resource_listing_outputs_formatted_json(self, cli_invocation, output, client):
        self.assertEquals('[\n    "some_id1",\n    "some_id2"\n]\n', output)

    # TODO will change when UX is finalized
    @cli_test(["user"])
    def test_cli_user_retuns_main_help(self, cli_invocation, output, client):
        self.assertIn("Usage:\n", output)

    # TODO will change when UX is finalized
    @cli_test(["user", "-h"])
    def test_cli_user_short_help_returns_user_help(self, cli_invocation, output, client):
        self.assertIn("Name:\n  user", output)

    # TODO will change when UX is finalized
    @cli_test(["user", "--help"])
    def test_cli_user_long_help_returns_user_help(self, cli_invocation, output, client):
        self.assertIn("Name:\n  user", output)

    # TODO will change when UX is finalized
    @cli_test(["user", "rotate-api-key", "-h"])
    def test_cli_user_rotate_api_key_short_help_returns_rotate_api_key_help(self, cli_invocation, output, client):
        self.assertIn("Name:\n  rotate-api-key", output)

    # TODO will change when UX is finalized
    @cli_test(["user",  "rotate-api-key", "--help"])
    def test_cli_user_rotate_api_key_long_help_returns_rotate_api_key_help(self, cli_invocation, output, client):
        self.assertIn("Name:\n  rotate-api-key", output)

    # TODO will change when UX is finalized
    @cli_test(["user", "change-password", "-h"])
    def test_cli_user_change_password_short_help_returns_change_password_help(self, cli_invocation, output, client):
        self.assertIn("Name:\n  change-password", output)

    # TODO will change when UX is finalized
    @cli_test(["user", "change-password", "--help"])
    def test_cli_user_change_password_long_help_returns_change_password_help(self, cli_invocation, output, client):
        self.assertIn("Name:\n  change-password", output)

    @cli_test(["user", "rotate-api-key", "-i", "someuserid"], rotate_api_key_output="123key")
    def test_cli_host_rotate_api_key_outputs_api_correctly(self, cli_invocation, output, client):
        client.rotate_other_api_key.assert_called_once_with('user', 'someuserid')

    # TODO will change when UX is finalized
    @cli_test(["host", "-h"])
    def test_cli_host_short_help_returns_host_help(self, cli_invocation, output, client):
        self.assertIn("Name:\n  host", output)

    # TODO will change when UX is finalized
    @cli_test(["host", "--help"])
    def test_cli_host_long_help_returns_host_help(self, cli_invocation, output, client):
        self.assertIn("Name:\n  host", output)

    # TODO will change when UX is finalized
    @cli_test(["host", "rotate-api-key", "-h"])
    def test_cli_host_rotate_api_key_short_help_returns_rotate_api_key_help(self, cli_invocation, output, client):
        self.assertIn("Name:\n  rotate-api-key", output)

    # TODO will change when UX is finalized
    @cli_test(["host",  "rotate-api-key", "--help"])
    def test_cli_host_rotate_api_key_long_help_returns_rotate_api_key_help(self, cli_invocation, output, client):
        self.assertIn("Name:\n  rotate-api-key", output)

    @cli_test(["host", "rotate-api-key", "-i", "somehostid"])
    def test_cli_host_rotate_api_key_outputs_api_correctly(self, cli_invocation, output, client):
        client.rotate_other_api_key.assert_called_once_with('host', 'somehostid')

    @cli_test(["whoami"], whoami_output=WHOAMI_RESPONSE)
    def test_cli_invokes_whoami_correctly(self, cli_invocation, output, client):
        client.whoami.assert_called_once_with()

    @cli_test(["whoami"], whoami_output=WHOAMI_RESPONSE)
    def test_cli_invokes_whoami_outputs_formatted_json(self, cli_invocation, output, client):
        self.assertEquals('{\n    "account": "myaccount"\n}\n', output)
