# -*- coding: utf-8 -*-

"""
ListController module

This module is the controller that facilitates all list actions
required to successfully execute the LIST command
"""
import json
import logging
import sys

from Utils.utils import Utils


class ListController:
    """
    ListController

    This class represents the Presentation Layer for the LIST command
    """

    def __init__(self, ssl_verify, list_logic, list_data):
        self.ssl_verify = ssl_verify
        if self.ssl_verify is False:
            Utils.get_insecure_warning()

        self.list_logic = list_logic
        self.list_data = list_data

    def load(self):
        """
        Method that facilitates all method calls in this class
        """
        list_constraints = self.list_data.list_dictify()
        # pylint: disable=logging-fstring-interpolation
        logging.debug(f"Executing list command with the following "\
                      f"constraints: {list_constraints}")

        result = self.list_logic.list(list_constraints)
        self.print_json_result(result)

    @classmethod
    def print_json_result(cls, result):
        """
        Method to print the JSON of the returned result
        """
        sys.stdout.write(f"{json.dumps(result, indent=4)}\n")
