"""
Module For the UserParser
"""
import argparse
from conjur.argument_parser.parser_utils import command_description, command_epilog, formatter, \
    title_formatter


# pylint: disable=too-few-public-methods
class UserParser:
    """Partial class of the ArgParseBuilder.
    This class add the User subparser to the ArgParseBuilder parser."""

    def __init__(self):
        self.resource_subparsers = None  # here to reduce warnings on resource_subparsers not exist
        raise NotImplementedError("this is partial class of ArgParseBuilder")

    def add_user_parser(self):
        """
        Method adds user parser functionality to parser
        """
        user_subparser = self._create_user_parser()
        user_subparsers = user_subparser.add_subparsers(dest='action',
                                                        title=title_formatter("Subcommands"))
        self._add_rotate_api_parser(user_subparsers)
        self._add_change_password(user_subparsers)
        self._add_user_options(user_subparser)

        return self

    def _create_user_parser(self):
        user_name = 'user - Manage users'
        user_usage = 'conjur [global options] user <subcommand> [options] [args]'
        user_subparser = self.resource_subparsers \
            .add_parser('user',
                        help='Manage users',
                        description=command_description(user_name,
                                                        user_usage),
                        epilog=command_epilog(
                            'conjur user rotate-api-key\t\t\t'
                            'Rotates logged-in user\'s API key\n'
                            '    conjur user rotate-api-key -i joe\t\t'
                            'Rotates the API key for user joe\n'
                            '    conjur user change-password\t\t\t'
                            'Prompts for password change for the logged-in user\n'
                            '    conjur user change-password -p Myp@SSw0rds!\t'
                            'Changes the password for the logged-in user to Myp@SSw0rds!',
                            command='user',
                            subcommands=['rotate-api-key',
                                         'change-password']),
                        usage=argparse.SUPPRESS,
                        add_help=False,
                        formatter_class=formatter)

        return user_subparser

    @staticmethod
    def _add_rotate_api_parser(sub_parser):
        user_rotate_api_key_name = 'rotate-api-key - Rotate a user’s API key'
        user_rotate_api_key_usage = 'conjur [global options] user rotate-api-key [options] [args]'
        user_rotate_api_key_parser = sub_parser \
            .add_parser('rotate-api-key',
                        help='Rotate a resource\'s API key',
                        description=command_description(
                            user_rotate_api_key_name,
                            user_rotate_api_key_usage),
                        epilog=command_epilog(
                            'conjur user rotate-api-key\t\t\t'
                            'Rotates logged-in user\'s API key\n'
                            '    conjur user rotate-api-key -i joe\t\t'
                            'Rotates the API key for user joe\n'),
                        usage=argparse.SUPPRESS,
                        add_help=False,
                        formatter_class=formatter)
        user_rotate_api_key_options = user_rotate_api_key_parser.add_argument_group(
            title=title_formatter("Options"))
        user_rotate_api_key_options.add_argument('-i', '--id',
                                                 help='Provide the identifier of the user for whom '
                                                      'you want to rotate the API key '
                                                      '(Default: logged-in user)')
        user_rotate_api_key_options.add_argument('-h', '--help', action='help',
                                                 help='Display help screen and exit')

    @staticmethod
    def _add_change_password(sub_parser):
        user_change_password_name = 'change-password - Change the password for the logged-in user'
        user_change_password_usage = 'conjur [global options] user change-password [options] [args]'
        user_change_password = sub_parser \
            .add_parser('change-password',
                        help='Change the password for the logged-in user',
                        description=command_description(
                            user_change_password_name, user_change_password_usage),
                        epilog=command_epilog('conjur user change-password\t\t\t'
                                              'Prompts for a new password for the logged-in user\n'
                                              '    conjur user change-password -p Myp@SSw0rds!\t'
                                              'Changes the password for the '
                                              'logged-in user to Myp@SSw0rds!'),
                        usage=argparse.SUPPRESS,
                        add_help=False,
                        formatter_class=formatter)

        user_change_password_options = user_change_password.add_argument_group(
            title=title_formatter("Options"))
        user_change_password_options.add_argument('-p', '--password', metavar='VALUE',
                                                  help='Provide the new password '
                                                       'for the logged-in user')
        user_change_password_options.add_argument('-h', '--help', action='help',
                                                  help='Display help screen and exit')

    @staticmethod
    def _add_user_options(sub_parser: argparse.ArgumentParser):
        user_options = sub_parser.add_argument_group(title=title_formatter("Options"))
        user_options.add_argument('-h', '--help', action='help',
                                  help='Display help screen and exit')
