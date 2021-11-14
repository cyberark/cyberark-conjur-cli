"""
Module For the hostfactoryParser
"""
import argparse
from conjur.argument_parser.parser_utils import command_description, command_epilog, formatter, \
    title_formatter
from conjur.wrapper.argparse_wrapper import ArgparseWrapper


# pylint: disable=too-few-public-methods
class HostFactoryParser:
    """Partial class of the ArgParseBuilder.
    This class add the HostFactory subparser to the ArgParseBuilder parser."""

    def __init__(self):
        self.resource_subparsers = None  # here to reduce warnings on resource_subparsers not exist
        raise NotImplementedError("this is partial class of ArgParseBuilder")

    def add_hostfactory_parser(self):
        """
        Method adds hostfactory parser functionality to parser
        """
        hostfactory_parser = self._create_hostfactory_parser()
        hostfactory_subparser = hostfactory_parser.add_subparsers(title="Subcommand", dest='action')
        hostfactory_create_menu_item = self._add_hostfactory_create(hostfactory_subparser)
        hostfactory_revoke_menu_item = self._add_hostfactory_revoke(hostfactory_subparser)
        self._add_hostfactory_create_token(hostfactory_create_menu_item)
        self._add_hostfactory_create_host(hostfactory_create_menu_item)
        self._add_hostfactory_revoke_token(hostfactory_revoke_menu_item)
        self._add_hostfactory_options(hostfactory_parser)

        return self

    def _create_hostfactory_parser(self):
        hostfactory_name = 'hostfactory - Manage hosts and Host Factory tokens'
        hostfactory_usage = 'conjur [global options] hostfactory <subcommand> [options] [args]'

        hostfactory_parser = self.resource_subparsers \
            .add_parser('hostfactory',
                        help='Allow creating hosts dynamically and managing Host Factory tokens',
                        description=command_description(hostfactory_name,
                                                        hostfactory_usage),
                        epilog=command_epilog(
                            'conjur hostfactory create token --hostfactoryid my_factory '
                            '--cidr 10.10.1.2/31 '
                            '--duration-days 2\t\t\t '
                            'Creates a token for creating hosts with restrictions\n',
                            command='hostfactory',
                            subcommands=['create']),
                        usage=argparse.SUPPRESS,
                        add_help=False,
                        formatter_class=formatter)
        return hostfactory_parser

    @staticmethod
    def _add_hostfactory_create(hostfactory_subparser: ArgparseWrapper):
        hostfactory_create_name = 'create - Generate Host Factory token for creating hosts ' \
                                  'with restrictions or create a host using the Host Factory'
        hostfactory_create_usage = 'conjur [global options] hostfactory ' \
                                   'create <subcommand> [options] [args]'

        create_cmd = hostfactory_subparser \
            .add_parser(name="create",
                        help='Generate a Host Factory token for creating hosts,' \
                                    'or create a host using a Host Factory token',
                        description=command_description(
                            hostfactory_create_name, hostfactory_create_usage),
                        epilog=command_epilog(
                            'conjur hostfactory create token --hostfactoryid my_factory '
                            '--cidr 10.10.1.2/31 '
                            '--duration-days 2\t\t\t '
                            'Generate a Host Factory token '
                            'for creating hosts with restrictions\t\t'
                            '\nconjur hostfactory create host --id brand-new-token '
                            '--token 82cv6kk040axyffzvmscpf129k81yq1bzkey3gcgfvjc00pfy41h\t\t\t '
                            'Create creates a Host using the HostFactory\t\t',
                            command='create',
                            subcommands=['token', 'host']
                        ),
                        usage=argparse.SUPPRESS,
                        add_help=False,
                        formatter_class=formatter)
        hostfactory_create_subcommand = create_cmd.add_subparsers(title="Subcommand", dest='action')
        hostfactory_create_options = create_cmd.add_argument_group(
            title=title_formatter("Options"))
        hostfactory_create_options.add_argument('-h', '--help', action='help',
                                        help='Display help screen and exit')
        return hostfactory_create_subcommand

    @staticmethod
    def _add_hostfactory_revoke(hostfactory_subparser: ArgparseWrapper):
        hostfactory_revoke_name = 'revoke - Revoke a Host Factory token and disable it immediately'
        hostfactory_revoke_usage = 'conjur [global options] hostfactory ' \
                                   'revoke <subcommand> [options] [args]'

        create_cmd = hostfactory_subparser \
            .add_parser(name="revoke",
                        help='Revoke a Host Factory token and disable it immediately',
                        description=command_description(
                            hostfactory_revoke_name, hostfactory_revoke_usage),
                        epilog=command_epilog(
                            'conjur hostfactory revoke token '
                            '--token "1bcarsc2bqvsxt6cnd74xem8yf15gtma71vp23y315n0z201"'
                            '\t\t\t '
                            'Revoke a Host Factory token and disable it immediately.',
                            command='revoke',
                            subcommands=['token']
                        ),
                        usage=argparse.SUPPRESS,
                        add_help=False,
                        formatter_class=formatter)
        hostfactory_revoke_subcommand = create_cmd.add_subparsers(title="Subcommand", dest='action')
        hostfactory_revoke_options = create_cmd.add_argument_group(
            title=title_formatter("Options"))
        hostfactory_revoke_options.add_argument('-h', '--help', action='help',
                                        help='Display help screen and exit')
        return hostfactory_revoke_subcommand

    @staticmethod
    def _add_hostfactory_revoke_token(menu: ArgparseWrapper):
        hostfactory_revoke_token_name = 'token - Revoke a Host Factory token ' \
                                            'and disable it immediately'
        hostfactory_revoke_token_usage = 'conjur [global options] hostfactory ' \
                                         'revoke token [options] [args]'

        subcommand = menu \
            .add_parser(name="token",
                        help='Revoke a Host Factory token and disable it immediately',
                        description=command_description(
                            hostfactory_revoke_token_name, hostfactory_revoke_token_usage),
                        epilog=command_epilog(
                            'conjur hostfactory revoke token '
                            '--token "1bcarsc2bqvsxt6cnd74xem8yf15gtma71vp23y315n0z201"'
                            '\t\t'
                            'Revoke a Host Factory token and disable it immediately\t\t',
                            command='token'
                        ),
                        usage=argparse.SUPPRESS,
                        add_help=False,
                        formatter_class=formatter)
        # Options
        options = subcommand.add_argument_group(
            title=title_formatter("Options"))
        options.add_argument('-action_type', default='revoke_token', help=argparse.SUPPRESS)
        options.add_argument('-t', '--token', metavar='VALUE', required=True,
                                          help='(Mandatory) Host Factory token to revoke')
        options.add_argument('-h', '--help', action='help',
                                          help='Display help screen and exit')

    @staticmethod
    def _add_hostfactory_create_token(menu: ArgparseWrapper):
        hostfactory_create_token_name = 'token - Generate a Host Factory token ' \
                                         'for creating hosts with restrictions'
        hostfactory_create_token_usage = 'conjur [global options] hostfactory ' \
                                         'create token [options] [args]'

        hostfactory_create_subcommand_parser = menu \
            .add_parser(name="token",
                        help='Generate a Host Factory token for creating hosts with restrictions',
                        description=command_description(
                            hostfactory_create_token_name, hostfactory_create_token_usage),
                        epilog=command_epilog(
                            'conjur hostfactory create token --hostfactoryid my_factory '
                            '--cidr 10.10.1.2/31 '
                            '--duration-days 2\t\t '
                            'Generate a Host Factory token for creating hosts '
                            'with restrictions\t\t',
                            command='token',
                        ),
                        usage=argparse.SUPPRESS,
                        add_help=False,
                        formatter_class=formatter)
        # Options
        create_token = hostfactory_create_subcommand_parser.add_argument_group(
            title=title_formatter("Options"))
        create_token.add_argument('-action_type', default='create_token', help=argparse.SUPPRESS)
        create_token.add_argument('-i', '--hostfactoryid', metavar='VALUE', required=True,
                                  help='(Mandatory) Host Factory ID to work with')
        create_token.add_argument('--cidr', metavar='VALUE',
                                  help='(Optional) CIDR containing all' \
                                        'IP addresses that can use Host Factory '
                                        ' token for creating hosts (for example ' \
                                       '--cidr "10.0.10.0/24,'
                                       '10.0.11.1/32,10.0.20.0/24")')
        create_token.add_argument('-d', '--duration-days', metavar='VALUE', type=int,
                                  help='(Optional) Validity (in days) '
                                       'of Host Factory token.')
        create_token.add_argument('-dh', '--duration-hours', metavar='VALUE', type=int,
                                  help='(Optional) Validity (in hours) '
                                       'of Host Factory token.')
        create_token.add_argument('-m', '--duration-minutes', metavar='VALUE', type=int,
                                  help='(Optional) Validity (in minutes) '
                                       'of Host Factory token.')
        create_token.add_argument('-h', '--help', action='help',
                                  help='Display help screen and exit')

    @staticmethod
    def _add_hostfactory_create_host(menu: ArgparseWrapper):
        name = 'host - Create host using Host Factory'
        usage = 'conjur [global options] hostfactory ' \
                'create host [options] [args]'

        hostfactory_create_subcommand_parser = menu \
            .add_parser(name="host",
                        help='Create host using Host Factory',
                        description=command_description(
                            name, usage),
                        epilog=command_epilog(
                            'conjur hostfactory create host --id brand-new-host '
                            '--token 82cv6kk040axyffzvmscpf129k81yq1bzkey3gcgfvjc00pfy41h\t\t '
                            'Create host using Host Factory\t\t',
                            command='host',
                        ),
                        usage=argparse.SUPPRESS,
                        add_help=False,
                        formatter_class=formatter)
        # Options
        create_host = hostfactory_create_subcommand_parser.add_argument_group(
            title=title_formatter("Options"))
        # hidden argument to be used to distinguish this action
        create_host.add_argument('-action_type', default='create_host', help=argparse.SUPPRESS)
        create_host.add_argument('-i', '--id', metavar='VALUE', required=True,
                                 help='(Mandatory) Identifier of host to be created '
                                      'It will be created within '
                                      'the account of the Host Factory.')
        create_host.add_argument('-t', '--token', metavar='VALUE', required=True,
                                 help='(Mandatory) A Host Factory token must be provided.')
        create_host.add_argument('-h', '--help', action='help',
                                 help='Display help screen and exit')

    @staticmethod
    def _add_hostfactory_options(parser: ArgparseWrapper):
        options = parser.add_argument_group(title=title_formatter("Options"))
        options.add_argument('-h', '--help', action='help',
                             help='Display help screen and exit')
