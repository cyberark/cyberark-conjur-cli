# -*- coding: utf-8 -*-

"""
ListLogic module

This module is the business logic for executing the list command
"""
# pylint: disable=too-few-public-methods
class ListLogic:
    """
    ListLogic

    This class holds the business logic for executing and manipulating
    returned data
    """
    def __init__(self, client):
        self.client = client

    def list(self, list_constraints):
        """
        Method for calling list from the client service
        """
        return self.client.list(list_constraints)
