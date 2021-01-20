# -*- coding: utf-8 -*-

"""
VariableController module

This module is the controller that facilitates all list actions
required to successfully execute the VARIABLE command
"""
import sys

# pylint: disable=too-few-public-methods
class VariableController:
    """
    VariableController

    This class represents the Presentation Layer for the VARIABLE command
    """
    def __init__(self, ssl_verify, variable_logic, variable_data):
        self.ssl_verify = ssl_verify
        self.variable_logic = variable_logic
        self.variable_data = variable_data

    def get_variable(self):
        """
        Method that facilitates get call to the logic
        """
        result = self.variable_logic.get_variable(self.variable_data)
        sys.stdout.write(result+'\n')

    def set_variable(self):
        """
        Method that facilitates set call to the logic
        """
        result = self.variable_logic.set_variable(self.variable_data)
        sys.stdout.write(f"Successfully set value for variable '{result}'\n")
