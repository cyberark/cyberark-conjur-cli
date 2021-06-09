# -*- coding: utf-8 -*-

"""
ListLogic module

This module is the business logic for executing the list command
"""
# pylint: disable=too-few-public-methods
import logging

class ListLogic:
    """
    ListLogic

    This class holds the business logic for executing and manipulating
    returned data
    """
    def __init__(self, client):
        self.client = client

    def list(self, list_data) -> str :
        """
        Method for calling list from the client service
        """
        list_constraints = self.build_constraints(list_data)
        return self.client.list(list_constraints)

    @classmethod
    def build_constraints(cls, list_data) -> dict :
        """
        Method to accumulate the constraints on list request
        """
        list_constraints = list_data.list_dictify()
        if list_constraints:
            # pylint: disable=logging-fstring-interpolation
            logging.debug(f"Executing list command with the following "\
                          f"constraints: {list_data}")
        else:
            logging.debug("Executing list command with no constraints")

        return list_constraints
