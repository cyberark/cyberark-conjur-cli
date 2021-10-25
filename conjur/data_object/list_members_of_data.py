# -*- coding: utf-8 -*-

"""
ListData module

This module represents the DTO that holds the params the user passes in.
We use this DTO to build the list members-of request
"""

# pylint: disable=too-few-public-methods
from conjur.data_object import ListData


class ListMembersOfData(ListData):
    """
    Used for organizing the the params the user passed in to execute the list members-of command
    """

    def __init__(self, **arg_params):
        super().__init__(**arg_params)
        self.identifier = arg_params['identifier'] if 'identifier' in arg_params.keys() else None
        self.privilege = arg_params['privilege'] if 'privilege' in arg_params.keys() else None

    def list_dictify(self):
        """
        Method for building a dictionary from all attributes that have values
        """
        list_dict = super().list_dictify()
        for attr, value in self.__dict__.items():
            if value:
                list_dict[str(attr)] = value

        return list_dict

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
