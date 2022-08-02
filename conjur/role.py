# -*- coding: utf-8 -*-

"""
Role module
"""


# pylint: disable=duplicate-code
from conjur.errors import MissingRequiredParameterException


class Role:
    """
    DTO class that represents a role in Conjur.
    """

    @classmethod
    def from_full_id(cls, full_id: str):
        """
        Factory method for creating a Role object from a full ID.
        """
        id_parts = full_id.split(':', 2)
        if len(id_parts) == 3:
            # If identifier contains also the account part, remove it.
            id_parts.pop(0)
        elif len(id_parts) != 2:
            raise MissingRequiredParameterException(
                f"Role ID missing 'kind:' prefix: {full_id}")

        return Role(kind=id_parts[0], identifier=id_parts[1])

    def __init__(self, kind: str, identifier: str):
        """
        Used for representing Conjur roles
        """
        self.kind = kind
        self.identifier = identifier

    def full_id(self):
        """
        Method for building the full role ID in the format 'user:someuser' for example
        """
        return f"{self.kind}:{self.identifier}"
