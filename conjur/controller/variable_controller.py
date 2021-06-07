# -*- coding: utf-8 -*-

"""
VariableController module

This module is the controller that facilitates all list actions
required to successfully execute the VARIABLE command
"""
import sys
from conjur.logic.variable_logic import VariableLogic
from conjur.data_object.variable_data import VariableData

# pylint: disable=too-few-public-methods
class VariableController:
    """
    VariableController

    This class represents the Presentation Layer for the VARIABLE command
    """
    def __init__(self, variable_logic:VariableLogic, variable_data:VariableData):
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
