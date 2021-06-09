# -*- coding: utf-8 -*-

"""
PolicyData module

This module represents the DTO that holds the params the user passes in.
We use this DTO to build the policy request
"""

# pylint: disable=too-few-public-methods
class PolicyData:
    """
    Used for organizing the the params the user passed in to execute the policy command
    """
    def __init__(self, **arg_params):
        self.action = arg_params['action']
        self.branch = arg_params['branch']
        self.file = arg_params['file']

    def __repr__(self) -> str:
        result = []
        # pylint: disable=multiple-statements
        if self.action=='load': result.append("Loading ")
        if self.action=='replace': result.append("Replacing ")
        if self.action=='update': result.append("Updating ")
        if self.file: result.append(f"'{self.file}' ")
        if self.branch: result.append(f"under '{self.branch}'...")
        return ''.join(result)
