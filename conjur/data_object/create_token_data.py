# -*- coding: utf-8 -*-

"""
VariableData module

This module represents the DTO that holds the params the user passes in.
We use this DTO to build the hostfactory create token request
"""

# pylint: disable=too-few-public-methods
from datetime import datetime, timedelta


class CreateTokenData:
    """
    Used for organizing the params the user passed in to execute the CreateToken command
    """

    def __init__(self,
                 host_factory: str,
                 cidr: str = None,
                 duration_days: int = 0,
                 duration_hours: int = 0,
                 duration_minutes: int = 0,
                 count: int = 0):
        self.host_factory = host_factory
        self.cidr = cidr.split(',') if cidr else None
        self.count = count if count else 0

        self.expiration = self.get_expiration(
            duration_days if duration_days else 0,
            duration_hours if duration_hours else 0,
            duration_minutes if duration_minutes else 0
        ).isoformat()

    @staticmethod
    def get_expiration(days, hours, minutes) -> datetime:
        default_expiration = datetime.now() + timedelta(hours=1)
        if days == 0 and hours == 0 and minutes == 0:
            return default_expiration

        return datetime.now() + timedelta(
            days=days,
            hours=hours,
            minutes=minutes)

    """
    to_dict

    This method enable aliasing 'cidr' to 'cidr[]' as the server expects and 
    is later used to urlencode this parameter
    see: parse.urlencode for more details
    """
    def to_dict(self):
        items = {
            'host_factory': self.host_factory,
            'cidr[]': self.cidr,
            'expiration': self.expiration,
            'count': self.count
        }

        if self.cidr is None:
            items.pop('cidr[]')

        return items

    def __repr__(self) -> str:
        return f"{{'host_factory': '{self.host_factory}', " \
               f"'cidr': '{self.cidr}', " \
               f"'expiration': '{self.expiration}'" \
               f"'count': '{self.count}'}} "
