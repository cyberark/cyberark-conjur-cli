import unittest

from .util.cli_helpers import cli_arg_test, cli_test

from conjur_api_python3.version import __version__

class CliTest(unittest.TestCase):
    @cli_test()
    def test_cli_without_args_shows_help(self, cli_invocation, output, client):
        self.assertIn("usage: cli", output)

    @cli_test(["-h"])
    def test_cli_shows_help_with_short_help_flag(self, cli_invocation, output, client):
        self.assertIn("usage: cli", output)

    @cli_test(["--help"])
    def test_cli_shows_help_with_long_help_flag(self, cli_invocation, output, client):
        self.assertIn("usage: cli", output)

    @cli_test(["-v"])
    def test_cli_shows_version_with_short_version_flag(self, cli_invocation, output, client):
        self.assertEquals("cli v{}\n".format(__version__), output)

    @cli_test(["--version"])
    def test_cli_shows_version_with_long_version_flag(self, cli_invocation, output, client):
        self.assertEquals("cli v{}\n".format(__version__), output)


    # Optional params

    # Account
    @cli_arg_test(["-a", "myaccount"], account='myaccount')
    def test_cli_passes_account_short_flag_to_client(self): pass

    @cli_arg_test(["--account", "myaccount"], account='myaccount')
    def test_cli_passes_account_long_flag_to_client(self): pass

    # API key
    @cli_arg_test(["-k", "myapikey"], api_key='myapikey')
    def test_cli_passes_api_key_short_flag_to_client(self): pass

    @cli_arg_test(["--api-key", "myapikey"], api_key='myapikey')
    def test_cli_passes_api_key_long_flag_to_client(self): pass

    # CA Bundle
    @cli_arg_test(["-c", "mycabundle"], ca_bundle='mycabundle')
    def test_cli_passes_ca_bundle_short_flag_to_client(self): pass

    @cli_arg_test(["--ca-bundle", "mycabundle"], ca_bundle='mycabundle')
    def test_cli_passes_ca_bundle_long_flag_to_client(self): pass

    # Debug
    @cli_arg_test(["-d"], debug=True)
    def test_cli_passes_debug_short_flag_to_client(self): pass

    @cli_arg_test(["--debug"], debug=True)
    def test_cli_passes_debug_long_flag_to_client(self): pass

    # User
    @cli_arg_test(["-u", "myuser"], login_id='myuser')
    def test_cli_passes_login_id_short_flag_to_client(self): pass

    @cli_arg_test(["--user", "myuser"], login_id='myuser')
    def test_cli_passes_login_id_long_flag_to_client(self): pass

    # Password
    @cli_arg_test(["-p", "mypassword"], password='mypassword')
    def test_cli_passes_password_short_flag_to_client(self): pass

    @cli_arg_test(["--password", "mypassword"], password='mypassword')
    def test_cli_passes_password_long_flag_to_client(self): pass

    # SSL Verify
    @cli_arg_test(["--insecure"], ssl_verify=False)
    def test_cli_passes_insecure_flag_to_client(self): pass

    # URL
    @cli_arg_test(["-l", "myurl"], url='myurl')
    def test_cli_passes_url_short_flag_to_client(self): pass

    @cli_arg_test(["--url", "myurl"], url='myurl')
    def test_cli_passes_url_long_flag_to_client(self): pass

    # Main method invocations

    @cli_test(["variable", "set", "foo", "bar"])
    def test_cli_invokes_variable_set_correctly(self, cli_invocation, output, client):
        client.set.assert_called_once_with('foo', 'bar')

    @cli_test(["variable"])
    def test_cli_variable_parser_doesnt_break_without_action(self, cli_invocation, output, client):
        self.assertIn("usage: cli", output)

    @cli_test(["variable", "get", "foo"])
    def test_cli_invokes_variable_get_correctly(self, cli_invocation, output, client):
        client.get.assert_called_once_with('foo')

    @cli_test(["variable", "get", "foo", "bar"], get_many_output={ "foo": "A", "bar": "B"})
    def test_cli_invokes_variable_get_correctly_with_multiple_vars(self, cli_invocation, output, client):
        client.get_many.assert_called_once_with('foo', 'bar')

    @cli_test(["variable", "get", "foo", "bar"], get_many_output={ "foo": "A", "bar": "B"})
    def test_cli_variable_get_with_multiple_vars_outputs_formatted_json(self, cli_invocation, output, client):
        self.assertEquals('{\n    "foo": "A",\n    "bar": "B"\n}\n', output)

    @cli_test(["policy"])
    def test_cli_policy_parser_doesnt_break_without_action(self, cli_invocation, output, client):
        self.assertIn("usage: cli", output)

    @cli_test(["policy", "apply", "foo", "foopolicy"])
    def test_cli_invokes_policy_apply_correctly(self, cli_invocation, output, client):
        client.apply_policy_file.assert_called_once_with('foo', 'foopolicy')

    @cli_test(["policy", "replace", "foo", "foopolicy"])
    def test_cli_invokes_policy_replace_correctly(self, cli_invocation, output, client):
        client.replace_policy_file.assert_called_once_with('foo', 'foopolicy')
