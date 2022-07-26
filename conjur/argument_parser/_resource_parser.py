"""
Module For the Parser
"""
import argparse
from conjur.argument_parser.parser_utils import command_description, command_epilog, formatter, \
    title_formatter
from conjur.wrapper.argparse_wrapper import ArgparseWrapper


# pylint: disable=too-few-public-methods
class ResourceParser:
    """Partial class of the ArgParseBuilder.
    This class add the Resource subparser to the ArgParseBuilder parser."""

    def __init__(self):
        self.resource_subparsers = None  # here to reduce warnings on resource_subparsers not exist
        raise NotImplementedError("this is partial class of ArgParseBuilder")

    def add_resource_parser(self):
        """
        Method adds resource parser functionality to parser
        """
        resource_parser = self._create_resource_parser()
        resource_subparser = resource_parser.add_subparsers(title="Subcommand", dest='action')

        self._add_resource_exists(resource_subparser)
        self._add_resource_permitted_roles(resource_subparser)
        self._add_resource_options(resource_parser)

        return self

    def _create_resource_parser(self):
        resource_name = 'resource - Manage resources'
        resource_usage = 'conjur [global options] resource <subcommand> [options] [args]'

        resource_parser = self.resource_subparsers \
            .add_parser('resource',
                        help='Manage resources',
                        description=command_description(resource_name,
                                                        resource_usage),
                        epilog=command_epilog(
                            'conjur resource get -i secrets/mysecret\t\t\t'
                            'Gets the value of resource secrets/mysecret\n'
                            'conjur resource permitted_roles -k variable -i secrets/mysecret -p read\t\t\t'
                            'Gets the list of roles with read access on the resource secrets/mysecret\n',
                            command='resource',
                            subcommands=['get', 'set']),
                        usage=argparse.SUPPRESS,
                        add_help=False,
                        formatter_class=formatter)
        return resource_parser

    @staticmethod
    def _add_resource_exists(resource_subparser: ArgparseWrapper):
        resource_get_name = 'exists - Return True if the resource exists, False if not'
        resource_get_usage = 'conjur [global options] resource exists [options] [args]'

        resource_get_subcommand_parser = resource_subparser \
            .add_parser(name="exists",
                        help='Determines whether a resource exists',
                        description=command_description(
                            resource_get_name, resource_get_usage),
                        epilog=command_epilog(
                            'conjur resource exists -k variable -i secrets/mysecret\t\t\t'
                            'Returns true if the variable secrets/mysecret exists\n'),
                        usage=argparse.SUPPRESS,
                        add_help=False,
                        formatter_class=formatter)
        resource_get_options = resource_get_subcommand_parser.add_argument_group(
            title=title_formatter("Options"))
        resource_get_options.add_argument('-k', '--kind', dest='kind', metavar='VALUE',
                                          help='Provide resource kind',
                                          required=True)
        resource_get_options.add_argument('-i', '--id', dest='identifier', metavar='VALUE',
                                          help='Provide resource identifier',
                                          required=True)
        resource_get_options.add_argument('-h', '--help', action='help',
                                          help='Display help screen and exit')

    @staticmethod
    def _add_resource_permitted_roles(resource_subparser: ArgparseWrapper):
        resource_get_name = 'permitted_roles - Returns a set of roles with access to the resource'
        resource_get_usage = 'conjur [global options] resource permitted_roles [options] [args]'

        resource_get_subcommand_parser = resource_subparser \
            .add_parser(name="permitted_roles",
                        help='List roles with a specified privilege on the resource',
                        description=command_description(
                            resource_get_name, resource_get_usage),
                        epilog=command_epilog(
                            'conjur resource permitted_roles -k variable -i secrets/mysecret -p read\t\t\t'
                            'Gets the list of roles with read access on the variable secrets/mysecret\n'),
                        usage=argparse.SUPPRESS,
                        add_help=False,
                        formatter_class=formatter)
        resource_get_options = resource_get_subcommand_parser.add_argument_group(
            title=title_formatter("Options"))
        resource_get_options.add_argument('-k', '--kind', dest='kind', metavar='VALUE',
                                          help='Provide resource kind',
                                          required=True)
        resource_get_options.add_argument('-i', '--id', dest='identifier', metavar='VALUE',
                                          help='Provide resource identifier',
                                          required=True)
        resource_get_options.add_argument('-p', '--privilege', dest='privilege', metavar='VALUE',
                                          help='Provide privilege',
                                          required=True)
        resource_get_options.add_argument('-h', '--help', action='help',
                                          help='Display help screen and exit')

    @staticmethod
    def _add_resource_options(resource_parser: ArgparseWrapper):
        policy_options = resource_parser.add_argument_group(title=title_formatter("Options"))
        policy_options.add_argument('-h', '--help', action='help',
                                    help='Display help screen and exit')
