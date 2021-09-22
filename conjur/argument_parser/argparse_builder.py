"""
Module For the argparseBuilder
"""
import argparse
from conjur.wrapper import ArgparseWrapper

from conjur.argument_parser.parser_utils import formatter, header, main_epilog, title_formatter
from conjur.argument_parser._init_parser import InitParser
from conjur.argument_parser._login_parser import LoginParser
from conjur.argument_parser._logout_parser import LogoutParser
from conjur.argument_parser._policy_parser import PolicyParser
from conjur.argument_parser._host_parser import HostParser
from conjur.argument_parser._list_parser import ListParser
from conjur.argument_parser._screen_options_parser import ScreenOptionsParser
from conjur.argument_parser._user_parser import UserParser
from conjur.argument_parser._variable_parser import VariableParser
from conjur.argument_parser._whoami_parser import WhoamiParser


# pylint: disable=line-too-long
class ArgParseBuilder(InitParser,
                      LoginParser,
                      LogoutParser,
                      PolicyParser,
                      HostParser,
                      ListParser,
                      UserParser,
                      VariableParser,
                      WhoamiParser,
                      HostFactoryParser,
                      ScreenOptionsParser):
    """
    This class simplifies and encapsulates the way we build the help screens.
    It uses a fluent interface pattern where each function return
    ArgParseBuilder current instance.
    This class is split into separate subclass file to avoid creating a single big file
    with a lot of code.
    """

    # pylint: disable=super-init-not-called
    # pylint: disable=too-many-ancestors
    def __init__(self):
        """
        Method that init the Builder resources
        """
        self.parser = ArgparseWrapper(
            description=header('conjur [global options] <command> <subcommand> [options] [args]'),
            epilog=main_epilog(),
            usage=argparse.SUPPRESS,
            add_help=False,
            formatter_class=formatter)
        self.resource_subparsers = self.parser.add_subparsers(dest='resource', title=title_formatter("Commands"))


    def build(self) -> ArgparseWrapper:
        """
        Method that return the final parser
        """
        return self.parser
