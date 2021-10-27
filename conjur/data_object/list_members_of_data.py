# -*- coding: utf-8 -*-

"""
ListData module

This module represents the DTO that holds the params the user passes in.
We use this DTO to build the list members-of request
"""

# pylint: disable=too-few-public-methods
from conjur.data_object import ListData
from conjur.util import util_functions
from conjur.util.util_functions import get_param


class ListMembersOfData(ListData):
    """
    Used for organizing the the params the user passed in to execute the list members-of command
    """

    def __init__(self, **arg_params):
        super().__init__(**arg_params)
        self.identifier = get_param('identifier', **arg_params)
        self.privilege = get_param('privilege', **arg_params)

    def list_dictify(self):
        """
        Returns a dictionary of all non-None attributes values
        """
        return util_functions.list_dictify(self)

    def __repr__(self) -> str:
        result = []
        # pylint: disable=multiple-statements
        if self.kind:
            result.append(f"'kind': '{self.kind}'")
        if self.limit:
            result.append(f"'limit': '{self.limit}'")
        if self.search:
            result.append(f"'search': '{self.search}'")
        if self.offset:
            result.append(f"'offset': '{self.offset}'")
        if self.role:
            result.append(f"'role': '{self.role}'")
        if self.role:
            result.append(f"'identifier': '{self.identifier}'")
        return '{' + ', '.join(result) + '}'
