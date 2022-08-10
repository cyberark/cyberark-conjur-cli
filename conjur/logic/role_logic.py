# -*- coding: utf-8 -*-

"""
RoleLogic module

This module is the business logic for executing the ROLE command
"""

# Builtins
import logging

# pylint: disable=too-few-public-methods
class RoleLogic:
    """
    RoleLogic

    This class holds the business logic for executing and manipulating
    returned data
    """

    def __init__(self, client):
        self.client = client

    # pylint: disable=logging-fstring-interpolation
    def role_exists(self, kind: str, role_id: str) -> bool:
        """
        Method to handle role exists action
        """
        logging.debug(role_id)

        return self.client.role_exists(kind, role_id)

    # pylint: disable=logging-fstring-interpolation
    def role_memberships(self, kind: str, role_id: str, direct: bool = False) -> bool:
        """
        Method to handle role memberships action
        """
        logging.debug(role_id)

        return self.client.role_memberships(kind, role_id, direct)
