# -*- coding: utf-8 -*-

"""
VariableLogic module

This module is the business logic for executing the HostFactory commands
"""

# Internals
import json

from conjur.data_object.create_token_data import CreateTokenData
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

    def create_token(self, create_token_data: CreateTokenData) -> str:
        if create_token_data is None:
            raise MissingRequiredParameterException('create_token_data')

        response = self.client.create_token(create_token_data)

        if response is not None and response.json() is not None and len(response.json()) > 0:
            return json.dumps(response.json(), indent=4, sort_keys=True)

        raise Exception('create_token API call failed')
