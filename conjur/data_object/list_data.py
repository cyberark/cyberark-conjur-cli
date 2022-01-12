# -*- coding: utf-8 -*-

"""
ListData module

This module represents the DTO that holds the params the user passes in.
We use this DTO to build the list request
"""


# pylint: disable=too-few-public-methods
from conjur_api.utils import util_functions
from conjur_api.utils.util_functions import get_param


class ListData:
    """
    Used for organizing the the params the user passed in to execute the list command
    """

    def __init__(self, **arg_params):
        self.kind = get_param('kind', **arg_params)
        self.inspect = get_param('inspect', **arg_params)
        self.search = get_param('search', **arg_params)
        self.limit = get_param('limit', **arg_params)
        self.offset = get_param('offset', **arg_params)
        self.role = get_param('role', **arg_params)

    def list_dictify(self):
        """
        Returns a dictionary of all non-None attributes values
        """
        return util_functions.list_dictify(self)

    def __repr__(self) -> str:
        result = []
        # pylint: disable=multiple-statements
        if self.kind: result.append(f"'kind': '{self.kind}'")
        if self.limit: result.append(f"'limit': '{self.limit}'")
        if self.inspect: result.append(f"'inspect': '{self.inspect}'")
        if self.search: result.append(f"'search': '{self.search}'")
        if self.offset: result.append(f"'offset': '{self.offset}'")
        if self.role: result.append(f"'role': '{self.role}'")
        return '{' + ', '.join(result) + '}'
