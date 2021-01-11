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
    # pylint: disable=line-too-long,too-many-arguments
    def __init__(self, kind=None, inspect=False, search=None, limit=None, offset=None, acting_as=None):
        self.kind = kind
        self.inspect = inspect
        self.search = search
        self.limit = limit
        self.offset = offset
        self.acting_as = acting_as

    def list_dictify(self):
        """
        Method for building a dictionary from all attributes that have values
        """
        list_dict={}
        for attr, value in self.__dict__.items():
            if value is not None and value is not False:
                list_dict[str(attr)] = value

        return list_dict

    def __repr__(self):
        # pylint: disable=line-too-long
        return "{ 'kind': %r, 'inspect': %r, 'search': %r, 'limit': %r, 'offset': %r, 'role': %r }" % (self.kind,
                                                                                                       self.inspect,
                                                                                                       self.search,
                                                                                                       self.limit,
                                                                                                       self.offset,
                                                                                                       self.acting_as)
