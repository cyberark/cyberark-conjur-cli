# -*- coding: utf-8 -*-

"""
UserResourceData module

This module represents the DTO that holds the params the user passes in.
We use this DTO to build the user request
"""

# pylint: disable=too-few-public-methods
class UserResourceData:
    """
    Used for organizing the the params execute the user command
    """
    def __init__(self, **arg_params):
        self.action = arg_params['action']
        self.user_id = arg_params['id']
        self.new_password = arg_params['new_password']

    def __repr__(self):
        result = []
        # pylint: disable=multiple-statements
        if self.action: result.append(f"'action': '{self.action}'")
        if self.action == 'rotate-api-key': result.append(f"'id': '{self.user_id}'")
        if self.action == 'change-password': result.append("'new_password': '****'")
        return '{'+', '.join(result) + '}'
