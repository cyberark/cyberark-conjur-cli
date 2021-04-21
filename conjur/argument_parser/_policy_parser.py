"""
Module For the PolicyParser
"""
import argparse
from conjur.argument_parser.parser_utils import command_description, command_epilog, formatter, title_formatter


class PolicyParser:
    """Partial class of the ArgParseBuilder.
    This class add the Policy subparser to the ArgParseBuilder parser."""

    def __init__(self):
        raise NotImplementedError("this is partial class of ArgParseBuilder")

    def add_policy_parser(self):
        """
        Method adds policy parser functionality to parser
        """
        policy_subparser = self._create_policy_parser()

        policy_subparsers = policy_subparser.add_subparsers(dest='action', title=title_formatter("Subcommands"))
        self._add_policy_load(policy_subparsers)
        self._add_policy_replace(policy_subparsers)
        self._add_policy_update(policy_subparsers)
        self._add_policy_options(policy_subparser)

        return self

    def _create_policy_parser(self):
        policy_name = 'policy - Manage policies'
        policy_usage = 'conjur [global options] policy <subcommand> [options] [args]'

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
                                                               formatter_class=formatter)
        return policy_subparser


    @staticmethod


    def _add_policy_load(policy_subparsers):
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
                                                          formatter_class=formatter)

        load_options = load_policy_parser.add_argument_group(title=title_formatter("Options"))
        load_options.add_argument('-f', '--file', required=True, metavar='VALUE',
                                  help='Provide policy file name')
        load_options.add_argument('-b', '--branch', required=True, metavar='VALUE',
                                  help='Provide the policy branch name')
        load_options.add_argument('-h', '--help', action='help', help='Display help screen and exit')


    @staticmethod
    def _add_policy_replace(policy_subparsers):
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
                                                             formatter_class=formatter)

        replace_options = replace_policy_parser.add_argument_group(title=title_formatter("Options"))

        replace_options.add_argument('-f', '--file', required=True, metavar='VALUE',
                                     help='Provide policy file name')
        replace_options.add_argument('-b', '--branch', required=True, metavar='VALUE',
                                     help='Provide the policy branch name')
        replace_options.add_argument('-h', '--help', action='help', help='Display help screen and exit')


    @staticmethod
    def _add_policy_update(policy_subparsers):
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
                                                            formatter_class=formatter)
        update_options = update_policy_parser.add_argument_group(title=title_formatter("Options"))

        update_options.add_argument('-f', '--file', required=True, metavar='VALUE',
                                    help='Provide policy file name')
        update_options.add_argument('-b', '--branch', required=True, metavar='VALUE',
                                    help='Provide the policy branch name')
        update_options.add_argument('-h', '--help', action='help', help='Display help screen and exit')


    @staticmethod
    def _add_policy_options(policy_subparser):
        policy_options = policy_subparser.add_argument_group(title=title_formatter("Options"))
        policy_options.add_argument('-h', '--help', action='help', help='Display help screen and exit')
