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
from conjur.argument_parser.argparse_builder import ArgParseBuilder
from conjur.logic.credential_provider.credential_store_factory import CredentialStoreFactory
from conjur.errors import CertificateVerificationException
from conjur.errors_messages import INCONSISTENT_VERIFY_MODE_MESSAGE
from conjur.util.util_functions import determine_status_code_specific_error_messages, \
    file_is_missing_or_empty
from conjur.wrapper import ArgparseWrapper
from conjur.api.client import Client
from conjur.constants import DEFAULT_CONFIG_FILE, LOGIN_IS_REQUIRED

from conjur.data_object import ConjurrcData
from conjur.data_object import PolicyData
import conjur.cli_actions as cli_actions
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



    @staticmethod
    # pylint: disable=too-many-branches,logging-fstring-interpolation
    def run_action(resource: str, args):
        """
        Helper for creating the Client instance and invoking the appropriate
        api class method with the specified parameters.
        """
        Client.setup_logging(Client, args.debug)

        credential_provider, _ = CredentialStoreFactory.create_credential_store()
        # pylint: disable=no-else-return,line-too-long
        if resource == 'logout':
            cli_actions.handle_logout_logic(credential_provider, args.ssl_verify)
            sys.stdout.write("Successfully logged out from Conjur\n")
            return

        if resource == 'init':
            cli_actions.handle_init_logic(args.url, args.name, args.certificate, args.force, args.ssl_verify)
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
            cli_actions.handle_init_logic()

        if resource == 'login':
            cli_actions.handle_login_logic(credential_provider, args.identifier, args.password, args.ssl_verify)
            return

        # If the user runs a command without logging into the CLI,
        # we request they do so before executing their request
        if not is_testing_env:
            loaded_conjurrc = ConjurrcData.load_from_file()
            if not credential_provider.is_exists(loaded_conjurrc.conjur_url):
                # The below message when a user implicitly requested to init
                # pylint: disable=logging-fstring-interpolation
                sys.stdout.write(f"{LOGIN_IS_REQUIRED}\n")
                cli_actions.handle_login_logic(credential_provider, ssl_verify=args.ssl_verify)

        client = Client(ssl_verify=args.ssl_verify, debug=args.debug)

        if resource == 'list':
            cli_actions.handle_list_logic(args, client)

        elif resource == 'whoami':
            result = client.whoami()
            print(json.dumps(result, indent=4))

        elif resource == 'variable':
            cli_actions.handle_variable_logic(args, client)

        elif resource == 'policy':
            policy_data = PolicyData(action=args.action, branch=args.branch, file=args.file)
            cli_actions.handle_policy_logic(policy_data, client)

        elif resource == 'user':
            cli_actions.handle_user_logic(credential_provider, args, client)

        elif resource == 'host':
            cli_actions.handle_host_logic(args, client)

        elif resource == 'hostfactory':
            cli_actions.handle_hostfactory_logic(args, client)

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
