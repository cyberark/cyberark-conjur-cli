"""
Module For the LogoutParser
"""
import argparse
from conjur.argument_parser.parser_utils import command_description, command_epilog, formatter, \
    title_formatter
from conjur.wrapper.argparse_wrapper import ArgparseWrapper


# pylint: disable=too-few-public-methods
class LogoutParser:
    """Partial class of the ArgParseBuilder.
    This class add the Logout subparser to the ArgParseBuilder parser."""

    def __init__(self):
        self.resource_subparsers = None  # here to reduce warnings on resource_subparsers not exist
        raise NotImplementedError("this is partial class of ArgParseBuilder")

    def add_logout_parser(self):
        """
        Method adds logout parser functionality to parser
        """
        logout_subparser = self._create_logout_parser()
        self._add_logout_options(logout_subparser)
        return self

    def _create_logout_parser(self):
        logout_name = 'logout - Log out and delete local cache'
        logout_usage = 'conjur [global options] logout [options]'

        logout_subparser = self.resource_subparsers \
            .add_parser('logout',
                        help='Log out from Conjur server and clear local cache',
                        description=command_description(logout_name,
                                                        logout_usage),
                        epilog=command_epilog('conjur logout\t'
                                              'Logs out the user from the Conjur'
                                              ' server and deletes the local '
                                              'cache (netrc file)'),
                        usage=argparse.SUPPRESS,
                        add_help=False,
                        formatter_class=formatter)
        return logout_subparser

    @staticmethod
    def _add_logout_options(logout_subparser: ArgparseWrapper):
        logout_options = logout_subparser.add_argument_group(title=title_formatter("Options"))
        logout_options.add_argument('-h', '--help', action='help'
                                    , help='Display help screen and exit')
