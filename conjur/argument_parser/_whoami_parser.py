import argparse
from conjur.argument_parser.parser_utils import command_description, formatter, title_formatter


class WhoamiParser:
    def add_whoami_parser(self):
        """
        Method adds whoami parser functionality to parser
        """
        whoami_subparser = self._init_whoami_parser()
        WhoamiParser._add_whoami_options(whoami_subparser)
        return self

    def _init_whoami_parser(self):
        whoami_name = 'whoami - Print information about the current logged-in user'
        whoami_usage = 'conjur [global options] whoami [options]'

        whoami_subparser = self.resource_subparsers.add_parser('whoami',
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

        whoami_options.add_argument('-h', '--help', action='help', help='Display help screen and exit')
