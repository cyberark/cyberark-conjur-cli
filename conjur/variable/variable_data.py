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
    def __init__(self, **argParams):
        self.action = argParams['action']
        self.id = argParams['id']
        if argParams['value']:
            self.value = argParams['value']

    def __repr__(self):
        result = []
        # pylint: disable=multiple-statements
        if self.action: result.append(f"'action': '{self.action}'")
        if self.id: result.append(f"'id': '{self.id}'")
        if self.action == 'set': result.append(f"'value': '****'")
        return '{'+', '.join(result) + '}'
