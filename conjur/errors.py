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

class OperationNotCompletedSuccessfullyException(Exception):
    """
    Exception for when an operation was not completed successfully
    and CLI is left in instable state
    """

class MissingRequiredParameterException(Exception):
    """ Exception for when user does not input a required paramter """
