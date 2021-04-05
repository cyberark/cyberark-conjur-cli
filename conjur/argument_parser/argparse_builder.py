import argparse
from conjur.wrapper import ArgparseWrapper
from conjur.version import __version__
from conjur.util.parser_utils import *


class ArgParseBuilder:

    def __init__(self):
        self.parser = ArgparseWrapper(
            description=usage('conjur [global options] <command> <subcommand> [options] [args]'),
            epilog=main_epilog(),
            usage=argparse.SUPPRESS,
            add_help=False,
            formatter_class=formatter_class)
        self.resource_subparsers = self.parser.add_subparsers(dest='resource', title=title("Commands"))

    def add_init_parser(self):
        init_name = 'init - Initialize Conjur configuration'
        input_usage = 'conjur [global options] init [options] [args]'
        # pylint: disable=line-too-long
        init_subparser = self.resource_subparsers.add_parser('init',
                                                             help='Initialize Conjur configuration',
                                                             description=command_description(init_name,
                                                                                             input_usage),
                                                             epilog=command_epilog(
                                                                 'conjur init -a my_org -u https://conjur-server\t'
                                                                 'Initializes Conjur configuration and writes to file (.conjurrc)'),
                                                             usage=argparse.SUPPRESS,
                                                             add_help=False,
                                                             formatter_class=formatter_class)

        init_options = init_subparser.add_argument_group(title=title("Options"))
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

        return self

    def add_login_parser(self):
        login_name = 'login - Log in to Conjur server'
        login_usage = 'conjur [global options] login [options] [args]'
        # pylint: disable=line-too-long
        login_subparser = self.resource_subparsers.add_parser('login',
                                                              help='Log in to Conjur server',
                                                              description=command_description(login_name,
                                                                                              login_usage),
                                                              epilog=command_epilog('conjur login \t\t\t\t'
                                                                                    'Prompts for the login name and password to log in to Conjur server\n'
                                                                                    '    conjur login -i admin \t\t\t'
                                                                                    'Prompts for password of the admin user to log in to Conjur server\n'
                                                                                    '    conjur login -i admin -p Myp@SSw0rds!\t'
                                                                                    'Logs the admin user in to Conjur server and saves the user and password '
                                                                                    'in the local cache (netrc file)'),
                                                              usage=argparse.SUPPRESS,
                                                              add_help=False,
                                                              formatter_class=formatter_class)

        login_options = login_subparser.add_argument_group(title=title("Options"))
        login_options.add_argument('-i', '--id', metavar='VALUE',
                                   action='store', dest='identifier',
                                   help='Provide a login name to log into Conjur server')
        login_options.add_argument('-p', '--password', metavar='VALUE',
                                   action='store', dest='password',
                                   help='Provide a password or API key for the specified login name')
        login_options.add_argument('-h', '--help', action='help', help='Display help screen and exit')

        return self

    def add_logout_parser(self):
        logout_name = 'logout - Log out and delete local cache'
        logout_usage = 'conjur [global options] logout [options]'
        # pylint: disable=line-too-long
        logout_subparser = self.resource_subparsers.add_parser('logout',
                                                               help='Log out from Conjur server and clear local cache',
                                                               description=command_description(logout_name,
                                                                                               logout_usage),
                                                               epilog=command_epilog('conjur logout\t'
                                                                                     'Logs out the user from the Conjur server and deletes the local '
                                                                                     'cache (netrc file)'),
                                                               usage=argparse.SUPPRESS,
                                                               add_help=False,
                                                               formatter_class=formatter_class)
        logout_options = logout_subparser.add_argument_group(title=title("Options"))
        logout_options.add_argument('-h', '--help', action='help', help='Display help screen and exit')
        return self

    def add_list_parser(self):
        list_name = 'list - List resources within an organization\'s account'
        list_usage = 'conjur [global options] list [options] [args]'
        # pylint: disable=line-too-long
        list_subparser = self.resource_subparsers.add_parser('list',
                                                             help='List all available resources belonging to this account',
                                                             description=command_description(list_name,
                                                                                             list_usage),
                                                             epilog=command_epilog(
                                                                 'conjur list --kind=variable\t\t\t'
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

        list_options = list_subparser.add_argument_group(title=title("Options"))
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

        return self

    def add_policy_parser(self):
        policy_name = 'policy - Manage policies'
        policy_usage = 'conjur [global options] policy <subcommand> [options] [args]'
        # pylint: disable=line-too-long
        policy_subparser = self.resource_subparsers.add_parser('policy',
                                                               help='Manage policies',
                                                               description=command_description(policy_name,
                                                                                               policy_usage),
                                                               epilog=command_epilog(
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
        policy_subparsers = policy_subparser.add_subparsers(dest='action', title=title("Subcommands"))

        policy_load_name = 'load - Load a policy and create resources'
        policy_load_usage = 'conjur [global options] policy load [options] [args]'

        load_policy_parser = policy_subparsers.add_parser('load',
                                                          help='Load a policy and create resources',
                                                          description=command_description(policy_load_name,
                                                                                          policy_load_usage),
                                                          epilog=command_epilog(
                                                              'conjur policy load -f /tmp/myPolicy.yml -b backend/dev\t'
                                                              'Creates and loads the policy myPolicy.yml under branch backend/dev\n'),
                                                          usage=argparse.SUPPRESS,
                                                          add_help=False,
                                                          formatter_class=formatter_class)

        load_options = load_policy_parser.add_argument_group(title=title("Options"))
        load_options.add_argument('-f', '--file', required=True, metavar='VALUE',
                                  help='Provide policy file name')
        load_options.add_argument('-b', '--branch', required=True, metavar='VALUE',
                                  help='Provide the policy branch name')
        load_options.add_argument('-h', '--help', action='help', help='Display help screen and exit')

        policy_replace_name = 'replace - Fully replace an existing policy'
        policy_replace_usage = 'conjur [global options] policy replace [options] [args]'
        replace_policy_parser = policy_subparsers.add_parser('replace',
                                                             help='Fully replace an existing policy',
                                                             description=command_description(policy_replace_name,
                                                                                             policy_replace_usage),
                                                             epilog=command_epilog(
                                                                 'conjur policy replace -f /tmp/myPolicy.yml -b root\t\t'
                                                                 'Replaces the existing policy myPolicy.yml under branch root\n'),
                                                             usage=argparse.SUPPRESS,
                                                             add_help=False,
                                                             formatter_class=formatter_class)

        replace_options = replace_policy_parser.add_argument_group(title=title("Options"))

        replace_options.add_argument('-f', '--file', required=True, metavar='VALUE',
                                     help='Provide policy file name')
        replace_options.add_argument('-b', '--branch', required=True, metavar='VALUE',
                                     help='Provide the policy branch name')
        replace_options.add_argument('-h', '--help', action='help', help='Display help screen and exit')

        policy_update_name = 'update - Update existing resources in policy or create new resources'
        policy_update_usage = 'conjur [global options] policy update [options] [args]'
        update_policy_parser = policy_subparsers.add_parser('update',
                                                            help='Update existing resources in policy or create new resources',
                                                            description=command_description(policy_update_name,
                                                                                            policy_update_usage),
                                                            epilog=command_epilog(
                                                                'conjur policy update -f /tmp/myPolicy.yml -b root\t'
                                                                'Updates existing resources in the policy /tmp/myPolicy.yml under branch root\n'),
                                                            usage=argparse.SUPPRESS,
                                                            add_help=False,
                                                            formatter_class=formatter_class)
        replace_options = update_policy_parser.add_argument_group(title=title("Options"))

        replace_options.add_argument('-f', '--file', required=True, metavar='VALUE',
                                     help='Provide policy file name')
        replace_options.add_argument('-b', '--branch', required=True, metavar='VALUE',
                                     help='Provide the policy branch name')
        replace_options.add_argument('-h', '--help', action='help', help='Display help screen and exit')

        policy_options = policy_subparser.add_argument_group(title=title("Options"))
        policy_options.add_argument('-h', '--help', action='help', help='Display help screen and exit')

        return self

    def add_user_parser(self):
        user_name = 'user - Manage users'
        user_usage = 'conjur [global options] user <subcommand> [options] [args]'
        user_subparser = self.resource_subparsers.add_parser('user',
                                                             help='Manage users',
                                                             description=command_description(user_name,
                                                                                             user_usage),
                                                             epilog=command_epilog(
                                                                 'conjur user rotate-api-key\t\t\t'
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

        user_subparsers = user_subparser.add_subparsers(dest='action', title=title("Subcommands"))
        user_rotate_api_key_name = 'rotate-api-key - Rotate a user’s API key'
        user_rotate_api_key_usage = 'conjur [global options] user rotate-api-key [options] [args]'
        user_rotate_api_key_parser = user_subparsers.add_parser('rotate-api-key',
                                                                help='Rotate a resource\'s API key',
                                                                description=command_description(
                                                                    user_rotate_api_key_name,
                                                                    user_rotate_api_key_usage),
                                                                epilog=command_epilog(
                                                                    'conjur user rotate-api-key\t\t\t'
                                                                    'Rotates logged-in user\'s API key\n'
                                                                    '    conjur user rotate-api-key -i joe\t\t'
                                                                    'Rotates the API key for user joe\n'),
                                                                usage=argparse.SUPPRESS,
                                                                add_help=False,
                                                                formatter_class=formatter_class)
        user_rotate_api_key_options = user_rotate_api_key_parser.add_argument_group(title=title("Options"))
        user_rotate_api_key_options.add_argument('-i', '--id',
                                                 help='Provide the identifier of the user for whom you want to rotate the API key (Default: logged-in user)')
        user_rotate_api_key_options.add_argument('-h', '--help', action='help', help='Display help screen and exit')

        user_change_password_name = 'change-password - Change the password for the logged-in user'
        user_change_password_usage = 'conjur [global options] user change-password [options] [args]'
        user_change_password = user_subparsers.add_parser('change-password',
                                                          help='Change the password for the logged-in user',
                                                          description=command_description(
                                                              user_change_password_name, user_change_password_usage),
                                                          epilog=command_epilog('conjur user change-password\t\t\t'
                                                                                'Prompts for a new password for the logged-in user\n'
                                                                                '    conjur user change-password -p Myp@SSw0rds!\t'
                                                                                'Changes the password for the logged-in user to Myp@SSw0rds!'),
                                                          usage=argparse.SUPPRESS,
                                                          add_help=False,
                                                          formatter_class=formatter_class)

        user_change_password_options = user_change_password.add_argument_group(title=title("Options"))
        user_change_password_options.add_argument('-p', '--password', metavar='VALUE',
                                                  help='Provide the new password for the logged-in user')
        user_change_password_options.add_argument('-h', '--help', action='help', help='Display help screen and exit')

        user_options = user_subparser.add_argument_group(title=title("Options"))
        user_options.add_argument('-h', '--help', action='help', help='Display help screen and exit')
        return self

    def add_host_parser(self):
        host_name = 'host - Manage hosts'
        host_usage = 'conjur [global options] host <subcommand> [options] [args]'
        host_subparser = self.resource_subparsers.add_parser('host',
                                                             help='Manage hosts',
                                                             description=command_description(host_name,
                                                                                             host_usage),
                                                             epilog=command_epilog(
                                                                 'conjur host rotate-api-key -i my_apps/myVM\t\t'
                                                                 'Rotates the API key for host myVM',
                                                                 command='host',
                                                                 subcommands=['change-password']),
                                                             usage=argparse.SUPPRESS,
                                                             add_help=False,
                                                             formatter_class=formatter_class)
        host_subparsers = host_subparser.add_subparsers(dest='action', title=title("Subcommands"))
        host_rotate_api_key_name = 'rotate-api-key - Rotate a host\'s API key'
        host_rotate_api_key_usage = 'conjur [global options] host rotate-api-key [options] [args]'
        host_rotate_api_key_parser = host_subparsers.add_parser('rotate-api-key',
                                                                help='Rotate a host\'s API key',
                                                                description=command_description(
                                                                    host_rotate_api_key_name,
                                                                    host_rotate_api_key_usage),
                                                                epilog=command_epilog(
                                                                    'conjur host rotate-api-key -i my_apps/myVM\t\t'
                                                                    'Rotates the API key for host myVM'),
                                                                usage=argparse.SUPPRESS,
                                                                add_help=False,
                                                                formatter_class=formatter_class)
        host_rotate_api_key = host_rotate_api_key_parser.add_argument_group(title=title("Options"))
        host_rotate_api_key.add_argument('-i', '--id',
                                         help='Provide host identifier for which you want to rotate the API key')
        host_rotate_api_key.add_argument('-h', '--help', action='help', help='Display help screen and exit')

        host_options = host_subparser.add_argument_group(title=title("Options"))
        host_options.add_argument('-h', '--help', action='help', help='Display help screen and exit')
        return self

    def add_variable_parser(self):
        variable_name = 'variable - Manage variables'
        variable_usage = 'conjur [global options] variable <subcommand> [options] [args]'

        variable_parser = self.resource_subparsers.add_parser('variable',
                                                              help='Manage variables',
                                                              description=command_description(variable_name,
                                                                                              variable_usage),
                                                              epilog=command_epilog(
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
                                                                       description=command_description(
                                                                           variable_get_name, variable_get_usage),
                                                                       epilog=command_epilog(
                                                                           'conjur variable get -i secrets/mysecret\t\t\t'
                                                                           'Gets the most recent value of variable secrets/mysecret\n'
                                                                           '    conjur variable get -i secrets/mysecret "secrets/my secret"\t'
                                                                           'Gets the values of variables secrets/mysecret and secrets/my secret\n'
                                                                           '    conjur variable get -i secrets/mysecret --version 2\t\t'
                                                                           'Gets the second version of variable secrets/mysecret\n'),
                                                                       usage=argparse.SUPPRESS,
                                                                       add_help=False,
                                                                       formatter_class=formatter_class)
        variable_get_options = variable_get_subcommand_parser.add_argument_group(title=title("Options"))
        variable_get_options.add_argument('-i', '--id', dest='identifier', metavar='VALUE',
                                          help='Provide variable identifier', nargs='*', required=True)
        variable_get_options.add_argument('--version', metavar='VALUE',
                                          help='Optional- specify desired version of variable value')
        variable_get_options.add_argument('-h', '--help', action='help', help='Display help screen and exit')

        variable_set_name = 'set - Set the value of a variable'
        variable_set_usage = 'conjur [global options] variable set [options] [args]'
        variable_set_subcommand_parser = variable_subparser.add_parser(name="set",
                                                                       help='Set the value of a variable',
                                                                       description=command_description(
                                                                           variable_set_name, variable_set_usage),
                                                                       epilog=command_epilog(
                                                                           'conjur variable set -i secrets/mysecret -v my_secret_value\t'
                                                                           'Sets the value of variable secrets/mysecret to my_secret_value\n'),
                                                                       usage=argparse.SUPPRESS,
                                                                       add_help=False,
                                                                       formatter_class=formatter_class)
        variable_set_options = variable_set_subcommand_parser.add_argument_group(title=title("Options"))

        variable_set_options.add_argument('-i', '--id', dest='identifier', metavar='VALUE',
                                          help='Provide variable identifier', required=True)
        variable_set_options.add_argument('-v', '--value', metavar='VALUE',
                                          help='Set the value of the specified variable', required=True)
        variable_set_options.add_argument('-h', '--help', action='help', help='Display help screen and exit')

        policy_options = variable_parser.add_argument_group(title=title("Options"))
        policy_options.add_argument('-h', '--help', action='help', help='Display help screen and exit')
        return self

    def add_whoami_parser(self):
        whoami_name = 'whoami - Print information about the current logged-in user'
        whoami_usage = 'conjur [global options] whoami [options]'
        # pylint: disable=line-too-long
        whoami_subparser = self.resource_subparsers.add_parser('whoami',
                                                               help='Provides information about the current logged-in user',
                                                               description=command_description(whoami_name,
                                                                                               whoami_usage),
                                                               usage=argparse.SUPPRESS,
                                                               add_help=False,
                                                               formatter_class=formatter_class)
        whoami_options = whoami_subparser.add_argument_group(title=title("Options"))

        whoami_options.add_argument('-h', '--help', action='help', help='Display help screen and exit')
        return self

    def add_main_screen_options(self):
        global_optional = self.parser.add_argument_group("Global options")
        global_optional.add_argument('-h', '--help', action='help', help="Display help list")
        global_optional.add_argument('-v', '--version', action='version',
                                     help="Display version number",
                                     version='Conjur CLI version ' + __version__ + "\n"
                                             + copyright())

        global_optional.add_argument('-d', '--debug',
                                     help='Enable debugging output',
                                     action='store_true')

        global_optional.add_argument('--insecure',
                                     help='Skip verification of server certificate (not recommended for production).\nThis makes your system vulnerable to security attacks!\n',
                                     dest='ssl_verify',
                                     action='store_false')
        return self

    def build(self) -> ArgparseWrapper:
        return self.parser
