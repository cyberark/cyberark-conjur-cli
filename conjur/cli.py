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
import os
import sys

# Third party
import requests

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

    @staticmethod
    def main_description():
        """
        This method builds the header for the main screen.
        """
        return '''Usage:
  conjur [global options] command [subcommand] [value] [--option=arg]'''

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
                                                                     max_help_position=50,
                                                                     width=50)

        parser = ArgparseWrapper(description=self.main_description(),
                                 epilog=self.main_epilog(),
                                 usage=argparse.SUPPRESS,
                                 add_help=False,
                                 formatter_class=argparse.RawTextHelpFormatter)

        global_optional = parser.add_argument_group("Global options")
        resource_subparsers = parser.add_subparsers(dest='resource', title=self.title("Commands"))

        resource_subparsers.add_parser('whoami',
            help='Provides information about the current logged-in user')

        resource_subparsers.add_parser('list',
            help='List all available resources belonging to this account')

        variable_parser = resource_subparsers.add_parser('variable',
                                                         help='Manage variables',
                                                         description=self.usage(
                                                             'conjur [global options] variable <subcommand> '
                                                             '[options] <VARIABLE_ID> <VALUE>'),
                                                         usage=argparse.SUPPRESS,
                                                         add_help=False,
                                                         formatter_class=formatter_class)

        var_options = variable_parser.add_argument_group(title=self.title("Options"))

        var_options.add_argument('-h', '--help', action='help', help='Display help list and exit')
        # TODO: missing Example section in help

        variable_subparsers = variable_parser.add_subparsers(dest='action')

        get_variable_parser = variable_subparsers.add_parser('get',
                                                             help='Get the value of one or more variables')
        set_variable_parser = variable_subparsers.add_parser('set',
                                                             help='Set the value of a variable')

        get_variable_parser.add_argument('variable_id',
                                         help='ID of a variable', nargs='+')

        set_variable_parser.add_argument('variable_id',
                                         help='ID of the variable')
        set_variable_parser.add_argument('value',
                                         help='New value of the variable')

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

        global_optional.add_argument('-h', '--help', action='help', help="Display help list")
        global_optional.add_argument('-v', '--version', action='version',
                                     help="Display version number",
                                     version='Conjur CLI version ' + __version__ + "\n"
                                             + self.copyright())

        global_optional.add_argument('-l', '--url')
        global_optional.add_argument('-a', '--account')

        global_optional.add_argument('-c', '--ca-bundle')
        global_optional.add_argument('--insecure',
            help='Skip verification of server certificate (not recommended)',
            dest='ssl_verify',
            action='store_false')

        # The external names for these are unfortunately named so we remap them
        global_optional.add_argument('-u', '--user', dest='login_id')
        global_optional.add_argument('-k', '--api-key')
        global_optional.add_argument('-p', '--password')

        global_optional.add_argument('-d', '--debug',
            help='Enable debugging output',
            action='store_true')

        global_optional.add_argument('--verbose',
            help='Enable verbose debugging output',
            action='store_true')


        resource, args = Cli._parse_args(parser)

        # We don't have a good "debug" vs "verbose" separation right now
        if args.verbose is True:
            args.debug = True

        # TODO Add tests for exception handling logic
        try:
            Cli.run_client_action(resource, args)
        except FileNotFoundError as not_found_error:
            sys.stdout.write(f"Error: No such file or directory: '{not_found_error.filename}'")
            logging.info('Error: No such file or directory: %s', not_found_error.filename)
            sys.exit(1)
        except requests.exceptions.HTTPError as http_error:
            sys.stdout.write(str(http_error))
            logging.info(str(http_error))
            sys.exit(1)
        else:
            sys.exit(0)

    @staticmethod
    def run_client_action(resource, args):
        """
        Helper for creating the Client instance and invoking the appropriate
        api class method with the specified parameters.
        """

        ca_bundle = None
        if args.ca_bundle:
            ca_bundle = os.path.expanduser(args.ca_bundle)

        # We want explicit definition of things to pass into the client
        # to avoid ambiguity
        client = Client(url=args.url,
                        account=args.account,
                        api_key=args.api_key,
                        login_id=args.login_id,
                        password=args.password,
                        ssl_verify=args.ssl_verify,
                        ca_bundle=ca_bundle,
                        debug=args.debug)

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

        # Check whether we are running a command with required additional
        # arguments and if so, validate that those additional arguments are present
        if args.resource not in ['list', 'whoami']:
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
