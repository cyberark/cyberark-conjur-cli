# -*- coding: utf-8 -*-

"""
VariableData module

This module represents the DTO that holds the params the user passes in.
We use this DTO to build the variable request
"""


# pylint: disable=too-few-public-methods
class VariableData:
    """
    Used for organizing the params the user passed in to execute the variable command
    """

    def __init__(self, **arg_params):
        self.action = arg_params['action']
        self.variable_id = arg_params['id']
        # pylint: disable=line-too-long
        self.variable_version = arg_params['variable_version'] if arg_params['variable_version'] else None
        self.value = arg_params['value'] if arg_params['value'] else None

    def __repr__(self) -> str:
        result = []
        # pylint: disable=multiple-statements
        if self.action == 'get': result.append(f"Getting variable values for: '{self.variable_id}'")
        if self.variable_version: result.append(f" with version '{self.variable_version}'")
        if self.action == 'set': result.append(f"Setting variable value for: '{self.variable_id}'")
        return ''.join(result)
