"""
Module For the ShowParser
"""

import argparse
from conjur.argument_parser.parser_utils import command_description, command_epilog, formatter, title_formatter
from conjur.wrapper.argparse_wrapper import ArgparseWrapper

# pylint: disable=too-few-public-methods
class ShowParser:
    """Partial class of the ArgParseBuilder.
    This class add the Show subparser to the ArgParseBuilder parser."""

    def __init__(self):
        self.resource_subparsers = None # here to reduce warnings on resource_subparsers not exist
        raise NotImplementedError("this is partial class of ArgParseBuilder")

    def add_show_parser(self):
        """
        Method adds show parser functionality to parser
        """
        show_subparser = self._create_show_parser()
        self._add_show_options(show_subparser)
        return self

    def _create_show_parser(self):
        show_name = 'show - Show an object'
        show_usage = 'conjur [global options] show [args]'

        show_subparser = self.resource_subparsers \
            .add_parser('show',
                        help='Shows an object',
                        description=command_description(show_name,
                                                        show_usage),
                        epilog=command_epilog(
                            'conjur show -i variable:somevariable\t'
                            'Shows metadata about the variable somevariable\n'
                        ),
                        usage=argparse.SUPPRESS,
                        add_help=False,
                        formatter_class=formatter)
        return show_subparser

    @staticmethod
    def _add_show_options(show_subparser: ArgparseWrapper):
        show_options = show_subparser.add_argument_group(title=title_formatter("Options"))

        show_options.add_argument('-i', '--id', dest='identifier', metavar='VALUE',
                                          help='Provide object identifier',
                                          required=True)

        show_options.add_argument('-h', '--help', action='help',
                                    help='Display help screen and exit')
