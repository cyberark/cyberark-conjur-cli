# -*- coding: utf-8 -*-

"""
Error module

This module holds Conjur SDK-specific errors for this project
"""


class CertificateHostnameMismatchException(Exception):
    """ Thrown to indicate that a mismatch in the certificate hostname. """
