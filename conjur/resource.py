# -*- coding: utf-8 -*-

"""
Resource module
"""

# pylint: disable=too-few-public-methods
class Resource:
    """
    Used for representing Conjur resources
    """
    def __init__(self, **arg_params):
        self.resource_type = arg_params['resource_type']
        self.resource_name = arg_params['resource_name']

    def full_id(self):
        """
        Method for building the full resource ID in the format 'user:someuser' for example
        """
        return ':'.join([self.resource_type, self.resource_name])

    def __repr__(self):
        return f"'resource_type': '{self.resource_type}', 'resource_name': '{self.resource_name}'"
