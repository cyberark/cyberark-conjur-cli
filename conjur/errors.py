# -*- coding: utf-8 -*-

"""
Error module

This module holds all CLI-specific errors
"""
# pylint: disable=unnecessary-pass
class InvalidOperation(Exception):
    """
    Error for invalid user operations
    """
    pass

# pylint: disable=unnecessary-pass
class InvalidPasswordComplexity(Exception):
    """
    Error for when the user supplies a not complex enough password when
    attempting to change their password
    """
    pass
