"""
Module For the ListParser
"""
import argparse
from conjur.argument_parser.parser_utils import command_description, command_epilog, formatter, \
    title_formatter
from conjur.wrapper.argparse_wrapper import ArgparseWrapper


# pylint: disable=too-few-public-methods
class ListParser:
    """Partial class of the ArgParseBuilder.
    This class add the List subparser to the ArgParseBuilder parser."""

    def __init__(self):
        self.resource_subparsers = None  # here to reduce warnings on resource_subparsers not exist
        raise NotImplementedError("this is partial class of ArgParseBuilder")

    def add_list_parser(self):
        """
        Method adds list parser functionality to parser
        """
        list_subparser = self._create_list_parser()
        self._add_list_options(list_subparser)

        return self

    def _create_list_parser(self):
        list_name = 'list - List resources or information about resources within an' \
                    ' organization\'s account'
        list_usage = 'conjur [global options] list [options] [args]'

        list_subparser = self.resource_subparsers \
            .add_parser('list',
                        help='List all available resources belonging to this account',
                        description=command_description(list_name,
                                                        list_usage),
                        epilog=command_epilog(
                            'conjur list --kind=variable\t\t\t\t\t\t'
                            'Filters list by variable\n'
                            '    conjur list --limit=20\t\t\t\t\t\t'
                            'Lists first 20 resources\n'
                            '    conjur list --offset=4\t\t\t\t\t\t'
                            'Skips the first 4 resources in the list and displays all the rest\n'
                            '    conjur list --role=myorg:user:superuser\t\t\t\t'
                            'Shows resources that superuser is entitled to see\n'
                            '    conjur list --search=superuser\t\t\t\t\t'
                            'Searches for resources with superuser\n'
                            '    conjur list --members-of group:\'aws-apps\'\t\t\t\t'
                            'Returns all direct members of the \'aws-apps\' group\n'
                            '    conjur list'
                            ' --permitted-roles \'azure-secret\' --privileges execute\t'
                            'Returns the roles that have the \'execute\' privilege on the '
                            '\'azure-secret\' resource. Note: If more than one resource in Conjur '
                            'uses the same ID, you must specify full resource identifier\n'
                        ),
                        usage=argparse.SUPPRESS,
                        add_help=False,
                        formatter_class=formatter)

        return list_subparser

    @staticmethod
    def _add_list_options(list_subparser: ArgparseWrapper):
        list_options = list_subparser.add_argument_group(title=title_formatter("Options"))
        list_options.add_argument('-i', '--inspect',
                                  action='store_true', dest='inspect',
                                  help='Optional- list the metadata for resources')
        list_options.add_argument('-k', '--kind',
                                  action='store', metavar='VALUE', dest='kind',
                                  help='Optional- filter resources by specified kind '
                                       '(user | host | layer | group '
                                       '| policy | variable | webservice)')
        list_options.add_argument('-l', '--limit',
                                  action='store', metavar='VALUE', dest='limit',
                                  help='Optional- limit list of resources to specified number')
        list_options.add_argument('-o', '--offset',
                                  action='store', metavar='VALUE', dest='offset',
                                  help='Optional- skip specified number of resources')
        list_options.add_argument('-r', '--role',
                                  action='store', metavar='VALUE', dest='role',
                                  help='Optional- retrieve list of resources that specified role '
                                       'is entitled to see (VALUE must include resource\'s full '
                                       'identifier. See example below)')
        list_options.add_argument('-s', '--search',
                                  action='store', metavar='VALUE', dest='search',
                                  help='Optional- search for resources based on specified query')
        list_options.add_argument('-m', '--members-of',
                                  action='store', metavar='VALUE', dest='members_of',
                                  help='Optional - retrieve list of direct members of a specified '
                                       'group/layer. Note: If more than one resource in Conjur uses'
                                       ' the same ID, VALUE must specify full resource identifier')
        list_options.add_argument('-pr', '--permitted-roles',
                                  action='store', metavar='VALUE',
                                  dest='permitted_roles_identifier',
                                  help='Optional - retrieve roles that have the specified '
                                       'privilege on the resource. Use \'--privilege\' option to '
                                       'specify privilege. Note: If more than one resource in '
                                       'Conjur uses the same ID, specify full resource identifier')
        list_options.add_argument('-p', '--privilege',
                                  action='store', metavar='VALUE', dest='privilege',
                                  help='Use together with \'--permitted-roles\' option - specify '
                                       'the privilege you are querying')
        list_options.add_argument('-h', '--help', action='help',
                                  help='Display help screen and exit')
