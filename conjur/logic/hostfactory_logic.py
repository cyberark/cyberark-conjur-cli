# -*- coding: utf-8 -*-

"""
VariableLogic module

This module is the business logic for executing the HostFactory commands
"""
import json
from urllib import parse

# Internals
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
            raise MissingRequiredParameterException('create_token_data cannot be empty!')

        # parse.urlencode, If any values in the query arg are sequences and doseq is true, each
        # sequence element is converted to a separate parameter.
        # This is set to True to handle CreateTokenData.cidr which is a list
        response = self.client.create_token(parse.urlencode(create_token_data.to_dict(),
                                                            doseq=True))

        if response is not None and response.json() is not None and len(response.json()) > 0:
            return json.dumps(response.json(), indent=4, sort_keys=True)

        raise Exception('create_token API call failed')
