"""
Module For the CheckParser
"""

import argparse
from conjur.argument_parser.parser_utils import command_description, command_epilog, formatter, title_formatter
from conjur.wrapper.argparse_wrapper import ArgparseWrapper

# pylint: disable=too-few-public-methods
class CheckParser:
    """Partial class of the ArgParseBuilder.
    This class adds the Check subparser to the ArgParseBuilder parser."""

    def __init__(self):
        self.resource_subparsers = None  # here to reduce warnings on resource_subparsers not exist
        raise NotImplementedError("this is partial class of ArgParseBuilder")

    def add_check_parser(self):
        """
        Method adds check parser functionality to parser
        """
        check_subparser = self._create_check_parser()
        self._add_check_options(check_subparser)
        return self

    def _create_check_parser(self):
        check_name = 'check - Check for a privilege on a resource'
        check_usage = 'conjur [global options] resource <subcommand> [options] [args]'

        check_parser = self.resource_subparsers \
            .add_parser('check',
                        help='Check for a privilege',
                        description=command_description(check_name,
                                                        check_usage),
                        epilog=command_epilog(
                            'conjur check -i dev:variable:somevariable -p read\t\t\t\t'
                            'Returns true if a privilege exists on a resource in present, default role\n'
                            '    conjur check -i dev:host:somehost -p execute -r dev:user:someuser\t\t'
                            'Returns true if a privilege exists on a resource in specified role\n\n\n'
                            '\n'
                        ),
                        usage=argparse.SUPPRESS,
                        add_help=False,
                        formatter_class=formatter)
        return check_parser

    @staticmethod
    def _add_check_options(check_subparser: ArgparseWrapper):
        check_options = check_subparser.add_argument_group(title=title_formatter("Options"))

        check_options.add_argument('-i', '--id', dest='identifier', metavar='VALUE',
                                    help='Provide object identifier',
                                    required=True)

        check_options.add_argument('-p', '--privilege', dest='privilege', metavar='VALUE',
                                    help='Privilege to test on the resource',
                                    required=True)

        check_options.add_argument('-r', '--role', dest='role', metavar='VALUE',
                                    help='Optional - Role to check privileges on',
                                    required=False)

        check_options.add_argument('-h', '--help', action='help',
                                    help='Display help screen and exit')
