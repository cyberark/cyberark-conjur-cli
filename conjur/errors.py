# -*- coding: utf-8 -*-

"""
Error module

This module holds Conjur CLI/SDK-specific errors for this project
"""
from conjur.errors_messages import MISMATCH_HOSTNAME_MESSAGE

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
    def __init__(self, message="Error: Failed to run command to completion."):
        self.message = message
        super().__init__(self.message)

class InvalidOperationException(Exception):
    """ Exception for when the operation performed was invalid """
    def __init__(self, cause="", solution=""):
        self.message = f"Error: Invalid operation. Reason: {cause} {solution}"
        super().__init__(self.message)

class MissingRequiredParameterException(Exception):
    """ Exception for when user does not input a required parameter """

class InvalidFormatException(Exception):
    """
    Exception for when user provides input that is not in the proper format
    (policy yml for example)
    """
    def __init__(self, message=""):
        self.message = message
        super().__init__("Failed to execute command. Reason: " + self.message)

class CertificateVerificationException(Exception):
    """
    Exception for when the user runs the Client in conflicting modes. For example,
    initializing the client using --insecure but running a follow-up command in secure mode
    (without --insecure)
    """
    def __init__(self, cause="", solution=""):
        self.message = f"{cause} {solution}"
        super().__init__(self.message)

# pylint: disable=line-too-long
class CertificateHostnameMismatchException(Exception):
    """ Exception for when machine's hostname does not match the hostname on the certificate """
    def __init__(self):
        self.message = MISMATCH_HOSTNAME_MESSAGE
        super().__init__(self.message)
