# -*- coding: utf-8 -*-

"""
Resource module
"""

# pylint: disable=too-few-public-methods
class Resource:
    """
    Used for representing Conjur resources
    """
    def __init__(self, type_, name):
        self.type = type_
        self.name = name

    def full_id(self):
        """
        Method for building the full resource ID in the format 'user:someuser' for example
        """
        return f"{self.type}:{self.name}"

    def __eq__(self, other):
        """
        Method for comparing resources by their values and not by reference
        """
        return self.type == other.type and self.name == other.name

    def __repr__(self):
        return f"'type': '{self.type}', 'name': '{self.name}'"
