import sys
import argparse

from .client import Client

from .version import __version__


class Cli(object):
    def run(self, *args, **kwargs):
        parser = argparse.ArgumentParser(description='Conjur Python3 API CLI')

        resource_subparsers = parser.add_subparsers(dest='resource')

        variable_parser = resource_subparsers.add_parser('variable',
            help='Perform variable-related actions . See "variable -help" for more options')

        variable_subparsers = variable_parser.add_subparsers(dest='action')
        get_variable_parser = variable_subparsers.add_parser('get',
            help='Get the value of a variable')
        set_variable_parser = variable_subparsers.add_parser('set',
            help='Set the value of a variable')

        get_variable_parser.add_argument('variable_id',
            help='ID of the variable')

        set_variable_parser.add_argument('variable_id',
            help='ID of the variable')
        set_variable_parser.add_argument('value',
            help='New value of the variable')


        parser.add_argument('-v', '--version', action='version',
            version='%(prog)s v' + __version__)

        parser.add_argument('-d', '--debug',
            help='Enable debugging output',
            action='store_true')

        parser.add_argument('--verbose',
            help='Enable verbose debugging output',
            action='store_true')


        resource, args = self._parse_args(parser)

        # We don't have a good "debug" vs "verbose" separation right now
        if args.verbose is True:
            args.debug = True

        self._run_client_action(resource, args)

    def _run_client_action(self, resource, args):
        client = Client(debug=args.debug)

        if resource == 'variable':
            variable_id = args.variable_id
            if args.action == 'get':
                variable_value = client.get(variable_id)
                print(variable_value.decode('utf-8'), end='')
            else:
                client.set(variable_id, args.value)

    def _parse_args(self, parser):
        args = parser.parse_args()

        if not args.resource:
            parser.print_help()

        return args.resource, args

    @staticmethod
    def launch():
        return Cli().run()

if __name__ == '__main__':
    Cli.launch()
