# -*- coding: utf-8 -*-

"""
RoleController module

This module is the controller that facilitates all list actions
required to successfully execute the ROLE command
"""
import json
import sys
from conjur.logic.role_logic import RoleLogic
from conjur.role import Role

# pylint: disable=too-few-public-methods
class RoleController:
    """
    RoleController

    This class represents the Presentation Layer for the ROLE command
    """
    def __init__(self, role_logic:RoleLogic):
        self.role_logic = role_logic

    def role_exists(self, identifier: str, json_response: str = False):
        """
        Method that facilitates get call to the logic
        """

        role = Role.from_full_id(identifier)
        result = self.role_logic.role_exists(role.kind, role.identifier)

        if json_response:
            sys.stdout.write(f"{json.dumps({'exists' : result}, indent=4)}\n")
        else:
            sys.stdout.write(str(result).lower()+'\n')
