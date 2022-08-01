# -*- coding: utf-8 -*-

"""
ShowController module

This module is the controller that facilitates all show actions
required to successfully execute the SHOW command
"""

from conjur_api.errors.errors import HttpStatusError
from conjur.logic.show_logic import ShowLogic
from conjur.resource import Resource
from conjur.util import util_functions

# pylint: disable=too-few-public-methods
class ShowController:
    """
    ShowController

    This class represents the Presentation Layer for the SHOW command
    """

    def __init__(self, show_logic: ShowLogic):
        self.show_logic = show_logic

    def load(self, resource_id: str):
        """
        Method that facilitates all method calls in this class
        """
        resource = Resource.from_full_id(resource_id)
        try:
            result = self.show_logic.show(resource.kind, resource.identifier)
            util_functions.print_json_result(result)
        except HttpStatusError as http_error:
            raise HttpStatusError(status=http_error.status,
                                  message=f"{http_error}. Error: {http_error.response}",
                                  response=http_error.response) from http_error
