import argparse
from conjur.argument_parser.parser_utils import command_description, command_epilog, formatter, title_formatter


class ListParser:
    """Partial class of the ArgParseBuilder. holds the public function add_list_parser."""

    def __init__(self):
        raise NotImplementedError("this is partial class of ArgParseBuilder")

    def add_list_parser(self):
        """
        Method adds list parser functionality to parser
        """
        list_subparser = self._init_list_parser()
        ListParser.add_list_options(list_subparser)

        return self

    def _init_list_parser(self):
        list_name = 'list - List resources within an organization\'s account'
        list_usage = 'conjur [global options] list [options] [args]'

        list_subparser = self.resource_subparsers.add_parser('list',
                                                             help='List all available resources belonging to this account',
                                                             description=command_description(list_name,
                                                                                             list_usage),
                                                             epilog=command_epilog(
                                                                 'conjur list --kind=variable\t\t\t'
                                                                 'Filters list by variable\n'
                                                                 '    conjur list --limit=20\t\t\t'
                                                                 'Lists first 20 resources\n'
                                                                 '    conjur list --offset=4\t\t\t'
                                                                 'Skips the first 4 resources in the list and displays all the rest\n'
                                                                 '    conjur list --role=myorg:user:superuser\t'
                                                                 'Shows resources that superuser is entitled to see\n'
                                                                 '    conjur list --search=superuser\t\t'
                                                                 'Searches for resources with superuser\n'),
                                                             usage=argparse.SUPPRESS,
                                                             add_help=False,
                                                             formatter_class=formatter)

        return list_subparser

    @staticmethod
    def add_list_options(list_subparser):
        list_options = list_subparser.add_argument_group(title=title_formatter("Options"))
        list_options.add_argument('-i', '--inspect',
                                  action='store_true', dest='inspect',
                                  help='Optional- list the metadata for resources')
        list_options.add_argument('-k', '--kind',
                                  action='store', metavar='VALUE', dest='kind',
                                  help='Optional- filter resources by specified kind (user | host | layer | group | policy | variable | webservice)')
        list_options.add_argument('-l', '--limit',
                                  action='store', metavar='VALUE', dest='limit',
                                  help='Optional- limit list of resources to specified number')
        list_options.add_argument('-o', '--offset',
                                  action='store', metavar='VALUE', dest='offset',
                                  help='Optional- skip specified number of resources')
        list_options.add_argument('-r', '--role',
                                  action='store', metavar='VALUE', dest='role',
                                  help='Optional- retrieve list of resources that specified role is entitled to see (must specify role’s full ID)')
        list_options.add_argument('-s', '--search',
                                  action='store', metavar='VALUE', dest='search',
                                  help='Optional- search for resources based on specified query')
        list_options.add_argument('-h', '--help', action='help', help='Display help screen and exit')
