# -*- coding: utf-8 -*-

"""
ResourceLogic module

This module is the business logic for executing the resource command
"""

import logging

# pylint: disable=too-few-public-methods
class ResourceLogic:
    """
    ResourceLogic

    This class holds the business logic for managing resources.
    """

    def __init__(self, client):
        self.client = client

    def exists(self, kind: str, resource_id: str) -> bool:
        """
        Method for checking for existence of a resource
        """
        logging.debug(resource_id)

        return self.client.resource_exists(kind, resource_id)
