"""
Module For the ResourceParser
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
                            'conjur resource exists -i variable:vars/myvar\t\t\t'
                            'Returns true if the variable resource vars/myvar exists\n',
                            command='resource',
                            subcommands=['exists']),
                        usage=argparse.SUPPRESS,
                        add_help=False,
                        formatter_class=formatter)
        return resource_parser

    @staticmethod
    def _add_resource_exists(resource_subparser: ArgparseWrapper):
        resource_exists_name = 'exists - Determines whether a resource exists'
        resource_exists_usage = 'conjur [global options] resource exists [options] [args]'

        resource_exists_subcommand_parser = resource_subparser \
            .add_parser(name="exists",
                        help='Determines whether a resource exists',
                        description=command_description(
                            resource_exists_name, resource_exists_usage),
                        epilog=command_epilog(
                            'conjur resource exists -i variable:vars/myvar\t\t\t'
                            'Returns true if the variable resource vars/myvar exists\n'),
                        usage=argparse.SUPPRESS,
                        add_help=False,
                        formatter_class=formatter)
        resource_exists_options = resource_exists_subcommand_parser.add_argument_group(
            title=title_formatter("Options"))
        resource_exists_options.add_argument('-i', '--id', dest='identifier', metavar='VALUE',
                                          help='Provide resource identifier',
                                          required=True)
        resource_exists_options.add_argument('--json', dest='json_response', action='store_true',
                                          help='Output a JSON response with a single field, exists')
        resource_exists_options.add_argument('-h', '--help', action='help',
                                          help='Display help screen and exit')


    @staticmethod
    def _add_resource_options(resource_parser: ArgparseWrapper):
        resource_options = resource_parser.add_argument_group(title=title_formatter("Options"))
        resource_options.add_argument('-h', '--help', action='help',
                                    help='Display help screen and exit')
