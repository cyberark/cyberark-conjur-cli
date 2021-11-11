# -*- coding: utf-8 -*-

"""
Resource module
"""


# pylint: disable=too-few-public-methods
from conjur.errors import MissingRequiredParameterException


class Resource:
    """
    DTO class that represents a resource in Conjur.
    """

    @classmethod
    def from_full_id(cls, full_id: str):
        """
        Factory method for
        """
        id_parts = full_id.split(':', 2)
        if len(id_parts) == 3:
            # If identifier contains also the account part, remove it.
            id_parts.pop(0)
        elif len(id_parts) != 2:
            raise MissingRequiredParameterException(
                f"Resource id is missing 'kind:' prefix: {full_id}")

        return Resource(kind=id_parts[0], identifier=id_parts[1])

    def __init__(self, kind: str, identifier: str):
        """
        Used for representing Conjur resources
        """
        self.kind = kind
        self.identifier = identifier

    def full_id(self):
        """
        Method for building the full resource ID in the format 'user:someuser' for example
        """
        return f"{self.kind}:{self.identifier}"

    def __eq__(self, other):
        """
        Method for comparing resources by their values and not by reference
        """
        return self.kind == other.kind and self.identifier == other.identifier

    def __repr__(self):
        return f"'kind': '{self.kind}', 'identifier': '{self.identifier}'"
