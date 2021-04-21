"""
Module For the VariableParser
"""
import argparse
from conjur.argument_parser.parser_utils import command_description, command_epilog, formatter, title_formatter


class VariableParser:
    """Partial class of the ArgParseBuilder.
    This class add the Variable subparser to the ArgParseBuilder parser."""

    def __init__(self):
        raise NotImplementedError("this is partial class of ArgParseBuilder")

    def add_variable_parser(self):
        """
        Method adds variable parser functionality to parser
        """
        variable_parser = self._create_variable_parser()
        variable_subparser = variable_parser.add_subparsers(title="Subcommand", dest='action')

        self._add_variable_get(variable_subparser)
        self._add_variable_set(variable_subparser)
        self._add_variable_options(variable_parser)

        return self

    def _create_variable_parser(self):
        variable_name = 'variable - Manage variables'
        variable_usage = 'conjur [global options] variable <subcommand> [options] [args]'

        variable_parser = self.resource_subparsers.add_parser('variable',
                                                              help='Manage variables',
                                                              description=command_description(variable_name,
                                                                                              variable_usage),
                                                              epilog=command_epilog(
                                                                  'conjur variable get -i secrets/mysecret\t\t\t'
                                                                  'Gets the value of variable secrets/mysecret\n'
                                                                  '    conjur variable get -i secrets/mysecret "secrets/my secret"\t'
                                                                  'Gets the values of variables secrets/mysecret and secrets/my secret\n'
                                                                  '    conjur variable set -i secrets/mysecret -v my_secret_value\t'
                                                                  'Sets the value of variable secrets/mysecret to my_secret_value\n',
                                                                  command='variable',
                                                                  subcommands=['get', 'set']),
                                                              usage=argparse.SUPPRESS,
                                                              add_help=False,
                                                              formatter_class=formatter)
        return variable_parser

    @staticmethod
    def _add_variable_get(variable_subparser):
        variable_get_name = 'get - Get the value of a variable'
        variable_get_usage = 'conjur [global options] variable get [options] [args]'

        variable_get_subcommand_parser = variable_subparser.add_parser(name="get",
                                                                       help='Get the value of one or more variables',
                                                                       description=command_description(
                                                                           variable_get_name, variable_get_usage),
                                                                       epilog=command_epilog(
                                                                           'conjur variable get -i secrets/mysecret\t\t\t'
                                                                           'Gets the most recent value of variable secrets/mysecret\n'
                                                                           '    conjur variable get -i secrets/mysecret "secrets/my secret"\t'
                                                                           'Gets the values of variables secrets/mysecret and secrets/my secret\n'
                                                                           '    conjur variable get -i secrets/mysecret --version 2\t\t'
                                                                           'Gets the second version of variable secrets/mysecret\n'),
                                                                       usage=argparse.SUPPRESS,
                                                                       add_help=False,
                                                                       formatter_class=formatter)
        variable_get_options = variable_get_subcommand_parser.add_argument_group(title=title_formatter("Options"))
        variable_get_options.add_argument('-i', '--id', dest='identifier', metavar='VALUE',
                                          help='Provide variable identifier', nargs='*', required=True)
        variable_get_options.add_argument('--version', metavar='VALUE',
                                          help='Optional- specify desired version of variable value')
        variable_get_options.add_argument('-h', '--help', action='help', help='Display help screen and exit')

    @staticmethod
    def _add_variable_set(variable_subparser):
        variable_set_name = 'set - Set the value of a variable'
        variable_set_usage = 'conjur [global options] variable set [options] [args]'
        variable_set_subcommand_parser = variable_subparser.add_parser(name="set",
                                                                       help='Set the value of a variable',
                                                                       description=command_description(
                                                                           variable_set_name, variable_set_usage),
                                                                       epilog=command_epilog(
                                                                           'conjur variable set -i secrets/mysecret -v my_secret_value\t'
                                                                           'Sets the value of variable secrets/mysecret to my_secret_value\n'),
                                                                       usage=argparse.SUPPRESS,
                                                                       add_help=False,
                                                                       formatter_class=formatter)
        variable_set_options = variable_set_subcommand_parser.add_argument_group(title=title_formatter("Options"))

        variable_set_options.add_argument('-i', '--id', dest='identifier', metavar='VALUE',
                                          help='Provide variable identifier', required=True)
        variable_set_options.add_argument('-v', '--value', metavar='VALUE',
                                          help='Set the value of the specified variable', required=True)
        variable_set_options.add_argument('-h', '--help', action='help', help='Display help screen and exit')

    @staticmethod
    def _add_variable_options(variable_parser):
        policy_options = variable_parser.add_argument_group(title=title_formatter("Options"))
        policy_options.add_argument('-h', '--help', action='help', help='Display help screen and exit')
