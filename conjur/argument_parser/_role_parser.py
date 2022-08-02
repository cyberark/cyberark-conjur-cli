"""
Module For the RoleParser
"""
import argparse
from conjur.argument_parser.parser_utils import command_description, command_epilog, formatter, \
    title_formatter
from conjur.wrapper.argparse_wrapper import ArgparseWrapper


# pylint: disable=too-few-public-methods
class RoleParser:
    """Partial class of the ArgParseBuilder.
    This class add the Role subparser to the ArgParseBuilder parser."""

    def __init__(self):
        self.resource_subparsers = None  # here to reduce warnings on resource_subparsers not exist
        raise NotImplementedError("this is partial class of ArgParseBuilder")

    def add_role_parser(self):
        """
        Method adds role parser functionality to parser
        """
        role_parser = self._create_role_parser()
        role_subparser = role_parser.add_subparsers(title="Subcommand", dest='action')

        self._add_role_exists(role_subparser)
        self._add_role_options(role_parser)

        return self

    def _create_role_parser(self):
        role_name = 'role - Manage roles'
        role_usage = 'conjur [global options] role <subcommand> [options] [args]'

        role_parser = self.resource_subparsers \
            .add_parser('role',
                        help='Manage roles',
                        description=command_description(role_name,
                                                        role_usage),
                        epilog=command_epilog(
                            'conjur role exists -i host:hosts/myhost\t\t\t'
                            'Returns true if the host role hosts/myhost exists\n',
                            command='role',
                            subcommands=['exists']),
                        usage=argparse.SUPPRESS,
                        add_help=False,
                        formatter_class=formatter)
        return role_parser

    @staticmethod
    def _add_role_exists(role_subparser: ArgparseWrapper):
        role_exists_name = 'exists - Determines whether a role exists'
        role_exists_usage = 'conjur [global options] role exists [options] [args]'

        role_exists_subcommand_parser = role_subparser \
            .add_parser(name="exists",
                        help='Determines whether a role exists',
                        description=command_description(
                            role_exists_name, role_exists_usage),
                        epilog=command_epilog(
                            'conjur role exists -i host:hosts/myhost\t\t\t'
                            'Returns true if the host role hosts/myhost exists\n'),
                        usage=argparse.SUPPRESS,
                        add_help=False,
                        formatter_class=formatter)
        role_exists_options = role_exists_subcommand_parser.add_argument_group(
            title=title_formatter("Options"))
        role_exists_options.add_argument('-i', '--id', dest='identifier', metavar='VALUE',
                                          help='Provide role identifier',
                                          required=True)
        role_exists_options.add_argument('--json', dest='json_response', action='store_true',
                                          help='Output a JSON response with a single field, exists')
        role_exists_options.add_argument('-h', '--help', action='help',
                                          help='Display help screen and exit')


    @staticmethod
    def _add_role_options(role_parser: ArgparseWrapper):
        policy_options = role_parser.add_argument_group(title=title_formatter("Options"))
        policy_options.add_argument('-h', '--help', action='help',
                                    help='Display help screen and exit')
