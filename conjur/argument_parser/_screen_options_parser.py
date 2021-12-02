"""
Module For the ScreenOptionsParser
"""
from conjur.version import __version__
from conjur.argument_parser.parser_utils import conjur_copyright


# pylint: disable=too-few-public-methods
class ScreenOptionsParser:
    """Partial class of the ArgParseBuilder.
    This class add the ScreenOptions subparser to the ArgParseBuilder parser."""

    def __init__(self):
        self.parser = None  # here to reduce warnings on parser not exist
        raise NotImplementedError("this is partial class of ArgParseBuilder")

    def add_main_screen_options(self):
        """
        Method adds main screen options functionality to parser
        """
        global_optional = self.parser.add_argument_group("Global options")
        global_optional.add_argument('-h', '--help', action='help', help="Display help list")
        global_optional.add_argument('-v', '--version', action='version',
                                     help="Display version number",
                                     version='Conjur CLI version ' + __version__ + "\n"
                                             + conjur_copyright())

        global_optional.add_argument('-d', '--debug',
                                     help='Enable debugging output',
                                     action='store_true')

        global_optional.add_argument('-i', '--insecure',
                                     help='Skip verification of server certificate '
                                          '(not recommended for production).\nThis makes your '
                                          'system vulnerable to security attacks!\n',
                                     dest='ssl_verify',
                                     action='store_false')
        return self
