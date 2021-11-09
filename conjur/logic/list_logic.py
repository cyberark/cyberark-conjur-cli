# -*- coding: utf-8 -*-

"""
ListLogic module

This module is the business logic for executing the list command
"""
# pylint: disable=too-few-public-methods
import logging

from conjur.data_object.list_permitted_roles_data import ListPermittedRolesData
from conjur.resource import Resource


class ListLogic:
    """
    ListLogic

    This class holds the business logic for executing and manipulating
    returned data
    """

    def __init__(self, client):
        self.client = client

    def list(self, list_data) -> str:
        """
        Method for calling list from the client service
        """
        list_constraints = self.build_constraints(list_data)
        return self.client.list(list_constraints)

    def get_permitted_roles(self, data: ListPermittedRolesData) -> dict:
        """
        Lists the roles which have the named permission on a resource.
        """
        # Split 'kind' out of the given identifier if it was prefixed with it.
        if ':' in data.identifier:
            data = self.extract_kind_from_identifier(data)
        elif not data.kind:
            data = self.retrieve_kind_by_resource_id(data)

        return self.client.list_permitted_roles(data)

    @staticmethod
    def extract_kind_from_identifier(data):
        resource = Resource.from_full_id(data.identifier)
        return ListPermittedRolesData(kind=resource.kind,
                                      identifier=resource.identifier,
                                      privilege=data.privilege)

    def retrieve_kind_by_resource_id(self, data):
        kind = self.client.get_resource_kind(data.identifier)
        return ListPermittedRolesData(kind=kind,
                                      identifier=data.identifier,
                                      privilege=data.privilege)

    @classmethod
    def build_constraints(cls, list_data: list) -> dict:
        """
        Method to accumulate the constraints on list request
        """
        list_constraints = list_data.list_dictify()
        if list_constraints:
            # pylint: disable=logging-fstring-interpolation
            logging.debug(f"Executing list command with the following constraints: {list_data}")
        else:
            logging.debug("Executing list command with no constraints")

        return list_constraints
