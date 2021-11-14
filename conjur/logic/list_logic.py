# -*- coding: utf-8 -*-

"""
ListLogic module

This module is the business logic for executing the list command
"""
# pylint: disable=too-few-public-methods
import logging

from conjur.data_object.list_members_of_data import ListMembersOfData
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
        resource = self.__get_resource_from_identifier(data.identifier)
        data = ListPermittedRolesData(kind=resource.kind,
                                      identifier=resource.identifier,
                                      privilege=data.privilege)

        return self.client.list_permitted_roles(data)

    def get_members_of(self, data: ListMembersOfData) -> dict:
        """
        Lists the roles which have the named permission on a resource.
        """
        data.set_resource(self.__get_resource_from_identifier(data.identifier))
        return self.client.list_members_of_role(data)

    def __get_resource_from_identifier(self, identifier):
        """
        Lists the roles which have the named permission on a resource.
        """
        # Split 'kind' out of the given identifier if it was prefixed with it.
        if ':' in identifier:
            return Resource.from_full_id(identifier)

        return self.client.find_resource_by_identifier(identifier)

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
