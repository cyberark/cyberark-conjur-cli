"""
Module For the WhoamiParser
"""

import argparse
from conjur.argument_parser.parser_utils import command_description, formatter, title_formatter


# pylint: disable=too-few-public-methods
class WhoamiParser:
    """Partial class of the ArgParseBuilder.
    This class add the Whoami subparser to the ArgParseBuilder parser."""

    def __init__(self):
        self.resource_subparsers = None # here to reduce warnings on resource_subparsers not exist
        raise NotImplementedError("this is partial class of ArgParseBuilder")

    def add_whoami_parser(self):
        """
        Method adds whoami parser functionality to parser
        """
        whoami_subparser = self._create_whoami_parser()
        self._add_whoami_options(whoami_subparser)
        return self

    def _create_whoami_parser(self):
        whoami_name = 'whoami - Print information about the current logged-in user'
        whoami_usage = 'conjur [global options] whoami [options]'

        whoami_subparser = self.resource_subparsers \
            .add_parser('whoami',
                        help='Provides information about the current logged-in user',
                        description=command_description(whoami_name,
                                                        whoami_usage),
                        usage=argparse.SUPPRESS,
                        add_help=False,
                        formatter_class=formatter)
        return whoami_subparser

    @staticmethod
    def _add_whoami_options(whoami_subparser):
        whoami_options = whoami_subparser.add_argument_group(title=title_formatter("Options"))

        whoami_options.add_argument('-h', '--help', action='help',
                                    help='Display help screen and exit')
