# -*- coding: utf-8 -*-

"""
ResourceLogic module

This module is the business logic for executing the VARIABLE command
"""

# Builtins
import json
import logging

from conjur_api.errors.errors import HttpStatusError
from conjur_api.models.list.list_permitted_roles_data import ListPermittedRolesData


# pylint: disable=too-few-public-methods
class ResourceLogic:
    """
    ResourceLogic

    This class holds the business logic for executing and manipulating
    returned data
    """

    def __init__(self, client):
        self.client = client

    # pylint: disable=logging-fstring-interpolation
    def get_resource_exists(self, kind: str, resource_id: str) -> bool:
        """
        Method to handle all get resource exists action activity
        """
        logging.debug(resource_id)
        try:
            resource_value = self.client.show(kind, resource_id)
        except HttpStatusError as err:
            if '404' in str(err):
                return False

        return resource_value is not None


    # pylint: disable=logging-fstring-interpolation
    def get_resource_permitted_roles(self, kind: str, resource_id: str, privilege: str) -> str:
        """
        Method to handle all get resource permitted roles action activity
        """
        logging.debug(resource_id)

        list_permitted_roles_data = ListPermittedRolesData(resource_id, privilege, kind)
        resource_value = self.client.list_permitted_roles(list_permitted_roles_data)

        return resource_value
