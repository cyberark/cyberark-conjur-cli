# -*- coding: utf-8 -*-

"""
HostResourceData module

This module represents the DTO that holds the params the user passes in.
We use this DTO to build the host request
"""


# pylint: disable=too-few-public-methods
class HostResourceData:
    """
    Used for organizing the the params execute the user command
    """

    def __init__(self, **arg_params):
        self.action = arg_params['action']
        self.host_to_update = arg_params['host_to_update']

    def __repr__(self) -> str:
        result = []
        # pylint: disable=multiple-statements
        if self.action: result.append(f"'action': '{self.action}'")
        if self.host_to_update: result.append(f"'host': '{self.host_to_update}'")
        return '{' + ', '.join(result) + '}'
