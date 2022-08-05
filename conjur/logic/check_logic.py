# -*- coding: utf-8 -*-

"""
CheckLogic module

This module is the business logic for executing the check command
"""

# pylint: disable=too-few-public-methods
class CheckLogic:
    """
    CheckLogic

    This class holds the business logic for checking privileges on a resource.
    """

    def __init__(self, client):
        self.client = client

    def check(self, kind: str, resource_id: str, privilege: str, role_id: str = None) -> bool:
        """
        Method for calling check_privilege from the client service
        """
        return self.client.check_privilege(kind, resource_id, privilege, role_id)
