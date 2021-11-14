# -*- coding: utf-8 -*-

"""
ListPermittedRolesData module

This module represents the DTO that holds the params the user passes in.
We use this DTO to build the permitted-roles request.
"""

# pylint: disable=too-few-public-methods


class ListPermittedRolesData:
    """
    Used for organizing the params the user passed in to execute the list permitted-roles command
    """

    def __init__(self, identifier: str, privilege: str, kind: str = None):
        self.identifier = identifier
        self.privilege = privilege
        self.kind = kind

    def __repr__(self) -> str:
        result = []
        # pylint: disable=multiple-statements
        if self.kind:
            result.append(f"'kind': '{self.kind}'")
        if self.identifier:
            result.append(f"'identifier': '{self.identifier}'")
        if self.privilege:
            result.append(f"'privilege': '{self.privilege}'")
        return '{' + ', '.join(result) + '}'
