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

# SDK
from conjur_api.client import Client
from conjur_api.errors.errors import HttpError, HttpStatusError

# Internals
from conjur.argument_parser.argparse_builder import ArgParseBuilder
from conjur.data_object.policy_data import PolicyData
from conjur.logic.credential_provider.credential_store_factory import CredentialStoreFactory
from conjur.errors import CertificateVerificationException
from conjur.errors_messages import INCONSISTENT_VERIFY_MODE_MESSAGE
from conjur.util.util_functions import determine_status_code_specific_error_messages, \
    file_is_missing_or_empty, get_ssl_verification_meta_data_from_conjurrc
from conjur.wrapper import ArgparseWrapper
from conjur.constants import DEFAULT_CONFIG_FILE, LOGIN_IS_REQUIRED

from conjur.data_object import ConjurrcData
from conjur import cli_actions
from conjur.version import __version__


# pylint: disable=too-many-statements
class Cli:
    """
    Main wrapper around CLI-like usages of this module. Provides various
    helpers around parsing of parameters and running client commands.
    """

    def __init__(self):
        # TODO stop using testing_env
        self.is_testing_env = str(os.getenv('TEST_ENV')).lower() == 'true'

        # Assume default credential store option until we get to parse the CLI args
        self.credential_provider = CredentialStoreFactory.create_credential_store()

    def run(self):
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

        resource, args = self._parse_args(parser)

        Client.configure_logger(debug=args.debug)

        # There may be a better way to do this. Currently we have to
        # re-initialize the credential store once the CLI args become available
        if 'use_netrc' not in args or args.use_netrc is False:
            args.use_netrc = None
        self.credential_provider = CredentialStoreFactory.create_credential_store(args.use_netrc)

        # pylint: disable=broad-except
        try:
            self.run_action(resource, args)
        except KeyboardInterrupt:
            self._handle_keyboard_interrupt_exception()
        except FileNotFoundError as file_not_found_error:
            self._handle_file_not_found_exception(file_not_found_error)
        except HttpError as server_error:
            self._handle_http_exception(server_error, args)
        except CertificateVerificationException:
            self._handle_certificate_verification_exception(args)
        except Exception as error:
            self._handle_general_exception(args, error)

        else:
            # Explicit exit (required for tests)
            sys.exit(0)

    # pylint: disable=too-many-branches,logging-fstring-interpolation
    def run_action(self, resource: str, args):
        """
        Helper for creating the Client instance and invoking the appropriate
        api class method with the specified parameters.
        """

        # Needed for unit tests so that they do not require configuring

        if resource in ['logout', 'init', 'login']:
            self._run_auth_flow(args, resource)
            return
        self._perform_auth_if_not_login(args)
        self._run_command_flow(args, resource)

    def _run_auth_flow(self, args, resource):
        # pylint: disable=no-else-return,line-too-long
        if resource == 'logout':
            cli_actions.handle_logout_logic(self.credential_provider)
            sys.stdout.write("Successfully logged out from Conjur\n")
            return

        if resource == 'init':
            cli_actions.handle_init_logic(args.url, args.name,
                                          args.authn_type, args.service_id,
                                          args.certificate, args.force,
                                          args.ssl_verify, args.is_self_signed,
                                          args.use_netrc)
            # A successful exit is required to prevent the initialization of
            # the Client because the init command does not require the Client
            # The below message when a user explicitly requested to init
            sys.stdout.write("To start using the Conjur CLI, log in to the Conjur server by "
                             "running `conjur login`\n")
            return

        if resource == 'login':
            # If the user runs a command without configuring the CLI,
            # we request they do so before executing their request
            # pylint: disable=line-too-long
            self._run_init_if_not_occur()

            cli_actions.handle_login_logic(self.credential_provider,
                                           args.identifier, args.password, args.ssl_verify)
            return

    def _run_command_flow(self, args, resource):
        ssl_verification_meta_data = get_ssl_verification_meta_data_from_conjurrc(args.ssl_verify)
        conjurrc_data = ConjurrcData.load_from_file()
        client = Client(ssl_verification_mode=ssl_verification_meta_data.mode,
                        connection_info=conjurrc_data.get_client_connection_info(),
                        authn_strategy=conjurrc_data.get_authn_strategy(self.credential_provider),
                        debug=args.debug,
                        async_mode=False)

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
            cli_actions.handle_user_logic(self.credential_provider, args, client)

        elif resource == 'host':
            cli_actions.handle_host_logic(args, client)

        elif resource == 'hostfactory':
            cli_actions.handle_hostfactory_logic(args, client)

    def _run_init_if_not_occur(self):
        if not self.is_testing_env and file_is_missing_or_empty(DEFAULT_CONFIG_FILE):
            sys.stdout.write("The Conjur CLI needs to be initialized before you can use it\n")
            cli_actions.handle_init_logic()

    def _perform_auth_if_not_login(self, args):
        self._run_init_if_not_occur()
        # If the user runs a command without logging into the CLI,
        # we request they do so before executing their request
        if not self.is_testing_env:
            loaded_conjurrc = ConjurrcData.load_from_file()
            if not self.credential_provider.is_exists(loaded_conjurrc.conjur_url):
                # The below message when a user implicitly requested to init
                # pylint: disable=logging-fstring-interpolation
                sys.stdout.write(f"{LOGIN_IS_REQUIRED}\n")
                cli_actions.handle_login_logic(self.credential_provider, ssl_verify=args.ssl_verify)

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

    @staticmethod
    def _handle_keyboard_interrupt_exception():
        # A new line required so when the CLI is packaged as an exec,
        # it won't erase the previous line
        sys.stdout.write("\n")
        sys.exit(0)

    @staticmethod
    def _handle_file_not_found_exception(file_not_found_error: FileNotFoundError):
        sys.stdout.write(f"Error: No such file or directory: '{file_not_found_error.filename}'\n")
        sys.exit(1)

    @staticmethod
    def _handle_http_exception(server_error, args):
        logging.debug(traceback.format_exc())
        if isinstance(server_error, HttpStatusError):
            sys.stdout.write(determine_status_code_specific_error_messages(server_error))
        else:
            sys.stdout.write(f"Failed to execute command. Reason: {server_error}\n")

        if args.debug is False:
            sys.stdout.write("Run the command again in debug mode for more information.\n")
        sys.exit(1)

    @staticmethod
    def _handle_certificate_verification_exception(args):
        logging.debug(traceback.format_exc())
        sys.stdout.write(f"Failed to execute command. Reason: "
                         f"{INCONSISTENT_VERIFY_MODE_MESSAGE}\n")
        if args.debug is False:
            sys.stdout.write("Run the command again in debug mode for more information.\n")
        sys.exit(1)

    @staticmethod
    def _handle_general_exception(args, error):
        logging.debug(traceback.format_exc())
        sys.stdout.write(f"Failed to execute command. Reason: {str(error)}\n")
        if args.debug is False:
            sys.stdout.write("Run the command again in debug mode for more information.\n")
        sys.exit(1)


if __name__ == '__main__':
    # Not coverage-tested since the integration tests do this
    Cli.launch()  # pragma: no cover
