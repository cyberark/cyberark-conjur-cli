# -*- coding: utf-8 -*-

"""
ListData module

This module represents the DTO that holds the params the user passes in.
We use this DTO to build the list request
"""


# pylint: disable=too-few-public-methods
class ListData:
    """
    Used for organizing the the params the user passed in to execute the list command
    """

    def __init__(self, **argParams):
        self.kind = argParams['kind']
        self.inspect = argParams['inspect']
        self.search = argParams['search']
        self.limit = argParams['limit']
        self.offset = argParams['offset']
        self.role = argParams['role']

    def list_dictify(self):
        """
        Method for building a dictionary from all attributes that have values
        """
        list_dict = {}
        for attr, value in self.__dict__.items():
            if value:
                list_dict[str(attr)] = value

        return list_dict

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
