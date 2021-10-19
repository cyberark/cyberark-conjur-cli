# -*- coding: utf-8 -*-

"""
Error module

This module holds Conjur CLI/SDK-specific errors for this project
"""
from conjur.errors_messages import FETCH_CREDENTIALS_FAILURE_MESSAGE, \
    FETCH_CONFIGURATION_FAILURE_MESSAGE, CONFIGURATION_MISSING_FAILURE_MESSAGE

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
    def __init__(self, message: str = ""):
        self.message = message
        super().__init__(self.message)

class MissingRequiredParameterException(Exception):
    """ Exception for when user does not input a required parameter """
    def __init__(self, message: str = ""):
        self.message = message
        super().__init__(self.message)

class InvalidResourceException(Exception):
    """ Exception when user inputted an invalid resource type """
    def __init__(self, message: str = ""):
        self.message = message
        super().__init__(self.message)

class InvalidFormatException(Exception):
    """
    Exception for when user provides input that is not in the proper format
    (policy yml for example)
    """
    def __init__(self, message: str = ""):
        self.message = message
        super().__init__(self.message)

class InvalidURLFormatException(Exception):
    """ Exception when user enter invalid URL format"""
    def __init__(self, message: str = ""):
        self.message = message
        super().__init__(self.message)

class CertificateNotTrustedException(Exception):
    """ Exception when user choose not trust fetched certificate """
    def __init__(self, message: str = ""):
        self.message = message
        super().__init__(self.message)

class CertificateVerificationException(Exception):
    """
    Exception for when the user runs the Client in conflicting modes. For example,
    initializing the client using --insecure but running a follow-up command in secure mode
    (without --insecure)
    """
    def __init__(self, cause: str = "", solution: str = ""):
        self.message = f"{cause} {solution}"
        super().__init__(self.message)


class RetrieveCertificateException(Exception):
    """ Exception when Unable retrieve a certificate """
    def __init__(self, message: str = ""):
        self.message = message
        super().__init__(self.message)

class ConnectionToConjurFailedException(Exception):
    """
    Exception when client cannot connect to Conjur server
    """
    def __init__(self, message: str = ""):
        self.message = message
        super().__init__(self.message)

class InvalidConfigurationException(Exception):
    """ Exception for when configuration file (from .conjurrc) is in invalid format """
    def __init__(self, message: str = FETCH_CONFIGURATION_FAILURE_MESSAGE):
        self.message = message
        super().__init__(self.message)

class ConfirmationException(Exception):
    """ Exception when user did not confirm a particular flow """
    def __init__(self, message: str = ""):
        self.message = message
        super().__init__(self.message)

class ConfigurationMissingException(Exception):
    """ Exception for when configuration is missing """
    def __init__(self, message: str = CONFIGURATION_MISSING_FAILURE_MESSAGE):
        self.message = message
        super().__init__(self.message)

class NotLoggedInException(Exception):
    """ Exception for when user not logged in """
    def __init__(self, message: str = ""):
        self.message = message
        super().__init__(self.message)

class LoggedOutFailedException(Exception):
    """ Exception for when user is failed to logout """
    def __init__(self, message:str = ""):
        self.message = message
        super().__init__(self.message)

class CredentialRetrievalException(Exception):
    """ Exception for when credentials cannot be retrieved """
    def __init__(self):
        self.message = FETCH_CREDENTIALS_FAILURE_MESSAGE
        super().__init__(self.message)

class KeyringWrapperGeneralError(Exception):
    """ General Exception for Keyring Wrapper """
    def __init__(self, message: str = ""):
        self.message = message
        super().__init__(self.message)

class KeyringWrapperDeletionError(KeyringWrapperGeneralError):
    """ Exception for Keyring Wrapper when underlying deletion operation failed """
    def __init__(self, message: str = ""):
        self.message = message
        super().__init__(self.message)

class KeyringWrapperSetError(KeyringWrapperGeneralError):
    """ Exception for Keyring Wrapper when underlying set operation failed """
    def __init__(self, message: str = ""):
        self.message = message
        super().__init__(self.message)
