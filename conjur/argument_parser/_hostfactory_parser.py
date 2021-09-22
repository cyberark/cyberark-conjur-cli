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
        hostfacotry_parser = self._create_hostfactory_parser()
        hostfacotry_subparser = hostfacotry_parser.add_subparsers(title="Subcommand", dest='action')

        self._add_hostfactory_get(hostfacotry_subparser)
        self._add_hostfactory_set(hostfacotry_subparser)
        self._add_hostfactory_options(hostfactory_parser)

        return self

    def _create_hostfacotry_parser(self):
        hostfactory_name = 'hostfactory - Manage host factories'
        hostfactory_usage = 'conjur [global options] hostfactory <subcommand> [options] [args]'

        hostfactory_parser = self.resource_subparsers \
            .add_parser('hostfactory',
                        help='Manage host factories',
                        description=command_description(hostfactory_name,
                                                        hostfactory_usage),
                        epilog=command_epilog(
                            'conjur hostfactory hosts \t\t\t'
                            'Operations on hosts\n'
                            'conjur hostfactory tokens \t\t'
                            'Operations on tokens\n',
                            command='hostfactory',
                            subcommands=['hosts', 'tokens']),
                        usage=argparse.SUPPRESS,
                        add_help=False,
                        formatter_class=formatter)
        return hostfactory_parser

    @staticmethod
    def _add_hostfacotry_tokens(hostfactory_subparser: ArgparseWrapper):
        hostfactory_tokens_name = 'tokens - Operations on tokens'
        hostfactory_tokens_usage = 'conjur [global options] hostfactory tokens [options] [args]'

        hostfactory_tokens_subcommand_parser = hostfactory_subparser \
            .add_parser(name="tokens",
                        help='Operations on tokens',
                        description=command_description(
                            hostfactory_tokens_name, hostfactory_tokens_usage),
                        epilog=command_epilog(
                            'conjur hostfactory create token --hostfactoryid my_factory --cidr 10.10.1.2/31 '
                            '--duration-days 2\t\t\t '
                            'Create token/s for hosts with restrictions\n'
                            '    conjur hostfactory revoke token --token <TOKEN>,<TOKEN2>\t\t'
                            'Revoke (delete) one or more tokens\n'),
                        usage=argparse.SUPPRESS,
                        add_help=False,
                        formatter_class=formatter)
        hostfactory_tokens_options = hostfactory_tokens_subcommand_parser.add_argument_group(
            title=title_formatter("Options"))
        hostfactory_tokens_options.add_argument('-i', '--id', dest='identifier', metavar='VALUE',
                                                help='Provide hostfactory identifier', nargs='*',
                                                required=True)
        hostfactory_tokens_options.add_argument('--hostfactoryid', '-i', metavar='VALUE',
                                                help='(Mandatory) the ID of the host factory you would like to work '
                                                     'with. This parameter is mandatory, so we need to prompt a '
                                                     'message/error if it is missing.')
        hostfactory_tokens_options.add_argument('--cidr', metavar='VALUE',
                                                help='(Optional) the CIDR address that contains all IPs that can '
                                                     'use this token to create hosts. We want to allow multiple cidrs, '
                                                     'separated by commas (for example --cidr "10.0.10.0/24,'
                                                     '10.0.11.1/32,10.0.20.0/24")')
        hostfactory_tokens_options.add_argument('-d', '--duration-days', metavar='VALUE',
                                                help='(Optional) the number of days the token will be valid.')
        hostfactory_tokens_options.add_argument('-H', '--duration-hours', metavar='VALUE',
                                                help='(Optional) the number of hours the token will be valid.')
        hostfactory_tokens_options.add_argument('-m', '--duration-minutes', metavar='VALUE',
                                                help='(Optional) the number of minutes the token will be valid.')
        hostfactory_tokens_options.add_argument('-c', '--count', metavar='VALUE',
                                                help='(Optional) the number of times the token can be used.')
        hostfactory_tokens_options.add_argument('-h', '--help', action='help',
                                                help='Display help screen and exit')

    @staticmethod
    def _add_hostfacotry_hosts(hostfactory_subparser: ArgparseWrapper):
        hostfactory_hosts_name = 'hosts - Operations on hosts'
        hostfactory_hosts_usage = 'conjur [global options] hostfactory hosts [options] [args]'
        hostfactory_hosts_subcommand_parser = hostfactory_subparser \
            .add_parser(name="create",
                        help='Use a token to create a host',
                        description=command_description(
                            hostfactory_hosts_name, hostfactory_hosts_usage),
                        epilog=command_epilog(
                            'conjur hostfactory create host -i my_host -t my_token\t'
                            'Create a host named \'my_host\' using the token \'my_token\' \n'),
                        usage=argparse.SUPPRESS,
                        add_help=False,
                        formatter_class=formatter)
        hostfactory_hosts_options = hostfactory_hosts_subcommand_parser.add_argument_group(
            title=title_formatter("Options"))

        hostfactory_hosts_options.add_argument('-i', '--id', dest='identifier', metavar='VALUE',
                                             help='(Mandatory) the host ID you wish to create. No need to mention the '
                                                  'type of entity (host).', required=True)
        hostfactory_hosts_options.add_argument('-t', '--token', metavar='VALUE',
                                             help=' (Mandatory) the token itself',
                                             required=True)
        hostfactory_hosts_options.add_argument('-h', '--help', action='help',
                                             help='Display help screen and exit')

    @staticmethod
    def _add_hostfacotry_options(hostfactory_parser: ArgparseWrapper):
        policy_options = hostfactory_parser.add_argument_group(title=title_formatter("Options"))
        policy_options.add_argument('-h', '--help', action='help',
                                    help='Display help screen and exit')
