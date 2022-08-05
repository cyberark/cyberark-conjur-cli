# -*- coding: utf-8 -*-

"""
CheckController module

This module is the controller that facilitates all check actions
required to successfully execute the CHECK command
"""
import sys
from conjur_api.errors.errors import HttpStatusError
from conjur.logic.check_logic import CheckLogic
from conjur.resource import Resource

# pylint: disable=too-few-public-methods
class CheckController:
    """
    CheckController

    This class represents the Presentation Layer for the CHECK command
    """

    def __init__(self, check_logic: CheckLogic):
        self.check_logic = check_logic

    def check(self, resource_id: str, privilege: str, role: str = None):
        """
        Method that facilitates all method calls in this class
        """
        resource = Resource.from_full_id(resource_id)
        try:
            result = self.check_logic.check(resource.kind, resource.identifier, privilege, role)
            sys.stdout.write(str(result).lower()+'\n')
        except HttpStatusError as http_error:
            raise HttpStatusError(status=http_error.status,
                                  message=f"{http_error}. Error: {http_error.response}",
                                  response=http_error.response) from http_error
