"""
This Module holds all the utils needed for the ArgParseBuilder
"""

import argparse
import time


def formatter(prog):
    """
    This method format the text of the different parsers.
    """
    return argparse.RawTextHelpFormatter(prog,
                                         max_help_position=100,
                                         width=100)


def header(*args):
    """
    This method builds the header for the main screen.
    """
    return '''Usage:
  {}'''.format(*args)


def command_description(example, usage):
    """
    This method builds the header for the main screen.
    """
    return '''

Name:
  {}

Usage:
  {}'''.format(example, usage)


def main_epilog():
    """
    This method builds the footer for the main help screen.
    """
    return '''
To get help on a specific command, see `conjur <command> -h | --help`

To start using Conjur with your environment, you must first initialize the configuration. See `conjur init -h` for more information.
'''


def command_epilog(example, command=None, subcommands=None):
    """
    This method builds the footer for each command help screen.
    """
    refer_to_help = "See more details in each subcommand's help:"
    if subcommands:
        res = ""
        for subcommand in subcommands:
            res += "conjur " + command + " " + subcommand + " -h\n"
        return f'''{refer_to_help}\n{res}'''
    return f'''Examples:
    {example}'''


def title_formatter(title):
    """
    This method builds a reusable title for each argument section
    """
    return "\n{}".format(title)


def conjur_copyright():
    """
    This method builds the copyright description
    """
    return f'''
Copyright (c) {time.strftime("%Y")} CyberArk Software Ltd. All rights reserved.
<www.cyberark.com>
'''
