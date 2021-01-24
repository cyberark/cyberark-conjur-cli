# -*- coding: utf-8 -*-

"""
Error module

This module holds all CLI-specific errors
"""
# pylint: disable=unnecessary-pass
class RotateApiKeyProvidedUserIsSameAsLoggedIn(Exception):
    """
    Error for when the logged-in user supplies their id for the user's API key to rotate
    This avoids returning a general 401 error from the Conjur server
    """
    pass

# pylint: disable=unnecessary-pass
class InvalidPasswordComplexity(Exception):
    """
    Error for when the user supplies a not complex enough password when
    attempting to change their password
    """
    pass
