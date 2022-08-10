import tempfile

import unittest
from unittest.mock import patch, MagicMock
import time

from conjur_api import Client
from conjur_api.models import SslVerificationMetadata, SslVerificationMode
from conjur.controller import InitController
from conjur.controller.host_controller import HostController
from conjur.controller.hostfactory_controller import HostFactoryController
from conjur.controller.login_controller import LoginController
from conjur.controller.logout_controller import LogoutController
from conjur.controller.user_controller import UserController
from conjur.errors import MissingRequiredParameterException
from conjur.logic.credential_provider import FileCredentialsProvider
from test.util.test_infrastructure import cli_test, cli_arg_test
from conjur.version import __version__
from conjur.cli import Cli
from conjur import cli_actions
from conjur.data_object.conjurrc_data import ConjurrcData
from conjur.constants import DEFAULT_CONFIG_FILE

RESOURCE_LIST = [
    'some_id1',
    'some_id2',
]
WHOAMI_RESPONSE = {
    "conjur_account": "myaccount"
}

MockConjurrc = ConjurrcData(conjur_url='https://someurl', account='someacc', cert_file='some/path/to/pem')

class MockArgs(object):
    pass


class CliTest(unittest.TestCase):

    def __init__(self, testname):
        ConjurrcData("https://someurl", "someacc", 'some/path/to/pem').write_to_file(DEFAULT_CONFIG_FILE)
        super(CliTest, self).__init__(testname)

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

Copyright (c) {time.strftime("%Y")} CyberArk Software Ltd. All rights reserved.
<www.cyberark.com>
''', str(output))

    @cli_test(["--version"])
    def test_cli_check_copyright_long_version_flag(self, cli_invocation, output, client):
        self.assertIn(f'''Conjur CLI version {format(__version__)}

Copyright (c) {time.strftime("%Y")} CyberArk Software Ltd. All rights reserved.
<www.cyberark.com>
''', str(output))

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
    def test_cli_invokes_variable_get_correctly_with_multiple_vars(
            self, cli_invocation, output,
            client):
        client.get_many.assert_called_once_with('foo', 'bar')

    @cli_test(["variable", "get", "-i", "foo", "bar"], get_many_output={})
    def test_cli_variable_get_with_multiple_vars_doesnt_break_on_empty_input(
            self, cli_invocation,
            output, client):
        self.assertEquals('{}\n', output)

    @cli_test(["variable", "get", "-i", "foo", "bar"], get_many_output={"foo": "A", "bar": "B"})
    def test_cli_variable_get_with_multiple_vars_outputs_formatted_json(
            self, cli_invocation,
            output, client):
        self.assertEquals('{\n    "foo": "A",\n    "bar": "B"\n}\n', output)

    @cli_test(["role", "exists", "-i", "somekind:/path/to/role"])
    def test_cli_invokes_role_exists_correctly(self, cli_invocation, output, client):
        client.role_exists.assert_called_once_with('somekind', '/path/to/role')

    @cli_test(["role", "memberships", "-i", "somekind:/path/to/role", "-d"], memberships_output=['abc', 'def'])
    def test_cli_invokes_role_memberships_correctly(self, cli_invocation, output, client):
        client.role_memberships.assert_called_once_with('somekind', '/path/to/role', True)

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

    @cli_test(["policy", "load", "-b", "foo", "-f", "foopolicy"],
              policy_change_output={"foo": "A", "bar": "B"})
    def test_cli_policy_load_outputs_formatted_json(self, cli_invocation, output, client):
        self.assertEquals('{\n    "foo": "A",\n    "bar": "B"\n}\n', output)

    @cli_test(["policy", "replace", "-b", "foo", "-f", "foopolicy"])
    def test_cli_invokes_policy_replace_correctly(self, cli_invocation, output, client):
        client.replace_policy_file.assert_called_once_with('foo', 'foopolicy')

    @cli_test(["policy", "replace", "-b", "foo", "-f", "foopolicy"], policy_change_output={})
    def test_cli_policy_replace_doesnt_break_on_empty_input(self, cli_invocation, output, client):
        self.assertEquals('{}\n', output)

    @cli_test(["policy", "replace", "-b", "foo", "-f", "foopolicy"],
              policy_change_output={"foo": "A", "bar": "B"})
    def test_cli_policy_replace_outputs_formatted_json(self, cli_invocation, output, client):
        self.assertEquals('{\n    "foo": "A",\n    "bar": "B"\n}\n', output)

    @cli_test(["policy", "update", "-b", "foo", "-f", "foopolicy"])
    def test_cli_invokes_policy_update_correctly(self, cli_invocation, output, client):
        client.update_policy_file.assert_called_once_with('foo', 'foopolicy')

    @cli_test(["policy", "update", "-b", "foo", "-f", "foopolicy"], policy_change_output={})
    def test_cli_policy_update_doesnt_break_on_empty_input(self, cli_invocation, output, client):
        self.assertEquals('{}\n', output)

    @cli_test(["policy", "update", "-b", "foo", "-f", "foopolicy"],
              policy_change_output={"foo": "A", "bar": "B"})
    def test_cli_policy_update_outputs_formatted_json(self, cli_invocation, output, client):
        self.assertEquals('{\n    "foo": "A",\n    "bar": "B"\n}\n', output)

    @cli_test(["list"], list_output=RESOURCE_LIST)
    def test_cli_invokes_resource_listing_correctly(self, cli_invocation, output, client):
        client.list.assert_called_once_with({})

    @cli_test(["list"], list_output=RESOURCE_LIST)
    def test_cli_resource_listing_outputs_formatted_json(self, cli_invocation, output, client):
        self.assertEquals('[\n    "some_id1",\n    "some_id2"\n]\n', output)

    @cli_test(["show", "-i", "kind:/path/to/var"])
    def test_cli_invokes_show_correctly(self, cli_invocation, output, client):
        client.get_resource.assert_called_once_with('kind', '/path/to/var')

    @cli_test(["show", "-i", "kind:/path/to/var"], show_output={"foo": "A", "bar": "B"})
    def test_cli_show_outputs_formatted_json(self, cli_invocation, output, client):
        self.assertEquals('{\n    "foo": "A",\n    "bar": "B"\n}\n', output)

    @cli_test(["resource", "exists", "-i", "kind:/path/to/var"])
    def test_cli_invokes_resource_exists_correctly(self, cli_invocation, output, client):
        client.resource_exists.assert_called_once_with('kind', '/path/to/var')

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
    def test_cli_user_rotate_api_key_short_help_returns_rotate_api_key_help(
            self, cli_invocation,
            output, client):
        self.assertIn("Name:\n  rotate-api-key", output)

    @cli_test(["user", "rotate-api-key", "--help"])
    def test_cli_user_rotate_api_key_long_help_returns_rotate_api_key_help(
            self, cli_invocation,
            output, client):
        self.assertIn("Name:\n  rotate-api-key", output)

    @cli_test(["user", "change-password", "-h"])
    def test_cli_user_change_password_short_help_returns_change_password_help(
            self, cli_invocation,
            output, client):
        self.assertIn("Name:\n  change-password", output)

    @cli_test(["user", "change-password", "--help"])
    def test_cli_user_change_password_long_help_returns_change_password_help(
            self, cli_invocation,
            output, client):
        self.assertIn("Name:\n  change-password", output)

    @cli_test(["host", "-h"])
    def test_cli_host_short_help_returns_host_help(self, cli_invocation, output, client):
        self.assertIn("Name:\n  host", output)

    @cli_test(["host", "--help"])
    def test_cli_host_long_help_returns_host_help(self, cli_invocation, output, client):
        self.assertIn("Name:\n  host", output)

    @cli_test(["host", "rotate-api-key", "-h"])
    def test_cli_host_rotate_api_key_short_help_returns_rotate_api_key_help(
            self, cli_invocation,
            output, client):
        self.assertIn("Name:\n  rotate-api-key", output)

    @cli_test(["host", "rotate-api-key", "--help"])
    def test_cli_host_rotate_api_key_long_help_returns_rotate_api_key_help(
            self, cli_invocation,
            output, client):
        self.assertIn("Name:\n  rotate-api-key", output)

    @cli_test(["whoami"], whoami_output=WHOAMI_RESPONSE)
    def test_cli_invokes_whoami_correctly(self, cli_invocation, output, client):
        client.whoami.assert_called_once_with()

    @cli_test(["whoami"], whoami_output=WHOAMI_RESPONSE)
    def test_cli_invokes_whoami_outputs_formatted_json(self, cli_invocation, output, client):
        self.assertEquals('{\n    "conjur_account": "myaccount"\n}\n', output)

    @patch('conjur.cli_actions.handle_init_logic')
    def test_cli_init_functions_are_properly_called(self, mock_init):
        cli_actions.handle_init_logic(url="https://someurl", account="somename",
                                      cert="/path/to/pem", force=False)
        mock_init.assert_called_once()

    @patch.object(InitController, 'load')
    def test_cli_init_load_function_is_properly_called(self, mock_load):
        with tempfile.NamedTemporaryFile() as t:
            file_path = f"{t.name}"
            cli_actions.handle_init_logic(url="https://someurl", account="somename",
                                          cert=file_path, force=False, ssl_verify=True)
            mock_load.assert_called_once()

    @patch.object(InitController, 'load')
    def test_cli_init_fails_with_authn_ldap_without_service_id(self, mock_load):
        with self.assertRaises(MissingRequiredParameterException) as context:
            cli_actions.handle_init_logic(url="https://someurl", account="somename", authn_type="ldap")

        mock_load.assert_not_called()
        self.assertRegex(context.exception.message, "service-id is required")

    @patch.object(InitController, 'load')
    def test_cli_init_succeeds_with_authn_without_service_id(self, mock_load):
        cli_actions.handle_init_logic(url="https://someurl", account="somename",
                                      authn_type="authn")
        mock_load.assert_called_once()

    @patch.object(ConjurrcData, '__init__', return_value=None)
    @patch.object(InitController, 'load')
    def test_cli_init_defaults_to_ldap_with_service_id(self, mock_load, mock_conjurrc_init):
        cli_actions.handle_init_logic(url="https://someurl", account="somename",
                                      service_id="some-service-id")
        mock_conjurrc_init.assert_called_once_with(
            conjur_url="https://someurl",
            account="somename",
            cert_file=None,
            authn_type="ldap",
            service_id="some-service-id",
            netrc_path=None,
        )
        mock_load.assert_called_once()

    @patch.object(LoginController, 'load')
    def test_cli_login_functions_are_properly_called(self, mock_load):
        cli_actions.handle_login_logic(credential_provider=FileCredentialsProvider,
                                       identifier='someidentifier', password='somepassword',
                                       ssl_verify=True)
        mock_load.assert_called_once()

    @patch.object(LogoutController, 'remove_credentials')
    def test_cli_logout_functions_are_properly_called(self, mock_remove_creds):
        cli_actions.handle_logout_logic(credential_provider=FileCredentialsProvider)
        mock_remove_creds.assert_called_once()

    @patch.object(UserController, 'rotate_api_key')
    def test_cli_user_rotate_api_key_functions_are_properly_called(self, mock_rotate_api_key):
        mock_obj = MockArgs()
        mock_obj.action = 'rotate-api-key'
        mock_obj.id = 'someid'

        cli_actions.handle_user_logic(credential_provider=FileCredentialsProvider(), args=mock_obj,
                                      client='someclient')
        mock_rotate_api_key.assert_called_once()

    @patch.object(UserController, 'change_personal_password')
    def test_cli_user_change_password_functions_are_properly_called(self, mock_change_password):
        mock_obj = MockArgs()
        mock_obj.action = 'change-password'
        mock_obj.password = 'somepass'

        cli_actions.handle_user_logic(credential_provider=FileCredentialsProvider, args=mock_obj,
                                      client='someclient')
        mock_change_password.assert_called_once()

    @patch.object(HostController, 'rotate_api_key')
    def test_cli_host_logic_functions_are_properly_called(self, mock_rotate_api_key):
        mock_obj = MockArgs()
        mock_obj.action = 'someaction'
        mock_obj.id = 'someid'

        cli_actions.handle_host_logic(args=mock_obj, client='someclient')
        mock_rotate_api_key.assert_called_once()

    @patch('conjur.cli_actions.handle_init_logic')
    def test_run_action_runs_init_logic(self, mock_handle_init):
        mock_obj = MockArgs()
        mock_obj.url = 'https://someurl'
        mock_obj.ssl_verify = True
        mock_obj.name = 'somename'
        mock_obj.certificate = 'somecert'
        mock_obj.force = 'force'
        mock_obj.debug = 'somedebug'
        mock_obj.is_self_signed = False
        mock_obj.authn_type = 'authn'
        mock_obj.service_id = 'service_id'
        mock_obj.force_netrc = None

        Cli().run_action('init', mock_obj)
        mock_handle_init.assert_called_once_with('https://someurl', 'somename', 'authn', 'service_id',
                                                 'somecert', 'force', True, False, None)

    '''
    Verifies that if a user didn't run init, they are prompted to do so and that after they 
    initialize,
    a command will be run to completion. In this case, variable.
    '''

    @patch.object(FileCredentialsProvider, 'is_exists', side_effect=[True, False])
    @patch('conjur.cli_actions.handle_init_logic')
    @patch('conjur.cli_actions.handle_variable_logic')
    @patch('os.path.exists', side_effect=[False, False, True])
    @patch('os.getenv', return_value=None)
    @patch('os.path.getsize', side_effect=[1, 1])
    @patch('conjur.data_object.conjurrc_data.ConjurrcData.load_from_file',
           return_value=MockConjurrc)
    @patch('keyring.get_keyring')
    def test_run_action_runs_init_if_conjurrc_not_found(
            self, mock_keyring, mock_conjurrc,
            mock_size, mock_getenv, mock_path_exists,
            mock_variable_init, mock_handle_init,
            mock_exists):
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

    @patch.object(FileCredentialsProvider, 'is_exists', return_value=False)
    @patch('conjur.cli_actions.handle_login_logic')
    @patch('conjur.cli_actions.handle_variable_logic')
    @patch('os.path.exists', side_effect=[True, True, False])
    @patch('os.getenv', return_value=None)
    @patch('os.path.getsize', side_effect=[1, 0])
    @patch('conjur.data_object.conjurrc_data.ConjurrcData.load_from_file',
           return_value=MockConjurrc)
    @patch('keyring.get_keyring')
    def test_run_action_runs_login_if_netrc_not_found(
            self, mock_keyring, mock_conjurrc, mock_size,
            mock_getenv, mock_path_exists,
            mock_variable_init, mock_handle_login, mock_is_exists):
        with patch('conjur.cli.Client') as mock_client:
            mock_keyring.name.return_value = 'somekeyring'
            mock_client.return_value = MagicMock()
            mock_obj = MockArgs()
            mock_obj.ssl_verify = False
            mock_obj.debug = 'somedebug'

            Cli().run_action('variable', mock_obj)
            mock_handle_login.assert_called_once()

    @patch.object(FileCredentialsProvider, 'is_exists', side_effect=[True, False])
    @patch('conjur.cli_actions.handle_user_logic')
    @patch('os.path.exists', side_effect=[True, True])
    @patch('os.getenv', return_value=None)
    @patch('os.path.getsize', return_value=1)
    @patch('conjur.data_object.conjurrc_data.ConjurrcData.load_from_file',
           return_value=MockConjurrc)
    @patch('keyring.get_keyring')
    def test_run_action_runs_user_logic(
            self, mock_keyring, mock_conjurrc, mock_size, mock_getenv,
            mock_path_exists, mock_handle_user, mock_is_exists):
        with patch('conjur.cli.Client') as mock_client:
            mock_client.return_value = MagicMock()
            mock_obj = MockArgs()
            mock_obj.ssl_verify = False
            mock_obj.debug = 'somedebug'

            Cli().run_action('user', mock_obj)
            mock_handle_user.assert_called_once()

    @patch.object(FileCredentialsProvider, 'is_exists', side_effect=[True, False])
    @patch('conjur.cli_actions.handle_host_logic')
    @patch('os.path.exists', side_effect=[True, True])
    @patch('os.getenv', return_value=None)
    @patch('os.path.getsize', return_value=1)
    @patch('keyring.get_keyring')
    @patch('conjur.data_object.conjurrc_data.ConjurrcData.load_from_file',
           return_value=MockConjurrc)
    def test_run_action_runs_host_logic(
            self, mock_keyring, mock_conjurrc, mock_size, mock_getenv,
            mock_path_exists, mock_handle_host, mock_is_exists):
        with patch('conjur.cli.Client') as mock_client:
            mock_keyring.name.return_value = 'somekeyring'
            mock_client.return_value = MagicMock()
            mock_obj = MockArgs()
            mock_obj.ssl_verify = False
            mock_obj.debug = 'somedebug'

            Cli().run_action('host', mock_obj)
            mock_handle_host.assert_called_once()

    @patch.object(HostFactoryController, 'create_token')
    def test_cli_hostfactory_token_create_functions_are_properly_called(
            self,
            mock_hostfactory_create_token):
        mock_obj = MockArgs()
        mock_obj.action_type = 'create_token'
        mock_obj.hostfactoryid = "some-id"
        mock_obj.duration_days = 1
        mock_obj.duration_hours = 1
        mock_obj.duration_minutes = 1
        mock_obj.cidr = '[]'
        mock_obj.count = 1

        cli_actions.handle_hostfactory_logic(args=mock_obj, client='someclient')
        mock_hostfactory_create_token.assert_called_once()
