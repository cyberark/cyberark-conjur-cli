# -*- coding: utf-8 -*-

"""
VariableLogic module

This module is the business logic for executing the VARIABLE command
"""

# Builtins
import json
import logging
import inspect

# pylint: disable=too-few-public-methods
class VariableLogic:
    """
    VariableLogic

    This class holds the business logic for executing and manipulating
    returned data
    """

    def __init__(self, client):
        self.client = client

    # pylint: disable=logging-fstring-interpolation
    def get_variable(self, variable_data):
        """
        Method to handle all get action activity
        """
        logging.debug(variable_data)
        # pylint: disable=no-else-return
        if len(variable_data.variable_id) == 1:
            variable_value = self.client.get(variable_data.variable_id[0],
                                             variable_data.variable_version)
            return variable_value.decode('utf-8')
        else:
            variable_values = self.client.get_many(*variable_data.variable_id)
            return json.dumps(variable_values, indent=4)

    # pylint: disable=logging-fstring-interpolation
    def set_variable(self, variable_data):
        """
        Method to handle all set action activity
        """
        logging.debug(variable_data)
        self.client.set(variable_data.variable_id, variable_data.value)

        logging.debug(f"Successfully set value for variable '{variable_data.variable_id}'")
        return variable_data.variable_id
