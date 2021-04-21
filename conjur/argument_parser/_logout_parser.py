import argparse
from conjur.argument_parser.parser_utils import command_description, command_epilog, formatter, title_formatter


class LogoutParser:
    """Partial class of the ArgParseBuilder. holds the public function add_logout_parser."""

    def __init__(self):
        raise NotImplementedError("this is partial class of ArgParseBuilder")

    def add_logout_parser(self):
        """
        Method adds logout parser functionality to parser
        """
        logout_subparser = self._init_logout_parser()
        LogoutParser._add_logout_options(logout_subparser)
        return self

    def _init_logout_parser(self):
        logout_name = 'logout - Log out and delete local cache'
        logout_usage = 'conjur [global options] logout [options]'

        logout_subparser = self.resource_subparsers.add_parser('logout',
                                                               help='Log out from Conjur server and clear local cache',
                                                               description=command_description(logout_name,
                                                                                               logout_usage),
                                                               epilog=command_epilog('conjur logout\t'
                                                                                     'Logs out the user from the Conjur server and deletes the local '
                                                                                     'cache (netrc file)'),
                                                               usage=argparse.SUPPRESS,
                                                               add_help=False,
                                                               formatter_class=formatter)
        return logout_subparser

    @staticmethod
    def _add_logout_options(logout_subparser):
        logout_options = logout_subparser.add_argument_group(title=title_formatter("Options"))
        logout_options.add_argument('-h', '--help', action='help', help='Display help screen and exit')
