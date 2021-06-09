"""
Module For the HostParser
"""
import argparse
from conjur.argument_parser.parser_utils import command_description, command_epilog, formatter, \
    title_formatter


# pylint: disable=too-few-public-methods
class HostParser:
    """Partial class of the ArgParseBuilder.
    This class add the Host subparser to the ArgParseBuilder parser."""

    def __init__(self):
        self.resource_subparsers = None  # here to reduce warnings on resource_subparsers not exist
        raise NotImplementedError("this is partial class of ArgParseBuilder")

    def add_host_parser(self):
        """
        Method adds host parser functionality to parser
        """
        host_subparser = self._create_host_parser()
        host_subparsers = host_subparser \
            .add_subparsers(dest='action', title=title_formatter("Subcommands"))
        self._host_rotate_api_key_parser(host_subparsers)
        self._add_host_options(host_subparser)

        return self

    def _create_host_parser(self) -> argparse.ArgumentParser :
        host_name = 'host - Manage hosts'
        host_usage = 'conjur [global options] host <subcommand> [options] [args]'
        host_subparser = self.resource_subparsers \
            .add_parser('host',
                        help='Manage hosts',
                        description=command_description(host_name,
                                                        host_usage),
                        epilog=command_epilog(
                            'conjur host rotate-api-key -i my_apps/myVM\t\t'
                            'Rotates the API key for host myVM',
                            command='host',
                            subcommands=['change-password']),
                        usage=argparse.SUPPRESS,
                        add_help=False,
                        formatter_class=formatter)

        return host_subparser

    @staticmethod
    def _host_rotate_api_key_parser(sub_parser:argparse.ArgumentParser):
        host_rotate_api_key_name = 'rotate-api-key - Rotate a host\'s API key'
        host_rotate_api_key_usage = 'conjur [global options] host rotate-api-key [options] [args]'
        host_rotate_api_key_parser = \
            sub_parser.add_parser('rotate-api-key',
                                  help='Rotate a host\'s API key',
                                  description=command_description(
                                      host_rotate_api_key_name,
                                      host_rotate_api_key_usage),
                                  epilog=command_epilog(
                                      'conjur host rotate-api-key -i my_apps/myVM\t\t'
                                      'Rotates the API key for host myVM'),
                                  usage=argparse.SUPPRESS,
                                  add_help=False,
                                  formatter_class=formatter)
        host_rotate_api_key = \
            host_rotate_api_key_parser.add_argument_group(title=title_formatter("Options"))
        host_rotate_api_key.add_argument('-i', '--id',
                                         help='Provide host identifier for which '
                                              'you want to rotate the API key')
        host_rotate_api_key.add_argument('-h', '--help', action='help',
                                         help='Display help screen and exit')

    @staticmethod
    def _add_host_options(host_subparser:argparse.ArgumentParser):
        host_options = host_subparser.add_argument_group(title=title_formatter("Options"))
        host_options.add_argument('-h', '--help', action='help'
                                  , help='Display help screen and exit')
