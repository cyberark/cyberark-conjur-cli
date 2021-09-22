# -*- coding: utf-8 -*-

"""
CLI module

This module is the main entrypoint for all CLI-like usages of this
module where only the minimal invocation configuration is required.
"""

# Builtins
import json
import logging
import os
import sys
import traceback

# Third party
import requests

# Internals
from conjur.api import SSLClient
from conjur.argument_parser.argparse_builder import ArgParseBuilder
from conjur.interface.credentials_store_interface import CredentialsStoreInterface
from conjur.logic.credential_provider.credential_store_factory import CredentialStoreFactory
from conjur.errors import CertificateVerificationException
from conjur.errors_messages import INCONSISTENT_VERIFY_MODE_MESSAGE
from conjur.util.util_functions import determine_status_code_specific_error_messages, \
    file_is_missing_or_empty
from conjur.wrapper import ArgparseWrapper
from conjur.api.client import Client
from conjur.constants import DEFAULT_CONFIG_FILE, LOGIN_IS_REQUIRED
from conjur.controller import HostController, ListController, LogoutController, InitController
from conjur.controller import LoginController, PolicyController, UserController, VariableController
from conjur.logic import ListLogic, LoginLogic, LogoutLogic, PolicyLogic, UserLogic, \
    VariableLogic, InitLogic
from conjur.data_object import ConjurrcData, CredentialsData, HostResourceData, ListData
from conjur.data_object import PolicyData, UserInputData, VariableData
from conjur.version import __version__

# pylint: disable=too-many-statements
class Cli():
    """
    Main wrapper around CLI-like usages of this module. Provides various
    helpers around parsing of parameters and running client commands.
    """

    LOGGING_FORMAT = '%(asctime)s %(levelname)s: %(message)s'


        # pylint: disable=no-self-use, too-many-locals
    def run(self, *args):
        """
        Main entrypoint for the class invocation from both CLI, Package, and
        test sources. Parses CLI args and invokes the appropriate client command.
        """

        # The following block of code implements the fluent interface technique
        # https://en.wikipedia.org/wiki/Fluent_interface
        parser = ArgParseBuilder() \
            .add_login_parser() \
            .add_init_parser() \
            .add_logout_parser() \
            .add_list_parser() \
            .add_host_parser() \
            .add_policy_parser() \
            .add_user_parser() \
            .add_variable_parser() \
            .add_whoami_parser() \
            .add_hostfactory_parser() \
            .add_main_screen_options() \
            .build()

        resource, args = Cli._parse_args(parser)
        # pylint: disable=broad-except
        try:
            Cli.run_action(resource, args)
        except KeyboardInterrupt:
            # A new line required so when the CLI is packaged as an exec,
            # it won't erase the previous line
            sys.stdout.write("\n")
            sys.exit(0)
        except FileNotFoundError as not_found_error:
            logging.debug(traceback.format_exc())
            sys.stdout.write(f"Error: No such file or directory: '{not_found_error.filename}'\n")
            sys.exit(1)
        except requests.exceptions.HTTPError as server_error:
            logging.debug(traceback.format_exc())
            # pylint: disable=no-member
            if hasattr(server_error.response, 'status_code'):
                sys.stdout.write(determine_status_code_specific_error_messages(server_error))
            else:
                sys.stdout.write(f"Failed to execute command. Reason: {server_error}\n")

            if args.debug is False:
                sys.stdout.write("Run the command again in debug mode for more information.\n")
            sys.exit(1)
        except CertificateVerificationException:
            logging.debug(traceback.format_exc())
            sys.stdout.write(f"Failed to execute command. Reason: "
                             f"{INCONSISTENT_VERIFY_MODE_MESSAGE}\n")
            if args.debug is False:
                sys.stdout.write("Run the command again in debug mode for more information.\n")
            sys.exit(1)
        except Exception as error:
            logging.debug(traceback.format_exc())
            sys.stdout.write(f"Failed to execute command. Reason: {str(error)}\n")
            if args.debug is False:
                sys.stdout.write("Run the command again in debug mode for more information.\n")
            sys.exit(1)
        else:
            # Explicit exit (required for tests)
            sys.exit(0)

    @classmethod
    # pylint: disable=too-many-arguments
    def handle_init_logic(cls, url:str=None, account:str=None, cert:str=None, force:bool=None,
            ssl_verify:bool=True):
        """
        Method that wraps the init call logic
        Initializes the client, creating the .conjurrc file
        """
        ssl_service = SSLClient()
        conjurrc_data = ConjurrcData(conjur_url=url,
                                     account=account,
                                     cert_file=cert)

        init_logic = InitLogic(ssl_service)
        input_controller = InitController(conjurrc_data=conjurrc_data,
                                          init_logic=init_logic,
                                          force=force,
                                          ssl_verify=ssl_verify)
        input_controller.load()

    @classmethod
    # pylint: disable=line-too-long
    def handle_login_logic(cls, credential_provider:CredentialsStoreInterface, identifier:str=None, password:str=None, ssl_verify:bool=True):
        """
        Method that wraps the login call logic
        """
        credential_data = CredentialsData(login=identifier)
        login_logic = LoginLogic(credential_provider)
        login_controller = LoginController(ssl_verify=ssl_verify,
                                           user_password=password,
                                           credential_data=credential_data,
                                           login_logic=login_logic)
        login_controller.load()

        sys.stdout.write("Successfully logged in to Conjur\n")

    @classmethod
    def handle_logout_logic(cls, credential_provider:CredentialsStoreInterface,
                            ssl_verify:bool=True):
        """
        Method that wraps the logout call logic
        """
        logout_logic = LogoutLogic(credential_provider)
        logout_controller = LogoutController(ssl_verify=ssl_verify,
                                             logout_logic=logout_logic,
                                             credentials_provider=credential_provider)
        logout_controller.remove_credentials()

    @classmethod
    def handle_list_logic(cls, list_data:ListData=None, client=None):
        """
        Method that wraps the list call logic
        """
        list_logic = ListLogic(client)
        list_controller = ListController(list_logic=list_logic,
                                         list_data=list_data)
        list_controller.load()

    @classmethod
    def handle_variable_logic(cls, args:list=None, client=None):
        """
        Method that wraps the variable call logic
        """
        variable_logic = VariableLogic(client)
        if args.action == 'get':
            variable_data = VariableData(action=args.action, id=args.identifier, value=None,
                                         variable_version=args.version)
            variable_controller = VariableController(variable_logic=variable_logic,
                                                     variable_data=variable_data)
            variable_controller.get_variable()
        elif args.action == 'set':
            variable_data = VariableData(action=args.action, id=args.identifier, value=args.value,
                                         variable_version=None)
            variable_controller = VariableController(variable_logic=variable_logic,
                                                     variable_data=variable_data)
            variable_controller.set_variable()

    @classmethod
    def handle_policy_logic(cls, policy_data:PolicyData=None, client=None):
        """
        Method that wraps the variable call logic
        """
        policy_logic = PolicyLogic(client)
        policy_controller = PolicyController(policy_logic=policy_logic,
                                             policy_data=policy_data)
        policy_controller.load()

    @classmethod
    def handle_user_logic(cls, credential_provider:CredentialsStoreInterface,
                          args=None, client=None):
        """
        Method that wraps the user call logic
        """
        user_logic = UserLogic(ConjurrcData, credential_provider, client)
        if args.action == 'rotate-api-key':
            user_input_data = UserInputData(action=args.action,
                                            id=args.id,
                                            new_password=None)

            user_controller = UserController(user_logic=user_logic,
                                             user_input_data=user_input_data)
            user_controller.rotate_api_key()
        elif args.action == 'change-password':
            user_input_data = UserInputData(action=args.action,
                                            id=None,
                                            new_password=args.password)
            user_controller = UserController(user_logic=user_logic,
                                             user_input_data=user_input_data)
            user_controller.change_personal_password()

    @classmethod
    def handle_host_logic(cls, args, client):
        """
        Method that wraps the host call logic
        """
        host_resource_data = HostResourceData(action=args.action, host_to_update=args.id)
        host_controller = HostController(client=client, host_resource_data=host_resource_data)
        host_controller.rotate_api_key()

    @staticmethod
    # pylint: disable=too-many-branches,logging-fstring-interpolation
    def run_action(resource:str, args):
        """
        Helper for creating the Client instance and invoking the appropriate
        api class method with the specified parameters.
        """
        Client.setup_logging(Client, args.debug)

        credential_provider, _ = CredentialStoreFactory.create_credential_store()
        # pylint: disable=no-else-return,line-too-long
        if resource == 'logout':
            Cli.handle_logout_logic(credential_provider, args.ssl_verify)
            sys.stdout.write("Successfully logged out from Conjur\n")
            return

        if resource == 'init':
            Cli.handle_init_logic(args.url, args.name, args.certificate, args.force, args.ssl_verify)
            # A successful exit is required to prevent the initialization of
            # the Client because the init command does not require the Client
            # The below message when a user explicitly requested to init
            sys.stdout.write("To start using the Conjur CLI, log in to the Conjur server by "
                             "running `conjur login`\n")
            return

        # Needed for unit tests so that they do not require configuring
        is_testing_env = os.getenv('TEST_ENV') in ('true', 'True')

        # If the user runs a command without configuring the CLI,
        # we request they do so before executing their request
        # pylint: disable=line-too-long
        if not is_testing_env and file_is_missing_or_empty(DEFAULT_CONFIG_FILE):
            sys.stdout.write("The Conjur CLI needs to be initialized before you can use it\n")
            Cli.handle_init_logic()

        if resource == 'login':
            Cli.handle_login_logic(credential_provider, args.identifier, args.password, args.ssl_verify)
            return

        # If the user runs a command without logging into the CLI,
        # we request they do so before executing their request
        if not is_testing_env:
            loaded_conjurrc = ConjurrcData.load_from_file()
            if not credential_provider.is_exists(loaded_conjurrc.conjur_url):
                # The below message when a user implicitly requested to init
                # pylint: disable=logging-fstring-interpolation
                sys.stdout.write(f"{LOGIN_IS_REQUIRED}\n")
                Cli.handle_login_logic(credential_provider, ssl_verify=args.ssl_verify)

        client = Client(ssl_verify=args.ssl_verify, debug=args.debug)

        if resource == 'list':
            list_data = ListData(kind=args.kind, inspect=args.inspect,
                                 search=args.search, limit=args.limit,
                                 offset=args.offset, role=args.role)
            Cli.handle_list_logic(list_data, client)

        elif resource == 'whoami':
            result = client.whoami()
            print(json.dumps(result, indent=4))

        elif resource == 'variable':
            Cli.handle_variable_logic(args, client)

        elif resource == 'policy':
            policy_data = PolicyData(action=args.action, branch=args.branch, file=args.file)
            Cli.handle_policy_logic(policy_data, client)

        elif resource == 'user':
            Cli.handle_user_logic(credential_provider, args, client)

        elif resource == 'host':
            Cli.handle_host_logic(args, client)

    @staticmethod
    def _parse_args(parser: ArgparseWrapper):
        args = parser.parse_args()

        if not args.resource:
            parser.print_help()
            sys.exit(0)

        # Check whether we are running a command with required additional arguments/options
        if args.resource not in ['list', 'whoami', 'init', 'login', 'logout']:
            if 'action' not in args or not args.action:
                parser.print_help()
                sys.exit(0)

        return args.resource, args

    @staticmethod
    def launch():
        """
        Static wrapper around instantiating and invoking the CLI that
        """
        Cli().run()

if __name__ == '__main__':
    # Not coverage-tested since the integration tests do this
    Cli.launch()  # pragma: no cover
