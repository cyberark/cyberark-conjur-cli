"""
Module For the InitParser
"""
import argparse
from conjur.argument_parser.parser_utils import command_description, command_epilog, formatter, title_formatter


class InitParser:
    """Partial class of the ArgParseBuilder.
    This class add the Init subparser to the ArgParseBuilder parser."""

    def __init__(self):
        raise NotImplementedError("this is partial class of ArgParseBuilder")

    def add_init_parser(self):
        """
        Method adds init parser functionality to parser
        """
        init_subparser = self._create_init_parser()
        self._add_init_options(init_subparser)
        return self

    def _create_init_parser(self):
        init_name = 'init - Initialize Conjur configuration'
        input_usage = 'conjur [global options] init [options] [args]'

        init_subparser = self.resource_subparsers.add_parser('init',
                                                             help='Initialize Conjur configuration',
                                                             description=command_description(init_name,
                                                                                             input_usage),
                                                             epilog=command_epilog(
                                                                 'conjur init -a my_org -u https://conjur-server\t'
                                                                 'Initializes Conjur configuration and writes to file (.conjurrc)'),
                                                             usage=argparse.SUPPRESS,
                                                             add_help=False,
                                                             formatter_class=formatter)
        return init_subparser

    @staticmethod
    def _add_init_options(sub_parser):
        init_options = sub_parser.add_argument_group(title=title_formatter("Options"))
        init_options.add_argument('-u', '--url', metavar='VALUE',
                                  action='store', dest='url',
                                  help='Provide URL of Conjur server')
        init_options.add_argument('-a', '--account', metavar='VALUE',
                                  action='store', dest='name',
                                  help='Provide Conjur account name. ' \
                                       'Optional for Conjur Enterprise - overrides the value on the Conjur Enterprise server')
        init_options.add_argument('-c', '--certificate', metavar='VALUE',
                                  action='store', dest='certificate',
                                  help='Optional- provide path to Conjur SSL certificate ' \
                                       '(obtained from Conjur server unless provided by this option)')
        init_options.add_argument('--force',
                                  action='store_true',
                                  dest='force', help='Optional- force overwrite of existing files')
        init_options.add_argument('-h', '--help', action='help', help='Display help screen and exit')
