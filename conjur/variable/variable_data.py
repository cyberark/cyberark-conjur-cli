# -*- coding: utf-8 -*-

"""
VariableData module

This module represents the DTO that holds the params the user passes in.
We use this DTO to build the variable request
"""

# pylint: disable=too-few-public-methods
class VariableData:
    """
    Used for organizing the the params the user passed in to execute the variable command
    """
    def __init__(self, **arg_params):
        self.action = arg_params['action']
        self.variable_id = arg_params['id']
        if arg_params['value']:
            self.value = arg_params['value']

    def __repr__(self):
        result = []
        # pylint: disable=multiple-statements
        if self.action: result.append(f"'action': '{self.action}'")
        if self.variable_id: result.append(f"'id': '{self.variable_id}'")
        if self.action == 'set': result.append("'value': '****'")
        return '{'+', '.join(result) + '}'
