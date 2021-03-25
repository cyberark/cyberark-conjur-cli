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
import traceback

# Third party
import requests

# Internals
from conjur.api import SSLClient
from conjur.logic.credential_provider.credential_store_factory import CredentialStoreFactory
from conjur.errors import CertificateVerificationException
from conjur.errors_messages import INCONSISTENT_VERIFY_MODE_MESSAGE
from conjur.util.util_functions import determine_status_code_specific_error_messages, file_is_missing_or_empty
from conjur.wrapper import ArgparseWrapper
from conjur.api.client import Client
from conjur.constants import DEFAULT_CONFIG_FILE
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

    @staticmethod
    def usage(*args):
        """
        This method builds the header for the main screen.
        """
        return '''Usage:
  {}'''.format(*args)

    @staticmethod
    def command_description(example, usage):
        """
        This method builds the header for the main screen.
        """
        return '''
        
Name:
  {}

Usage:
  {}'''.format(example, usage)

    @staticmethod
    def main_epilog():
        """
        This method builds the footer for the main help screen.
        """
        return '''
To get help on a specific command, see `conjur <command> -h | --help`

To start using Conjur with your environment, you must first initialize the configuration. See `conjur init -h` for more information.
'''

    @staticmethod
    def command_epilog(example, command=None, subcommands=None):
        """
        This method builds the footer for each command help screen.
        """
        refer_to_help = "See more details in each subcommand's help:"
        if subcommands:
            res = ""
            for subcommand in subcommands:
                res += "conjur " + command + " " + subcommand + " -h\n"
            return f'''{refer_to_help}\n{res}'''
        return f'''Examples:
    {example}'''

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
Copyright (c) 2021 CyberArk Software Ltd. All rights reserved.
<www.cyberark.com>
'''

    # pylint: disable=no-self-use, too-many-locals
    def run(self, *args):
        """
        Main entrypoint for the class invocation from both CLI, Package, and
        test sources. Parses CLI args and invokes the appropriate client command.
        """
        formatter_class = lambda prog: argparse.RawTextHelpFormatter(prog,
                                                                     max_help_position=100,
                                                                     width=100)
        # pylint: disable=line-too-long
        parser = ArgparseWrapper(
            description=self.usage('conjur [global options] <command> <subcommand> [options] [args]'),
            epilog=self.main_epilog(),
            usage=argparse.SUPPRESS,
            add_help=False,
            formatter_class=formatter_class)

        global_optional = parser.add_argument_group("Global options")
        resource_subparsers = parser.add_subparsers(dest='resource', title=self.title("Commands"))

        # *************** INIT COMMAND ***************

        init_name = 'init - Initialize Conjur configuration'
        input_usage = 'conjur [global options] init [options] [args]'
        # pylint: disable=line-too-long
        init_subparser = resource_subparsers.add_parser('init',
                                                        help='Initialize Conjur configuration',
                                                        description=self.command_description(init_name, input_usage),
                                                        epilog=self.command_epilog(
                                                            'conjur init -a my_org -u https://conjur-server\t'
                                                            'Initializes Conjur configuration and writes to file (.conjurrc)'),
                                                        usage=argparse.SUPPRESS,
                                                        add_help=False,
                                                        formatter_class=formatter_class)

        init_options = init_subparser.add_argument_group(title=self.title("Options"))
        init_options.add_argument('-u', '--url', metavar='VALUE',
                                  action='store', dest='url',
                                  help='Provide URL of Conjur server')
        init_options.add_argument('-a', '--account', metavar='VALUE',
                                  action='store', dest='name',
                                  help='Provide Conjur account name. ' \
                                       'Optional for Conjur Enterprise - overrides the value on the Conjur Enterprise server')
        init_options.add_argument('-c', '--certificate', metavar='VALUE',
                                  action='store', dest='certificate',
                                  help='Optional- provide path to Conjur SSL certificate ' \
                                       '(obtained from Conjur server unless provided by this option)')
        init_options.add_argument('--force',
                                  action='store_true',
                                  dest='force', help='Optional- force overwrite of existing files')
        init_options.add_argument('-h', '--help', action='help', help='Display help screen and exit')

        # *************** LOGIN COMMAND ***************

        login_name = 'login - Log in to Conjur server'
        login_usage = 'conjur [global options] login [options] [args]'
        # pylint: disable=line-too-long
        login_subparser = resource_subparsers.add_parser('login',
                                                         help='Log in to Conjur server',
                                                         description=self.command_description(login_name, login_usage),
                                                         epilog=self.command_epilog('conjur login \t\t\t\t'
                                                                                    'Prompts for the login name and password to log in to Conjur server\n'
                                                                                    '    conjur login -i admin \t\t\t'
                                                                                    'Prompts for password of the admin user to log in to Conjur server\n'
                                                                                    '    conjur login -i admin -p Myp@SSw0rds!\t'
                                                                                    'Logs the admin user in to Conjur server and saves the user and password '
                                                                                    'in the local cache (netrc file)'),
                                                         usage=argparse.SUPPRESS,
                                                         add_help=False,
                                                         formatter_class=formatter_class)

        login_options = login_subparser.add_argument_group(title=self.title("Options"))
        login_options.add_argument('-i', '--id', metavar='VALUE',
                                   action='store', dest='identifier',
                                   help='Provide a login name to log into Conjur server')
        login_options.add_argument('-p', '--password', metavar='VALUE',
                                   action='store', dest='password',
                                   help='Provide a password or API key for the specified login name')
        login_options.add_argument('-h', '--help', action='help', help='Display help screen and exit')

        # *************** LOGOUT COMMAND ***************

        logout_name = 'logout - Log out and delete local cache'
        logout_usage = 'conjur [global options] logout [options]'
        # pylint: disable=line-too-long
        logout_subparser = resource_subparsers.add_parser('logout',
                                                          help='Log out from Conjur server and clear local cache',
                                                          description=self.command_description(logout_name,
                                                                                               logout_usage),
                                                          epilog=self.command_epilog('conjur logout\t'
                                                                                     'Logs out the user from the Conjur server and deletes the local '
                                                                                     'cache (netrc file)'),
                                                          usage=argparse.SUPPRESS,
                                                          add_help=False,
                                                          formatter_class=formatter_class)
        logout_options = logout_subparser.add_argument_group(title=self.title("Options"))
        logout_options.add_argument('-h', '--help', action='help', help='Display help screen and exit')

        # *************** LIST COMMAND ***************

        list_name = 'list - List resources within an organization\'s account'
        list_usage = 'conjur [global options] list [options] [args]'
        # pylint: disable=line-too-long
        list_subparser = resource_subparsers.add_parser('list',
                                                        help='List all available resources belonging to this account',
                                                        description=self.command_description(list_name, list_usage),
                                                        epilog=self.command_epilog('conjur list --kind=variable\t\t\t'
                                                                                   'Filters list by variable\n'
                                                                                   '    conjur list --limit=20\t\t\t'
                                                                                   'Lists first 20 resources\n'
                                                                                   '    conjur list --offset=4\t\t\t'
                                                                                   'Skips the first 4 resources in the list and displays all the rest\n'
                                                                                   '    conjur list --role=myorg:user:superuser\t'
                                                                                   'Shows resources that superuser is entitled to see\n'
                                                                                   '    conjur list --search=superuser\t\t'
                                                                                   'Searches for resources with superuser\n'),
                                                        usage=argparse.SUPPRESS,
                                                        add_help=False,
                                                        formatter_class=formatter_class)

        list_options = list_subparser.add_argument_group(title=self.title("Options"))
        list_options.add_argument('-i', '--inspect',
                                  action='store_true', dest='inspect',
                                  help='Optional- list the metadata for resources')
        list_options.add_argument('-k', '--kind',
                                  action='store', metavar='VALUE', dest='kind',
                                  help='Optional- filter resources by specified kind (user | host | layer | group | policy | variable | webservice)')
        list_options.add_argument('-l', '--limit',
                                  action='store', metavar='VALUE', dest='limit',
                                  help='Optional- limit list of resources to specified number')
        list_options.add_argument('-o', '--offset',
                                  action='store', metavar='VALUE', dest='offset',
                                  help='Optional- skip specified number of resources')
        list_options.add_argument('-r', '--role',
                                  action='store', metavar='VALUE', dest='role',
                                  help='Optional- retrieve list of resources that specified role is entitled to see (must specify role’s full ID)')
        list_options.add_argument('-s', '--search',
                                  action='store', metavar='VALUE', dest='search',
                                  help='Optional- search for resources based on specified query')
        list_options.add_argument('-h', '--help', action='help', help='Display help screen and exit')

        # *************** POLICY COMMAND ***************

        policy_name = 'policy - Manage policies'
        policy_usage = 'conjur [global options] policy <subcommand> [options] [args]'
        # pylint: disable=line-too-long
        policy_subparser = resource_subparsers.add_parser('policy',
                                                          help='Manage policies',
                                                          description=self.command_description(policy_name,
                                                                                               policy_usage),
                                                          epilog=self.command_epilog(
                                                              'conjur policy load -f /tmp/myPolicy.yml -b backend/dev\t'
                                                              'Creates and loads the policy myPolicy.yml under branch backend/dev\n'
                                                              '    conjur policy replace -f /tmp/myPolicy.yml -b root\t\t'
                                                              'Replaces the existing policy myPolicy.yml under branch root\n'
                                                              '    conjur policy update -f /tmp/myPolicy.yml -b root\t\t'
                                                              'Updates existing resources in the policy /tmp/myPolicy.yml under branch root\n',
                                                              command='policy',
                                                              subcommands=['load', 'replace', 'update']),
                                                          usage=argparse.SUPPRESS,
                                                          add_help=False,
                                                          formatter_class=formatter_class)
        policy_subparsers = policy_subparser.add_subparsers(dest='action', title=self.title("Subcommands"))

        policy_load_name = 'load - Load a policy and create resources'
        policy_load_usage = 'conjur [global options] policy load [options] [args]'

        load_policy_parser = policy_subparsers.add_parser('load',
                                                          help='Load a policy and create resources',
                                                          description=self.command_description(policy_load_name,
                                                                                               policy_load_usage),
                                                          epilog=self.command_epilog(
                                                              'conjur policy load -f /tmp/myPolicy.yml -b backend/dev\t'
                                                              'Creates and loads the policy myPolicy.yml under branch backend/dev\n'),
                                                          usage=argparse.SUPPRESS,
                                                          add_help=False,
                                                          formatter_class=formatter_class)

        load_options = load_policy_parser.add_argument_group(title=self.title("Options"))
        load_options.add_argument('-f', '--file', required=True, metavar='VALUE',
                                  help='Provide policy file name')
        load_options.add_argument('-b', '--branch', required=True, metavar='VALUE',
                                  help='Provide the policy branch name')
        load_options.add_argument('-h', '--help', action='help', help='Display help screen and exit')

        policy_replace_name = 'replace - Fully replace an existing policy'
        policy_replace_usage = 'conjur [global options] policy replace [options] [args]'
        replace_policy_parser = policy_subparsers.add_parser('replace',
                                                             help='Fully replace an existing policy',
                                                             description=self.command_description(policy_replace_name,
                                                                                                  policy_replace_usage),
                                                             epilog=self.command_epilog(
                                                                 'conjur policy replace -f /tmp/myPolicy.yml -b root\t\t'
                                                                 'Replaces the existing policy myPolicy.yml under branch root\n'),
                                                             usage=argparse.SUPPRESS,
                                                             add_help=False,
                                                             formatter_class=formatter_class)

        replace_options = replace_policy_parser.add_argument_group(title=self.title("Options"))

        replace_options.add_argument('-f', '--file', required=True, metavar='VALUE',
                                     help='Provide policy file name')
        replace_options.add_argument('-b', '--branch', required=True, metavar='VALUE',
                                     help='Provide the policy branch name')
        replace_options.add_argument('-h', '--help', action='help', help='Display help screen and exit')

        policy_update_name = 'update - Update existing resources in policy or create new resources'
        policy_update_usage = 'conjur [global options] policy update [options] [args]'
        update_policy_parser = policy_subparsers.add_parser('update',
                                                            help='Update existing resources in policy or create new resources',
                                                            description=self.command_description(policy_update_name,
                                                                                                 policy_update_usage),
                                                            epilog=self.command_epilog(
                                                                'conjur policy update -f /tmp/myPolicy.yml -b root\t'
                                                                'Updates existing resources in the policy /tmp/myPolicy.yml under branch root\n'),
                                                            usage=argparse.SUPPRESS,
                                                            add_help=False,
                                                            formatter_class=formatter_class)
        replace_options = update_policy_parser.add_argument_group(title=self.title("Options"))

        replace_options.add_argument('-f', '--file', required=True, metavar='VALUE',
                                     help='Provide policy file name')
        replace_options.add_argument('-b', '--branch', required=True, metavar='VALUE',
                                     help='Provide the policy branch name')
        replace_options.add_argument('-h', '--help', action='help', help='Display help screen and exit')

        policy_options = policy_subparser.add_argument_group(title=self.title("Options"))
        policy_options.add_argument('-h', '--help', action='help', help='Display help screen and exit')

        # *************** USER COMMAND ***************

        user_name = 'user - Manage users'
        user_usage = 'conjur [global options] user <subcommand> [options] [args]'
        user_subparser = resource_subparsers.add_parser('user',
                                                        help='Manage users',
                                                        description=self.command_description(user_name, user_usage),
                                                        epilog=self.command_epilog('conjur user rotate-api-key\t\t\t'
                                                                                   'Rotates logged-in user\'s API key\n'
                                                                                   '    conjur user rotate-api-key -i joe\t\t'
                                                                                   'Rotates the API key for user joe\n'
                                                                                   '    conjur user change-password\t\t\t'
                                                                                   'Prompts for password change for the logged-in user\n'
                                                                                   '    conjur user change-password -p Myp@SSw0rds!\t'
                                                                                   'Changes the password for the logged-in user to Myp@SSw0rds!',
                                                                                   command='user',
                                                                                   subcommands=['rotate-api-key',
                                                                                                'change-password']),
                                                        usage=argparse.SUPPRESS,
                                                        add_help=False,
                                                        formatter_class=formatter_class)

        user_subparsers = user_subparser.add_subparsers(dest='action', title=self.title("Subcommands"))
        user_rotate_api_key_name = 'rotate-api-key - Rotate a user’s API key'
        user_rotate_api_key_usage = 'conjur [global options] user rotate-api-key [options] [args]'
        user_rotate_api_key_parser = user_subparsers.add_parser('rotate-api-key',
                                                                help='Rotate a resource\'s API key',
                                                                description=self.command_description(
                                                                    user_rotate_api_key_name,
                                                                    user_rotate_api_key_usage),
                                                                epilog=self.command_epilog(
                                                                    'conjur user rotate-api-key\t\t\t'
                                                                    'Rotates logged-in user\'s API key\n'
                                                                    '    conjur user rotate-api-key -i joe\t\t'
                                                                    'Rotates the API key for user joe\n'),
                                                                usage=argparse.SUPPRESS,
                                                                add_help=False,
                                                                formatter_class=formatter_class)
        user_rotate_api_key_options = user_rotate_api_key_parser.add_argument_group(title=self.title("Options"))
        user_rotate_api_key_options.add_argument('-i', '--id',
                                                 help='Provide the identifier of the user for whom you want to rotate the API key (Default: logged-in user)')
        user_rotate_api_key_options.add_argument('-h', '--help', action='help', help='Display help screen and exit')

        user_change_password_name = 'change-password - Change the password for the logged-in user'
        user_change_password_usage = 'conjur [global options] user change-password [options] [args]'
        user_change_password = user_subparsers.add_parser('change-password',
                                                          help='Change the password for the logged-in user',
                                                          description=self.command_description(
                                                              user_change_password_name, user_change_password_usage),
                                                          epilog=self.command_epilog('conjur user change-password\t\t\t'
                                                                                     'Prompts for a new password for the logged-in user\n'
                                                                                     '    conjur user change-password -p Myp@SSw0rds!\t'
                                                                                     'Changes the password for the logged-in user to Myp@SSw0rds!'),
                                                          usage=argparse.SUPPRESS,
                                                          add_help=False,
                                                          formatter_class=formatter_class)

        user_change_password_options = user_change_password.add_argument_group(title=self.title("Options"))
        user_change_password_options.add_argument('-p', '--password', metavar='VALUE',
                                                  help='Provide the new password for the logged-in user')
        user_change_password_options.add_argument('-h', '--help', action='help', help='Display help screen and exit')

        user_options = user_subparser.add_argument_group(title=self.title("Options"))
        user_options.add_argument('-h', '--help', action='help', help='Display help screen and exit')

        # *************** HOST COMMAND ***************
        host_name = 'host - Manage hosts'
        host_usage = 'conjur [global options] host <subcommand> [options] [args]'
        host_subparser = resource_subparsers.add_parser('host',
                                                        help='Manage hosts',
                                                        description=self.command_description(host_name, host_usage),
                                                        epilog=self.command_epilog(
                                                            'conjur host rotate-api-key -i my_apps/myVM\t\t'
                                                            'Rotates the API key for host myVM',
                                                            command='host',
                                                            subcommands=['change-password']),
                                                        usage=argparse.SUPPRESS,
                                                        add_help=False,
                                                        formatter_class=formatter_class)
        host_subparsers = host_subparser.add_subparsers(dest='action', title=self.title("Subcommands"))
        host_rotate_api_key_name = 'rotate-api-key - Rotate a host\'s API key'
        host_rotate_api_key_usage = 'conjur [global options] host rotate-api-key [options] [args]'
        host_rotate_api_key_parser = host_subparsers.add_parser('rotate-api-key',
                                                                help='Rotate a host\'s API key',
                                                                description=self.command_description(
                                                                    host_rotate_api_key_name,
                                                                    host_rotate_api_key_usage),
                                                                epilog=self.command_epilog(
                                                                    'conjur host rotate-api-key -i my_apps/myVM\t\t'
                                                                    'Rotates the API key for host myVM'),
                                                                usage=argparse.SUPPRESS,
                                                                add_help=False,
                                                                formatter_class=formatter_class)
        host_rotate_api_key = host_rotate_api_key_parser.add_argument_group(title=self.title("Options"))
        host_rotate_api_key.add_argument('-i', '--id',
                                         help='Provide host identifier for which you want to rotate the API key')
        host_rotate_api_key.add_argument('-h', '--help', action='help', help='Display help screen and exit')

        host_options = host_subparser.add_argument_group(title=self.title("Options"))
        host_options.add_argument('-h', '--help', action='help', help='Display help screen and exit')

        # *************** VARIABLE COMMAND ***************

        variable_name = 'variable - Manage variables'
        variable_usage = 'conjur [global options] variable <subcommand> [options] [args]'

        variable_parser = resource_subparsers.add_parser('variable',
                                                         help='Manage variables',
                                                         description=self.command_description(variable_name,
                                                                                              variable_usage),
                                                         epilog=self.command_epilog(
                                                             'conjur variable get -i secrets/mysecret\t\t\t'
                                                             'Gets the value of variable secrets/mysecret\n'
                                                             '    conjur variable get -i secrets/mysecret "secrets/my secret"\t'
                                                             'Gets the values of variables secrets/mysecret and secrets/my secret\n'
                                                             '    conjur variable set -i secrets/mysecret -v my_secret_value\t'
                                                             'Sets the value of variable secrets/mysecret to my_secret_value\n',
                                                             command='variable',
                                                             subcommands=['get', 'set']),
                                                         usage=argparse.SUPPRESS,
                                                         add_help=False,
                                                         formatter_class=formatter_class)

        variable_get_name = 'get - Get the value of a variable'
        variable_get_usage = 'conjur [global options] variable get [options] [args]'
        variable_subparser = variable_parser.add_subparsers(title="Subcommand", dest='action')
        variable_get_subcommand_parser = variable_subparser.add_parser(name="get",
                                                                       help='Get the value of one or more variables',
                                                                       description=self.command_description(
                                                                           variable_get_name, variable_get_usage),
                                                                       epilog=self.command_epilog(
                                                                           'conjur variable get -i secrets/mysecret\t\t\t'
                                                                           'Gets the most recent value of variable secrets/mysecret\n'
                                                                           '    conjur variable get -i secrets/mysecret "secrets/my secret"\t'
                                                                           'Gets the values of variables secrets/mysecret and secrets/my secret\n'
                                                                           '    conjur variable get -i secrets/mysecret --version 2\t\t'
                                                                           'Gets the second version of variable secrets/mysecret\n'),
                                                                       usage=argparse.SUPPRESS,
                                                                       add_help=False,
                                                                       formatter_class=formatter_class)
        variable_get_options = variable_get_subcommand_parser.add_argument_group(title=self.title("Options"))
        variable_get_options.add_argument('-i', '--id', dest='identifier', metavar='VALUE',
                                          help='Provide variable identifier', nargs='*', required=True)
        variable_get_options.add_argument('--version', metavar='VALUE',
                                          help='Optional- specify desired version of variable value')
        variable_get_options.add_argument('-h', '--help', action='help', help='Display help screen and exit')

        variable_set_name = 'set - Set the value of a variable'
        variable_set_usage = 'conjur [global options] variable set [options] [args]'
        variable_set_subcommand_parser = variable_subparser.add_parser(name="set",
                                                                       help='Set the value of a variable',
                                                                       description=self.command_description(
                                                                           variable_set_name, variable_set_usage),
                                                                       epilog=self.command_epilog(
                                                                           'conjur variable set -i secrets/mysecret -v my_secret_value\t'
                                                                           'Sets the value of variable secrets/mysecret to my_secret_value\n'),
                                                                       usage=argparse.SUPPRESS,
                                                                       add_help=False,
                                                                       formatter_class=formatter_class)
        variable_set_options = variable_set_subcommand_parser.add_argument_group(title=self.title("Options"))

        variable_set_options.add_argument('-i', '--id', dest='identifier', metavar='VALUE',
                                          help='Provide variable identifier', required=True)
        variable_set_options.add_argument('-v', '--value', metavar='VALUE',
                                          help='Set the value of the specified variable', required=True)
        variable_set_options.add_argument('-h', '--help', action='help', help='Display help screen and exit')

        policy_options = variable_parser.add_argument_group(title=self.title("Options"))
        policy_options.add_argument('-h', '--help', action='help', help='Display help screen and exit')

        # *************** WHOAMI COMMAND ***************

        whoami_name = 'whoami - Print information about the current logged-in user'
        whoami_usage = 'conjur [global options] whoami [options]'
        # pylint: disable=line-too-long
        whoami_subparser = resource_subparsers.add_parser('whoami',
                                                          help='Provides information about the current logged-in user',
                                                          description=self.command_description(whoami_name,
                                                                                               whoami_usage),
                                                          usage=argparse.SUPPRESS,
                                                          add_help=False,
                                                          formatter_class=formatter_class)
        whoami_options = whoami_subparser.add_argument_group(title=self.title("Options"))

        whoami_options.add_argument('-h', '--help', action='help', help='Display help screen and exit')

        # *************** MAIN HELP SCREEN OPTIONS ***************

        global_optional.add_argument('-h', '--help', action='help', help="Display help list")
        global_optional.add_argument('-v', '--version', action='version',
                                     help="Display version number",
                                     version='Conjur CLI version ' + __version__ + "\n"
                                             + self.copyright())

        global_optional.add_argument('-d', '--debug',
                                     help='Enable debugging output',
                                     action='store_true')

        global_optional.add_argument('--insecure',
                                     help='Skip verification of server certificate (not recommended for production).\nThis makes your system vulnerable to security attacks!\n',
                                     dest='ssl_verify',
                                     action='store_false')

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
            sys.stdout.write(f"Failed to execute command. Reason: {INCONSISTENT_VERIFY_MODE_MESSAGE}\n")
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
    def handle_init_logic(cls, url=None, account=None, cert=None, force=None, ssl_verify=True):
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
    def handle_login_logic(cls, credential_provider, identifier=None, password=None, ssl_verify=True):
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
    def handle_logout_logic(cls, credential_provider, ssl_verify=True):
        """
        Method that wraps the logout call logic
        """
        logout_logic = LogoutLogic(credential_provider)
        logout_controller = LogoutController(ssl_verify=ssl_verify,
                                             logout_logic=logout_logic,
                                             credentials_provider=credential_provider)
        logout_controller.remove_credentials()

    @classmethod
    def handle_list_logic(cls, list_data=None, client=None):
        """
        Method that wraps the list call logic
        """
        list_logic = ListLogic(client)
        list_controller = ListController(list_logic=list_logic,
                                         list_data=list_data)
        list_controller.load()

    @classmethod
    def handle_variable_logic(cls, args=None, client=None):
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
    def handle_policy_logic(cls, policy_data=None, client=None):
        """
        Method that wraps the variable call logic
        """
        policy_logic = PolicyLogic(client)
        policy_controller = PolicyController(policy_logic=policy_logic,
                                             policy_data=policy_data)
        policy_controller.load()

    @classmethod
    def handle_user_logic(cls, credential_provider, args=None, client=None):
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
    def run_action(resource, args):
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
            return

        # Needed for unit tests so that they do not require configuring
        is_testing_env = os.getenv('TEST_ENV') in ('true', 'True')

        # If the user runs a command without configuring the CLI,
        # we request they do so before executing their request
        # pylint: disable=line-too-long
        if not is_testing_env and file_is_missing_or_empty(DEFAULT_CONFIG_FILE):
            sys.stdout.write("The Conjur CLI needs to be initialized before you can use it.\n")
            Cli.handle_init_logic()

        if resource == 'login':
            Cli.handle_login_logic(credential_provider, args.identifier, args.password, args.ssl_verify)
            return

        # If the user runs a command without logging into the CLI,
        # we request they do so before executing their request
        loaded_conjurrc = ConjurrcData.load_from_file()
        if not is_testing_env and not credential_provider.is_exists(loaded_conjurrc.conjur_url):
            sys.stdout.write("To start using the CLI, log in to Conjur.\n")
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
    def _parse_args(parser):
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
