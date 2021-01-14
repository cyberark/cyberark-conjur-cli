# -*- coding: utf-8 -*-

"""
VariableController module

This module is the controller that facilitates all list actions
required to successfully execute the VARIABLE command
"""
import sys


class VariableController:
    """
    VariableController

    This class represents the Presentation Layer for the VARIABLE command
    """
    def __init__(self, ssl_verify, variable_logic, variable_data):
        self.ssl_verify = ssl_verify
        self.variable_logic = variable_logic
        self.variable_data = variable_data

    def load(self):
        result = self.variable_logic.run_action(self.variable_data)
        self.print_json_result(result)

    @classmethod
    def print_json_result(cls, result):
        """
        Method to print the JSON of the returned result
        """
        sys.stdout.write(result+'\n')
