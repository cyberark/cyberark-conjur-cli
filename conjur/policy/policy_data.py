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
    def __init__(self, **argParams):
        self.action = argParams['action']
        self.branch = argParams['branch']
        self.file = argParams['file']

    def __repr__(self):
        result = []
        # pylint: disable=multiple-statements
        if self.action: result.append(f"'action': '{self.action}'")
        if self.branch: result.append(f"'branch': '{self.branch}'")
        if self.file: result.append(f"'file': '{self.file}'")
        return '{'+', '.join(result) + '}'
