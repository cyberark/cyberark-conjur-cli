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
        self._add_hostfactory_create_token(hostfactory_create_menu_item)
        self._add_hostfactory_create_host(hostfactory_create_menu_item)
        self._add_hostfactory_options(hostfactory_parser)

        return self

    def _create_hostfactory_parser(self):
        hostfactory_name = 'hostfactory - Manage hosts and tokens'
        hostfactory_usage = 'conjur [global options] hostfactory <subcommand> [options] [args]'

        hostfactory_parser = self.resource_subparsers \
            .add_parser('hostfactory',
                        help='Allows creating hosts dynamically and manage hostfactory tokens',
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
        hostfactory_create_name = 'create - Create token for creating hosts ' \
                                  'with restrictions or creates a Host using the Host Factory'
        hostfactory_create_usage = 'conjur [global options] hostfactory ' \
                                   'create <subcommand> [options] [args]'

        create_cmd = hostfactory_subparser \
            .add_parser(name="create",
                        help='Creates a token for creating hosts or creates a host using a token',
                        description=command_description(
                            hostfactory_create_name, hostfactory_create_usage),
                        epilog=command_epilog(
                            'conjur hostfactory create token --hostfactoryid my_factory '
                            '--cidr 10.10.1.2/31 '
                            '--duration-days 2\t\t\t '
                            'Create creates a token '
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
        hostfactory_create = create_cmd.add_argument_group(
            title=title_formatter("Options"))
        hostfactory_create.add_argument('-h', '--help', action='help',
                                        help='Display help screen and exit')
        return create_cmd.add_subparsers(title="Subcommand", dest='action')

    @staticmethod
    def _add_hostfactory_create_token(menu: ArgparseWrapper):
        hostfactory_create_token_name = 'token - Creates a token for creating hosts ' \
                                        'with restrictions'
        hostfactory_create_token_usage = 'conjur [global options] hostfactory ' \
                                         'create token [options] [args]'

        hostfactory_create_subcommand_parser = menu \
            .add_parser(name="token",
                        help='Creates a token for creating hosts with restrictions',
                        description=command_description(
                            hostfactory_create_token_name, hostfactory_create_token_usage),
                        epilog=command_epilog(
                            'conjur hostfactory create token --hostfactoryid my_factory '
                            '--cidr 10.10.1.2/31 '
                            '--duration-days 2\t\t '
                            'Creates a token for creating hosts with restrictions\t\t',
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
                                  help='(Mandatory) the ID of the host factory.')
        create_token.add_argument('--cidr', metavar='VALUE',
                                  help='(Optional) the CIDR address that contains '
                                       'all IPs that can use this token to create hosts. '
                                       'You can specify multiple cidr, '
                                       'separated by commas (for example '
                                       '--cidr "10.0.10.0/24,'
                                       '10.0.11.1/32,10.0.20.0/24")')
        create_token.add_argument('-d', '--duration-days', metavar='VALUE', type=int,
                                  help='(Optional) the number of days the token will be valid.')
        create_token.add_argument('-H', '--duration-hours', metavar='VALUE', type=int,
                                  help='(Optional) the number of hours the token will be valid.')
        create_token.add_argument('-m', '--duration-minutes', metavar='VALUE', type=int,
                                  help='(Optional) the number of minutes the token will be valid.')
        create_token.add_argument('-h', '--help', action='help',
                                  help='Display help screen and exit')

    @staticmethod
    def _add_hostfactory_create_host(menu: ArgparseWrapper):
        name = 'host - Creates a Host using the Host Factory'
        usage = 'conjur [global options] hostfactory ' \
                'create host [options] [args]'

        hostfactory_create_subcommand_parser = menu \
            .add_parser(name="host",
                        help='Creates a Host using the Host Factory',
                        description=command_description(
                            name, usage),
                        epilog=command_epilog(
                            'conjur hostfactory create host --id brand-new-host '
                            '--token 82cv6kk040axyffzvmscpf129k81yq1bzkey3gcgfvjc00pfy41h\t\t '
                            'Creates a Host using the HostFactory\t\t',
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
                                 help='(Mandatory) Identifier of the Host to be created. '
                                      'It will be created within '
                                      'the account of the Host Factory.')
        create_host.add_argument('-t', '--token', metavar='VALUE', required=True,
                                 help='(Mandatory) A Host Factory Token must be provided.')
        create_host.add_argument('-h', '--help', action='help',
                                 help='Display help screen and exit')

    @staticmethod
    def _add_hostfactory_options(parser: ArgparseWrapper):
        options = parser.add_argument_group(title=title_formatter("Options"))
        options.add_argument('-h', '--help', action='help',
                             help='Display help screen and exit')
