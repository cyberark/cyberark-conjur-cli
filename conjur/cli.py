# -*- coding: utf-8 -*-

"""
CLI module

This module is the main entrypoint for all CLI-like usages of this
module where only the minimal invocation configuration is required.
"""

import argparse
import json
import os
import sys

from .client import Client

from .version import __version__


class Cli():
    """
    Main wrapper around CLI-like usages of this module. Provides various
    helpers around parsing of parameters and running client commands.
    """

    #pylint: disable=no-self-use
    def run(self, *args):
        """
        Main entrypoint for the class invocation from both CLI, Package, and
        test sources. Parses CLI args and invokes the appropriate client command.
        """
        parser = argparse.ArgumentParser(description='Conjur Python3 API CLI')

        resource_subparsers = parser.add_subparsers(dest='resource')

        resource_subparsers.add_parser('whoami',
            help='Provides information about the user making an API request.')

        resource_subparsers.add_parser('list',
            help='Lists all available resources beloging to this account')

        variable_parser = resource_subparsers.add_parser('variable',
            help='Perform variable-related actions . See "variable -help" for more options')
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

        policy_parser = resource_subparsers.add_parser('policy',
            help='Perform policy-related actions . See "policy -help" for more options')
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


        parser.add_argument('-v', '--version', action='version',
            version='%(prog)s v' + __version__)

        parser.add_argument('-l', '--url')
        parser.add_argument('-a', '--account')

        parser.add_argument('-c', '--ca-bundle')
        parser.add_argument('--insecure',
            help='Skip verification of server certificate (not recommended)',
            dest='ssl_verify',
            action='store_false')

        # The external names for these are unfortunately named so we remap them
        parser.add_argument('-u', '--user', dest='login_id')
        parser.add_argument('-k', '--api-key')
        parser.add_argument('-p', '--password')

        parser.add_argument('-d', '--debug',
            help='Enable debugging output',
            action='store_true')

        parser.add_argument('--verbose',
            help='Enable verbose debugging output',
            action='store_true')


        resource, args = Cli._parse_args(parser)

        # We don't have a good "debug" vs "verbose" separation right now
        if args.verbose is True:
            args.debug = True

        Cli.run_client_action(resource, args)

        # Explicit exit (required for tests)
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
