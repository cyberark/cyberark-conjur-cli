"""
AuthnTypes module
This module is used to represent different authentication methods.
"""

from enum import Enum


class AuthnTypes(Enum):   # pragma: no cover
    """
    Represent possible authn methods that can be used.
    """
    AUTHN = 0
    LDAP = 1

    def __str__(self):
        """
        Return string representation of AuthnTypes.
        """
        return self.name.lower()
