# -*- coding: utf-8 -*-

"""
ResourceController module

This module is the controller that facilitates all list actions
required to successfully execute the VARIABLE command
"""
import sys
from conjur.logic.resource_logic import ResourceLogic

# pylint: disable=too-few-public-methods
class ResourceController:
    """
    ResourceController

    This class represents the Presentation Layer for the VARIABLE command
    """
    def __init__(self, resource_logic:ResourceLogic, kind:str, resource_id:str, privilege:str = None):
        self.resource_logic = resource_logic
        self.kind = kind
        self.resource_id = resource_id
        self.privilege = privilege

    def get_resource_exists(self):
        """
        Method that facilitates get call to the logic
        """
        result = self.resource_logic.get_resource_exists(self.kind, self.resource_id)
        sys.stdout.write(str(result)+'\n')

    def get_resource_permitted_roles(self):
        """
        Method that facilitates get call to the logic
        """
        result = self.resource_logic.get_resource_permitted_roles(self.kind, self.resource_id, self.privilege)
        sys.stdout.write(str(result)+'\n')
