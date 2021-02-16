# -*- coding: utf-8 -*-

"""
Error module

This module holds all CLI-specific errors
"""

class InvalidOperationException(Exception):
    """ Exception for invalid user operations """

class InvalidPasswordComplexityException(Exception):
    """
    Exception for when the user supplies a not complex enough password when
    attempting to change their password
    """

class OperationNotCompletedException(Exception):
    """
    Exception for when an operation was not completed successfully
    and CLI is left in instable state
    """
    def __init__(self, cause="", solution=""):
        self.message = "Error: Failed to run command to completion. " + cause + solution
        super().__init__(self.message)

class MissingRequiredParameterException(Exception):
    """ Exception for when user does not input a required parameter """

class InvalidFormatException(Exception):
    """
    Exception for when user provides input that is not in the proper format
    (policy yml for example)
    """
    def __init__(self, message):
        self.message = message
        super().__init__("Failed to execute command. Reason: " + self.message)
