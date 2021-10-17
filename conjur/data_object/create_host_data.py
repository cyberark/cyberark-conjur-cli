# -*- coding: utf-8 -*-

"""
CreateHostData module

This module represents the DTO that holds the params the user passes in.
We use this DTO to build the hostfactory create host request
"""

# pylint: disable=too-many-arguments,no-self-use,too-few-public-methods
from conjur.errors import MissingRequiredParameterException


class CreateHostData:
    """
    Used for organizing the params the user passed in to execute the CreateHost command
    """

    def __init__(self,
                 # using id shadows the internal id
                 host_id: str = "",
                 token: str = "",
                 annotations: str = None):
        self.host_id = host_id
        self.token = token
        self.annotations = annotations

        if self.id == "":
            raise MissingRequiredParameterException("Missing required parameter, 'id'")

        if self.token == "":
            raise MissingRequiredParameterException("Missing required parameter, 'token'")

    def to_dict(self):
        """
        to_dict

        This method enable aliasing 'host_id' to 'id' as the server expects
        """
        params = {
            'id': self.host_id
        }

        if self.annotations is not None:
            params['annotations': self.annotations]

        return params

    def __repr__(self) -> str:
        return f"{{'id': '{self.host_factory}', " \
               f"'annotations': '{self.annotations}'"
