# -*- coding: utf-8 -*-

"""
ResourceController module

This module is the controller that facilitates all resource actions
required to successfully execute the RESOURCE command
"""

import sys
from conjur.logic.resource_logic import ResourceLogic
from conjur.resource import Resource
from conjur.util import util_functions

# pylint: disable=too-few-public-methods
class ResourceController:
    """
    ResourceController

    This class represents the Presentation Layer for the RESOURCE command
    """

    def __init__(self, resource_logic: ResourceLogic):
        self.resource_logic = resource_logic

    def exists(self, resource_id: str, json_response: str = False):
        """
        Method that facilitates the exists command
        """
        resource = Resource.from_full_id(resource_id)
        result = self.resource_logic.exists(resource.kind, resource.identifier)

        if json_response:
            util_functions.print_json_result({'exists' : result})
        else:
            sys.stdout.write(str(result).lower()+'\n')
