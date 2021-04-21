import argparse
from conjur.argument_parser.parser_utils import command_description, command_epilog, formatter, title_formatter


class LoginParser:
    """Partial class of the ArgParseBuilder. holds the public function add_login_parser."""

    def __init__(self):
        raise NotImplementedError("this is partial class of ArgParseBuilder")

    def add_login_parser(self):
        """
        Method adds login parser functionality to parser
        """
        login_subparser = self._init_login_parser()
        LoginParser._add_login_options(login_subparser)

        return self

    def _init_login_parser(self):
        login_name = 'login - Log in to Conjur server'
        login_usage = 'conjur [global options] login [options] [args]'

        login_subparser = self.resource_subparsers.add_parser('login',
                                                              help='Log in to Conjur server',
                                                              description=command_description(login_name,
                                                                                              login_usage),
                                                              epilog=command_epilog('conjur login \t\t\t\t'
                                                                                    'Prompts for the login name and password to log in to Conjur server\n'
                                                                                    '    conjur login -i admin \t\t\t'
                                                                                    'Prompts for password of the admin user to log in to Conjur server\n'
                                                                                    '    conjur login -i admin -p Myp@SSw0rds!\t'
                                                                                    'Logs the admin user in to Conjur server and saves the user and password '
                                                                                    'in the local cache (netrc file)'),
                                                              usage=argparse.SUPPRESS,
                                                              add_help=False,
                                                              formatter_class=formatter)
        return login_subparser

    @staticmethod
    def _add_login_options(login_subparser):
        login_options = login_subparser.add_argument_group(title=title_formatter("Options"))
        login_options.add_argument('-i', '--id', metavar='VALUE',
                                   action='store', dest='identifier',
                                   help='Provide a login name to log into Conjur server')
        login_options.add_argument('-p', '--password', metavar='VALUE',
                                   action='store', dest='password',
                                   help='Provide a password or API key for the specified login name')
        login_options.add_argument('-h', '--help', action='help', help='Display help screen and exit')
