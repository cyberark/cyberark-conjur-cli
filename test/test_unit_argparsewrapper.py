# Builtins
import io
import unittest
from contextlib import redirect_stderr, redirect_stdout

# Internals
from unittest.mock import patch

from conjur.wrapper.argparse_wrapper import ArgparseWrapper

class ArgparserWrapperTest(unittest.TestCase):
    capture_stream = io.StringIO()

    arg_parse = ArgparseWrapper(description='Conjur CLI', add_help=False)

    subparser = arg_parse.add_subparsers(dest='resource', title="Commands")
    variable_parser = subparser.add_parser('testCommand',
        help='Manage testCommand')
    variable_subparsers = variable_parser.add_subparsers(dest='action')
    variable_subparsers.add_parser('subCommand')

    '''
    Returns correct error message
    '''
    def test_error_prints_help_and_exits(self):
        with self.assertRaises(SystemExit):
            with redirect_stderr(self.capture_stream):
                self.arg_parse.error("--unknown")

        self.assertRegex(self.capture_stream.getvalue(), "Error unrecognized arguments:")

    '''
    Returns updated namespace with provided args
    Command: conjur testCommand
    '''
    def test_no_flag_returns_namespace(self):
        with redirect_stderr(self.capture_stream):
            output = self.arg_parse.parse_args(['testCommand'])

        self.assertEquals("Namespace(resource='testCommand', action=None)", str(output))

    '''
    Returns namespace when not given any flags and does not error
    Command: conjur
    '''
    def test_no_flag_returns_prints_command_help(self):
        with redirect_stderr(self.capture_stream):
            output = self.arg_parse.parse_args([])

        self.assertIn("Namespace(resource=None)", str(output))

    '''
    Unknown flag without an action should print error and exit 1
    Command: conjur --unknown
    '''
    def test_no_action_returns_prints_error(self):
        with self.assertRaises(SystemExit):
            with redirect_stderr(self.capture_stream):
                self.arg_parse.parse_args(["--unknown"])

        self.assertRegex(self.capture_stream.getvalue(), "Error unrecognized arguments: --unknown")

    '''
    Unknown flag with an action should print error and exit 1
    Command: Conjur testCommand --unknown
    '''
    def test_action_with_unknown_flag_returns_prints_error(self):
        with self.assertRaises(SystemExit):
            with redirect_stderr(self.capture_stream):
                with patch.object(self.arg_parse, '_get_resource_namespace', return_value=None):
                    self.arg_parse.parse_args(["testCommand", "--unknown"])

        self.assertRegex(self.capture_stream.getvalue(), "Error unrecognized arguments: --unknown")

    '''
    Unknown subCommand should print error and exit 1
    Command: conjur testCommand unknown
    '''
    def test_action_with_unknown_subcommand_returns_prints_error(self):
        with self.assertRaises(SystemExit):
            with redirect_stderr(self.capture_stream):
                self.arg_parse.parse_args(["testCommand", "unknown"])

        self.assertRegex(self.capture_stream.getvalue(), "(choose from 'subCommand')")

    '''
    Valid input should pass and return correct namespace object
    Command: conjur testCommand subCommand
    '''
    def test_correct_arg_should_pass(self):
        output = self.arg_parse.parse_args(["testCommand", "subCommand"])

        self.assertEquals(str(output), "Namespace(resource='testCommand', action='subCommand')")

    def test_no_resource_namespace(self):
        with patch.object(self.arg_parse, '_get_resource_namespace', return_value=None):
            self.assertEquals(self.arg_parse._get_resource_namespace('will return None'), None)

    '''
    Subcommand error will write and exit
    '''
    def test_subcommand_prints_and_exits(self):
        with self.assertRaises(SystemExit):
            with redirect_stdout(self.capture_stream):
                self.arg_parse._subcommand_error("oops!", "Usage:")
            self.assertRegex(self.capture_stream.getvalue(), "Error oops!")
