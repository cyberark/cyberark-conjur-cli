
# -*- coding: utf-8 -*-

"""
Error module
This module holds Conjur SDK-specific errors for this project
"""


class CertificateHostnameMismatchException(Exception):
    """ Thrown to indicate that a mismatch in the certificate hostname. """


# pylint: disable=line-too-long
class InvalidParameterException(Exception):
    """ Thrown to indicate that a method has been passed an illegal or inappropriate argument. """


# pylint: disable=line-too-long
class InvalidConfigurationsException(Exception):
    """ Thrown to indicate a configuration exception. """


# pylint: disable=line-too-long
class InitializationException(Exception):
    """ Thrown to indicate an exception during init """