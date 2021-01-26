# -*- coding: utf-8 -*-

"""
ListController module

This module is the controller that facilitates all list actions
required to successfully execute the LIST command
"""
# Builtins
import json
import sys


class ListController:
    """
    ListController

    This class represents the Presentation Layer for the LIST command
    """

    def __init__(self, list_logic, list_data):
        self.list_logic = list_logic
        self.list_data = list_data

    def load(self):
        """
        Method that facilitates all method calls in this class
        """
        result = self.list_logic.list(self.list_data)
        self.print_json_result(result)

    @classmethod
    def print_json_result(cls, result):
        """
        Method to print the JSON of the returned result
        """
        sys.stdout.write(f"{json.dumps(result, indent=4)}\n")
