# -*- coding: utf-8 -*-

"""
Argparse_wrapper module

This module is a wrapper for the third-party argparse module used to parse
commandline arguments. The module controls the types of errors and help screens
we return according to the types of inputs received.
"""

# Builtins
import sys

# Third party
import argparse

class ArgparseWrapper(argparse.ArgumentParser):
    """
    Wrapper to override default behavior of the argparse module.
    """

    ARG_ERROR_FORMAT = 'unrecognized arguments: %s'

    def error(self, message):
        """
        This method handles the errors that originate from incorrect
        commands.
        """
        sys.stderr.write(f"Error {message}\n")
        self.print_help()
        sys.exit(1)

    @staticmethod
    def _subcommand_error(message, help_screen):
        """
        This method handles the errors that originate from incorrect
        subcommands/flags.
        """
        sys.stderr.write(f"Error {message}\n")
        sys.stderr.write(f"{help_screen}\n")
        sys.exit(1)

    # pylint: disable=arguments-differ
    def parse_args(self, args=None, namespace=None, resource=None):
        args, arg_flags = self.parse_known_args(args, namespace)
        resource = args.resource if args else None
        if arg_flags:
            err_msg = (self.ARG_ERROR_FORMAT % ' '.join(arg_flags))
            if not resource:
                self.error(err_msg)

            # pylint: disable=protected-access
            # Get the namespace of the particular resource
            resource_namespace = self._subparsers._actions[0].choices.get(resource)
            if not resource_namespace:
                self.error(err_msg)
            # Return the help for the specific resource
            self._subcommand_error(err_msg, resource_namespace.format_help())

        return args
