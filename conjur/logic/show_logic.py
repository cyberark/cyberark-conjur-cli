# -*- coding: utf-8 -*-

"""
ShowLogic module

This module is the business logic for executing the show command
"""

import json

# pylint: disable=too-few-public-methods
class ShowLogic:
    """
    ShowLogic

    This class holds the business logic for displaying individual resources.
    """

    def __init__(self, client):
        self.client = client

    def show(self, kind: str, resource_id: str) -> json:
        """
        Method for calling get_resource from the client service
        """
        return self.client.get_resource(kind, resource_id)
