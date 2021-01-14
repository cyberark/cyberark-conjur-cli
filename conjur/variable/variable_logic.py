# -*- coding: utf-8 -*-

"""
VariableLogic module

This module is the business logic for executing the VARIABLE command
"""

# Builtins
import json
import logging


class VariableLogic:
    """
    VariableLogic

    This class holds the business logic for executing and manipulating
    returned data
    """
    def __init__(self, client):
        self.client = client

    def run_action(self, variable_data):
        """
        Method to determine which subcommand action to run {get, set}
        """
        if variable_data.action == 'get':
            logging.debug(f"Fetching variable value(s) for: {variable_data.id}")
            if len(variable_data.id) == 1:
                variable_value = self.client.get(variable_data.id[0])
                return variable_value.decode('utf-8')
            else:
                variable_values = self.client.get_many(*variable_data.id)
                return json.dumps(variable_values, indent=4)
        else:
            logging.debug(f"Setting variable value for: '{variable_data.id}'")
            self.client.set(variable_data.id, variable_data.value)
            logging.debug(f"Successfully set value for variable '{variable_data.id}'")
            return "Value set: '{}'".format(variable_data.id)
