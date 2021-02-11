import unittest
from unittest.mock import patch, MagicMock

from conjur import Client
from conjur.controller.host_controller import HostController
from conjur.controller.login_controller import LoginController
from conjur.controller.logout_controller import LogoutController
from conjur.controller.user_controller import UserController
from test.util.test_infrastructure import cli_test, cli_arg_test
from conjur.version import __version__
from conjur.cli import Cli

RESOURCE_LIST = [
    'some_id1',
    'some_id2',
]
WHOAMI_RESPONSE = {
    "account": "myaccount"
}

class MockArgs(object):
    pass

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

Copyright (c) 2021 CyberArk Software Ltd. All rights reserved.
<www.cyberark.com>
''', str(output))

    @cli_test(["--version"])
    def test_cli_check_copyright_long_version_flag(self, cli_invocation, output, client):
        self.assertIn(f'''Conjur CLI version {format(__version__)}

Copyright (c) 2021 CyberArk Software Ltd. All rights reserved.
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

    @cli_test(["policy", "--help"])
    def test_cli_policy_long_help_returns_help(self, cli_invocation, output, client):
        self.assertIn("Name:\n  policy", output)

    @cli_test(["policy", "-h"])
    def test_cli_policy_short_help_returns_help(self, cli_invocation, output, client):
        self.assertIn("Name:\n  policy", output)

    @cli_test(["policy", "load", "--help"])
    def test_cli_policy_load_long_help_returns_help(self, cli_invocation, output, client):
        self.assertIn("Name:\n  load", output)

    @cli_test(["policy", "load", "-h"])
    def test_cli_policy_load_short_help_returns_help(self, cli_invocation, output, client):
        self.assertIn("Name:\n  load", output)

    @cli_test(["policy", "replace", "-h"])
    def test_cli_policy_replace_short_returns_help(self, cli_invocation, output, client):
        self.assertIn("Name:\n  replace", output)

    @cli_test(["policy", "replace", "--help"])
    def test_cli_policy_replace_long_returns_help(self, cli_invocation, output, client):
        self.assertIn("Name:\n  replace", output)

    @cli_test(["policy", "update", "-h"])
    def test_cli_policy_update_short_returns_help(self, cli_invocation, output, client):
        self.assertIn("Name:\n  update", output)

    @cli_test(["policy", "update", "--help"])
    def test_cli_policy_update_long_returns_help(self, cli_invocation, output, client):
        self.assertIn("Name:\n  update", output)

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

    @cli_test(["user"])
    def test_cli_user_retuns_main_help(self, cli_invocation, output, client):
        self.assertIn("Usage:\n", output)

    @cli_test(["user", "-h"])
    def test_cli_user_short_help_returns_user_help(self, cli_invocation, output, client):
        self.assertIn("Name:\n  user", output)

    @cli_test(["user", "--help"])
    def test_cli_user_long_help_returns_user_help(self, cli_invocation, output, client):
        self.assertIn("Name:\n  user", output)

    @cli_test(["user", "rotate-api-key", "-h"])
    def test_cli_user_rotate_api_key_short_help_returns_rotate_api_key_help(self, cli_invocation, output, client):
        self.assertIn("Name:\n  rotate-api-key", output)

    @cli_test(["user",  "rotate-api-key", "--help"])
    def test_cli_user_rotate_api_key_long_help_returns_rotate_api_key_help(self, cli_invocation, output, client):
        self.assertIn("Name:\n  rotate-api-key", output)

    @cli_test(["user", "change-password", "-h"])
    def test_cli_user_change_password_short_help_returns_change_password_help(self, cli_invocation, output, client):
        self.assertIn("Name:\n  change-password", output)

    @cli_test(["user", "change-password", "--help"])
    def test_cli_user_change_password_long_help_returns_change_password_help(self, cli_invocation, output, client):
        self.assertIn("Name:\n  change-password", output)

    @cli_test(["host", "-h"])
    def test_cli_host_short_help_returns_host_help(self, cli_invocation, output, client):
        self.assertIn("Name:\n  host", output)

    @cli_test(["host", "--help"])
    def test_cli_host_long_help_returns_host_help(self, cli_invocation, output, client):
        self.assertIn("Name:\n  host", output)

    @cli_test(["host", "rotate-api-key", "-h"])
    def test_cli_host_rotate_api_key_short_help_returns_rotate_api_key_help(self, cli_invocation, output, client):
        self.assertIn("Name:\n  rotate-api-key", output)

    @cli_test(["host",  "rotate-api-key", "--help"])
    def test_cli_host_rotate_api_key_long_help_returns_rotate_api_key_help(self, cli_invocation, output, client):
        self.assertIn("Name:\n  rotate-api-key", output)

    @cli_test(["whoami"], whoami_output=WHOAMI_RESPONSE)
    def test_cli_invokes_whoami_correctly(self, cli_invocation, output, client):
        client.whoami.assert_called_once_with()

    @cli_test(["whoami"], whoami_output=WHOAMI_RESPONSE)
    def test_cli_invokes_whoami_outputs_formatted_json(self, cli_invocation, output, client):
        self.assertEquals('{\n    "account": "myaccount"\n}\n', output)

    @patch.object(LoginController, 'load')
    def test_cli_login_functions_are_properly_called(self, mock_load):
        Cli().handle_login_logic(identifier='someidentifier', password='somepassword', ssl_verify=True)
        mock_load.assert_called_once()

    @patch.object(Client, 'initialize')
    def test_cli_init_functions_are_properly_called(self, mock_init):
        Cli().handle_init_logic(url="https://someurl", name="somename", certificate="/path/to/pem", force=False)
        mock_init.assert_called_once()

    @patch.object(LogoutController, 'remove_credentials')
    def test_cli_logout_functions_are_properly_called(self, mock_remove_creds):
        Cli().handle_logout_logic(ssl_verify=True)
        mock_remove_creds.assert_called_once()

    @patch.object(UserController, 'rotate_api_key')
    def test_cli_user_rotate_api_key_functions_are_properly_called(self, mock_rotate_api_key):
        mock_obj = MockArgs()
        mock_obj.action = 'rotate-api-key'
        mock_obj.id = 'someid'

        Cli().handle_user_logic(args=mock_obj, client='someclient')
        mock_rotate_api_key.assert_called_once()

    @patch.object(UserController, 'change_personal_password')
    def test_cli_user_change_password_functions_are_properly_called(self, mock_change_password):
        mock_obj = MockArgs()
        mock_obj.action = 'change-password'
        mock_obj.password = 'somepass'

        Cli().handle_user_logic(args=mock_obj, client='someclient')
        mock_change_password.assert_called_once()

    @patch.object(HostController, 'rotate_api_key')
    def test_cli_host_logic_functions_are_properly_called(self, mock_rotate_api_key):
        mock_obj = MockArgs()
        mock_obj.action = 'someaction'
        mock_obj.id = 'someid'

        Cli().handle_host_logic(args=mock_obj, client='someclient')
        mock_rotate_api_key.assert_called_once()

    @patch.object(Cli, 'handle_init_logic')
    @patch.object(Client, 'setup_logging')
    def test_run_action_runs_init_logic(self, mock_setup_logging, mock_handle_init):
        mock_obj = MockArgs()
        mock_obj.url = 'https://someurl'
        mock_obj.name = 'somename'
        mock_obj.certificate = 'somecert'
        mock_obj.force = 'force'
        mock_obj.debug = 'somedebug'

        Cli().run_action('init', mock_obj)
        mock_handle_init.assert_called_once_with('https://someurl', 'somename', 'somecert', 'force')

    @patch.object(Cli, 'handle_login_logic')
    @patch.object(Client, 'setup_logging')
    def test_run_action_runs_login_logic(self, mock_setup_logging, mock_handle_login):
        mock_obj = MockArgs()
        mock_obj.identifier = 'someidentifier'
        mock_obj.password = 'somepassword'
        mock_obj.ssl_verify = False
        mock_obj.debug = 'somedebug'

        Cli().run_action('login', mock_obj)
        mock_handle_login.assert_called_once_with('someidentifier', 'somepassword', False)

    @patch.object(Cli, 'handle_logout_logic')
    @patch.object(Client, 'setup_logging')
    def test_run_action_runs_logout_logic(self, mock_setup_logging, mock_handle_logout):
        mock_obj = MockArgs()
        mock_obj.ssl_verify = False
        mock_obj.debug = 'somedebug'

        Cli().run_action('logout', mock_obj)
        mock_handle_logout.assert_called_once_with(False)

    '''
    Verifies that if a user didn't run init, they are prompted to do so and that after they initialize,
    a command will be run to completion. In this case, variable.
    '''
    @patch.object(Cli, 'handle_init_logic')
    @patch.object(Cli, 'handle_variable_logic')
    @patch('os.path.exists', side_effect=[False, True])
    @patch('os.getenv', return_value=None)
    @patch('os.path.getsize', side_effect=[1, 1])
    def test_run_action_runs_init_if_conjurrc_not_found(self, mock_size, mock_getenv, mock_path_exists, mock_variable_init, mock_handle_init):
        with patch('conjur.cli.Client') as mock_client:
            mock_client.return_value = MagicMock()
            mock_obj = MockArgs()
            mock_obj.ssl_verify = False
            mock_obj.debug = 'somedebug'

            Cli().run_action('variable', mock_obj)
            mock_handle_init.assert_called_once()

    '''
    Verifies that if a user didn't run login, they are prompted to do so and that after they login,
    a command will be run to completion. In this case, variable.
    '''
    @patch.object(Cli, 'handle_login_logic')
    @patch.object(Cli, 'handle_variable_logic')
    @patch('os.path.exists', side_effect=[True, False])
    @patch('os.getenv', return_value=None)
    @patch('os.path.getsize', side_effect=[1, 0])
    def test_run_action_runs_login_if_netrc_not_found(self, mock_size, mock_getenv, mock_path_exists, mock_variable_init, mock_handle_login):
        with patch('conjur.cli.Client') as mock_client:
            mock_client.return_value = MagicMock()
            mock_obj = MockArgs()
            mock_obj.ssl_verify = False
            mock_obj.debug = 'somedebug'

            Cli().run_action('variable', mock_obj)
            mock_handle_login.assert_called_once()

    @patch.object(Cli, 'handle_user_logic')
    @patch('os.path.exists', side_effect=[True, True])
    @patch('os.getenv', return_value=None)
    @patch('os.path.getsize', return_value=1)
    def test_run_action_runs_user_logic(self, mock_size, mock_getenv, mock_path_exists, mock_handle_user):
        with patch('conjur.cli.Client') as mock_client:
            mock_client.return_value = MagicMock()
            mock_obj = MockArgs()
            mock_obj.ssl_verify = False
            mock_obj.debug = 'somedebug'

            Cli().run_action('user', mock_obj)
            mock_handle_user.assert_called_once()

    @patch.object(Cli, 'handle_host_logic')
    @patch('os.path.exists', side_effect=[True, True])
    @patch('os.getenv', return_value=None)
    @patch('os.path.getsize', return_value=1)
    def test_run_action_runs_host_logic(self, mock_size, mock_getenv, mock_path_exists, mock_handle_host):
        with patch('conjur.cli.Client') as mock_client:
            mock_client.return_value = MagicMock()
            mock_obj = MockArgs()
            mock_obj.ssl_verify = False
            mock_obj.debug = 'somedebug'

            Cli().run_action('host', mock_obj)
            mock_handle_host.assert_called_once()


