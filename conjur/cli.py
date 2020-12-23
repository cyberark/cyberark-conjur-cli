# -*- coding: utf-8 -*-

"""
CLI module

This module is the main entrypoint for all CLI-like usages of this
module where only the minimal invocation configuration is required.
"""

# Builtins
import argparse
import json
import logging
import sys

# Third party
import traceback

# Internals
from conjur.argparse_wrapper import ArgparseWrapper
from conjur.client import Client
from conjur.version import __version__

# pylint: disable=too-many-statements
class Cli():
    """
    Main wrapper around CLI-like usages of this module. Provides various
    helpers around parsing of parameters and running client commands.
    """
    LOGGING_FORMAT = '%(asctime)s %(levelname)s: %(message)s'

    @staticmethod
    def usage(*args):
        """
        This method builds the header for the main screen.
        """
        return '''Usage:
  {}'''.format(*args)

    @staticmethod
    def main_epilog():
        """
        This method builds the footer for the main help screen.
        """
        return '''
To get help on a specific command, see `conjur <command> -h`
'''

    @staticmethod
    def command_epilog(*args):
        """
        This method builds the footer for each command help screen.
        """
        return '''Example:
    {}'''.format(*args)

    @staticmethod
    def title(title):
        """
        This method builds a reusable title for each argument section
        """
        return "\n{}".format(title)

    @staticmethod
    def copyright():
        """
        This method builds the copyright description
        """
        return '''
Copyright 2020 CyberArk Software Ltd. All rights reserved.
<www.cyberark.com>
'''

    # pylint: disable=no-self-use, too-many-locals
    def run(self, *args):
        """
        Main entrypoint for the class invocation from both CLI, Package, and
        test sources. Parses CLI args and invokes the appropriate client command.
        """
        formatter_class = lambda prog: argparse.RawTextHelpFormatter(prog,
                                                                     max_help_position=60,
                                                                     width=60)
        # pylint: disable=line-too-long
        parser = ArgparseWrapper(description=self.usage('conjur [global options] <command> <subcommand> [options] [args]'),
                                 epilog=self.main_epilog(),
                                 usage=argparse.SUPPRESS,
                                 add_help=False,
                                 formatter_class=formatter_class)

        global_optional = parser.add_argument_group("Global options")
        resource_subparsers = parser.add_subparsers(dest='resource', title=self.title("Commands"))

        # pylint: disable=line-too-long
        init_subparser = resource_subparsers.add_parser('init',
                                                        help='Initialize the Conjur configuration',
                                                        description=self.usage('conjur [global options] init [options] [args]'),
                                                        epilog=self.command_epilog('conjur init -a my_org -u https://localhost\t'
                                                                                   'Initializes Conjur configuration and writes to file (.conjurrc)'),
                                                        usage=argparse.SUPPRESS,
                                                        add_help=False,
                                                        formatter_class=formatter_class)

        init_options = init_subparser.add_argument_group(title=self.title("Options"))
        init_options.add_argument('-a', '--account',
                                  action='store', dest='name',
                                  help='Provide Conjur account name ' \
                                  '(obtained from Conjur server unless provided by this option)')
        init_options.add_argument('-c', '--certificate',
                                  action='store', dest='certificate',
                                  help='Provide Conjur SSL certificate file location' \
                                  '(obtained from Conjur server unless provided by this option)')
        init_options.add_argument('--force',
                                  action='store_true',
                                  dest='force', help='Force overwrite of existing files')
        init_options.add_argument('-u', '--url',
                                  action='store', dest='url',
                                  help='Provide URL of Conjur server')
        init_options.add_argument('-h', '--help', action='help', help='Display this help screen and exit')

        # pylint: disable=line-too-long
        resource_subparsers.add_parser('list',
                                       help='List all available resources belonging to this account')

        policy_parser = resource_subparsers.add_parser('policy',
                                                       help='Manage policies')
        policy_subparsers = policy_parser.add_subparsers(dest='action')

        apply_policy_parser = policy_subparsers.add_parser('apply',
                                                           help='Apply a policy file')
        apply_policy_parser.add_argument('name',
                                         help='Name of the policy (usually "root")')
        apply_policy_parser.add_argument('policy',
                                         help='File containing the YAML policy')

        replace_policy_parser = policy_subparsers.add_parser('replace',
                                                             help='Replace a policy file')
        replace_policy_parser.add_argument('name',
                                           help='Name of the policy (usually "root")')
        replace_policy_parser.add_argument('policy',
                                           help='File containing the YAML policy')

        delete_policy_parser = policy_subparsers.add_parser('delete',
                                                            help='Delete a policy file')
        delete_policy_parser.add_argument('name',
                                          help='Name of the policy (usually "root")')
        delete_policy_parser.add_argument('policy',
                                          help='File containing the YAML policy')

        variable_parser = resource_subparsers.add_parser('variable',
                                                         help='Manage variables',
                                                         formatter_class=formatter_class)
        variable_subparsers = variable_parser.add_subparsers(dest='action')
        get_variable_parser = variable_subparsers.add_parser('get',
                                                             help='Get the value of a variable')
        set_variable_parser = variable_subparsers.add_parser('set',
                                                             help='Set the value of a variable')

        get_variable_parser.add_argument('variable_id',
                                         help='ID of a variable', nargs='+')

        set_variable_parser.add_argument('variable_id',
                                         help='ID of the variable')
        set_variable_parser.add_argument('value',
                                         help='New value of the variable')
        # pylint: disable=line-too-long
        resource_subparsers.add_parser('whoami',
                                       help='Provides information about the current logged-in user')

        global_optional.add_argument('-h', '--help', action='help', help="Display help list")
        global_optional.add_argument('-v', '--version', action='version',
                                     help="Display version number",
                                     version='Conjur CLI version ' + __version__ + "\n"
                                             + self.copyright())

        global_optional.add_argument('-d', '--debug',
                                     help='Enable debugging output',
                                     action='store_true')

        global_optional.add_argument('--insecure',
                                     help='Skip verification of server certificate (not recommended for production)',
                                     dest='ssl_verify',
                                     action='store_false')

        resource, args = Cli._parse_args(parser)

        # TODO Add tests for exception handling logic
        # pylint: disable=broad-except
        try:
            Cli.run_client_action(resource, args)
        except FileNotFoundError as not_found_error:
            logging.debug(traceback.format_exc())
            sys.stdout.write(f"Error: No such file or directory: '{not_found_error.filename}'")
            sys.exit(1)
        except Exception as error:
            logging.debug(traceback.format_exc())
            sys.stdout.write(str(error))
            sys.exit(1)
        else:
            # Explicit exit (required for tests)
            sys.exit(0)

    @staticmethod
    def run_client_action(resource, args):
        """
        Helper for creating the Client instance and invoking the appropriate
        api class method with the specified parameters.
        """
        if resource == 'init':
            Client.setup_logging(Client, args.debug)
            Client.initialize(args.url,
                              args.name,
                              args.certificate,
                              args.force)

            # A successful exit is required to prevent the initialization of
            # the Client because the init command does not require the Client
            sys.exit(0)

        client = Client(ssl_verify=args.ssl_verify, debug=args.debug)

        if resource == 'list':
            result = client.list()
            print(json.dumps(result, indent=4))
        elif resource == 'whoami':
            result = client.whoami()
            print(json.dumps(result, indent=4))
        elif resource == 'variable':
            variable_id = args.variable_id
            if args.action == 'get':
                if len(variable_id) == 1:
                    variable_value = client.get(variable_id[0])
                    print(variable_value.decode('utf-8'), end='')
                else:
                    variable_values = client.get_many(*variable_id)
                    print(json.dumps(variable_values, indent=4))
            else:
                client.set(variable_id, args.value)
                print("Value set: '{}'".format(variable_id))
        elif resource == 'policy':
            if args.action == 'replace':
                resources = client.replace_policy_file(args.name, args.policy)
                print(json.dumps(resources, indent=4))
            elif args.action == 'delete':
                resources = client.delete_policy_file(args.name, args.policy)
                print(json.dumps(resources, indent=4))
            else:
                resources = client.apply_policy_file(args.name, args.policy)
                print(json.dumps(resources, indent=4))

    @staticmethod
    def _parse_args(parser):
        args = parser.parse_args()

        if not args.resource:
            parser.print_help()
            sys.exit(0)

        # Check whether we are running a command with required additional arguments/options
        if args.resource not in ['list', 'whoami', 'init']:
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
    Cli.launch() # pragma: no cover
