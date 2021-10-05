# -*- coding: utf-8 -*-

"""
VariableData module

This module represents the DTO that holds the params the user passes in.
We use this DTO to build the hostfactory create token request
"""

# pylint: disable=too-few-public-methods
from datetime import timedelta


class CreateTokenData:
    """
    Used for organizing the params the user passed in to execute the CreateToken command
    """

    def __init__(self,
                 host_factory: str = "",
                 cidr: str = None,
                 duration: timedelta = timedelta(days=0, hours=1, minutes=0),
                 count: int = 1):
        self.host_factory = host_factory
        self.cidr = cidr.split(',') if cidr else []
        self.count = 1 if count is None else count
        self.duration = duration

    def to_dict(self):
        """
        to_dict

        This method enable aliasing 'cidr' to 'cidr[]' as the server expects and
        is later used to urlencode this parameter
        see: parse.urlencode for more details
        """
        return {
            'host_factory': self.host_factory,
            'cidr[]': self.cidr,
            'expiration': self.duration,
            'count': self.count
        }

    def __repr__(self) -> str:
        return f"{{'host_factory': '{self.host_factory}', " \
               f"'cidr': '{self.cidr}', " \
               f"'expiration': '{self.duration}', " \
               f"'count': '{self.count}'}}"
