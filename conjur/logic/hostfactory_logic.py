# -*- coding: utf-8 -*-
"""
HostFactoryLogic

This module holds the business logic for executing and manipulating
returned data
"""

# Builtins
import json

# Internals
from conjur.data_object.create_token_data import CreateTokenData
from conjur.data_object.create_host_data import CreateHostData
from conjur.errors import MissingRequiredParameterException


# pylint: disable=too-few-public-methods
class HostFactoryLogic:
    """
    HostFactoryLogic

    This class holds the business logic for executing and manipulating
    returned data
    """

    def __init__(self, client):
        self.client = client

    # pylint: disable=inconsistent-return-statements
    def create_token(self, create_token_data: CreateTokenData) -> str:
        """
        Creates a host factory token using the parameters in the 'create_token_data' argument.
        Returns the generated token.
        """
        if create_token_data is None:
            raise MissingRequiredParameterException('Missing required parameters')

        response = self.client.create_token(create_token_data)

        if response is not None:
            data = response.json()
            if data is not None and len(data) > 0:
                return json.dumps(data, indent=4, sort_keys=True)

    # pylint: disable=inconsistent-return-statements
    def create_host(self, create_host_data: CreateHostData) -> str:
        """
        Creates a host factory token using the parameters in the 'create_token_data' argument.
        Returns the generated token.
        """
        if create_host_data is None:
            raise MissingRequiredParameterException('Missing required parameters')

        response = self.client.create_host(create_host_data)

        if response is not None:
            data = response.json()
            if data is not None and len(data) > 0:
                return json.dumps(data, indent=4, sort_keys=True)

    # pylint: disable=inconsistent-return-statements
    def revoke_token(self, token: str):
        """
        Revokes the given token.
        """
        if token is None:
            raise MissingRequiredParameterException('Missing required parameters')

        return self.client.revoke_token(token)
