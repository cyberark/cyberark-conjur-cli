# -*- coding: utf-8 -*-

"""
ListController module

This module is the controller that facilitates all list actions
required to successfully execute the LIST command
"""

from conjur_api.models import ListMembersOfData, ListPermittedRolesData
from conjur.logic.list_logic import ListLogic
from conjur.data_object.list_data import ListData
from conjur.util import util_functions


class ListController:
    """
    ListController

    This class represents the Presentation Layer for the LIST command
    """

    def __init__(self, list_logic: ListLogic):
        self.list_logic = list_logic

    def load(self, list_data: ListData):
        """
        Method that facilitates all method calls in this class
        """
        result = self.list_logic.list(list_data)
        util_functions.print_json_result(result)

    def get_permitted_roles(self, list_permitted_roles_data: ListPermittedRolesData):
        """
        Get all permitted roles according to given data
        """
        result = self.list_logic.get_permitted_roles(list_permitted_roles_data)
        util_functions.print_json_result(result)

    def get_role_members(self, list_role_members_data: ListMembersOfData):
        """
        List members within a role
        """
        result = self.list_logic.get_members_of(list_role_members_data)
        util_functions.print_json_result(result)
