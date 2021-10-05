# -*- coding: utf-8 -*-

"""
VariableData module

This module represents the DTO that holds the params the user passes in.
We use this DTO to build the hostfactory create token request
"""

import logging
from datetime import timedelta, datetime

# pylint: disable=too-many-arguments,no-self-use,too-few-public-methods
class CreateTokenData:
    """
    Used for organizing the params the user passed in to execute the CreateToken command
    """

    def __init__(self,
                 host_factory: str = "",
                 cidr: str = None,
                 days: int = 0,
                 hours: int = 0,
                 minutes: int = 0,
                 count: int = 0):
        self.host_factory = host_factory
        self.cidr = cidr.split(',') if cidr else []
        self.count = 1 if count is None else count

        self.days = days if days else 0
        self.hours = hours if hours else 0
        self.minutes = minutes if minutes else 0

        self.duration = self.set_duration(self.days, self.hours, self.minutes)

    def set_duration(self, days, hours, minutes):
        """
        Compiles the hours, days, minutes into a single duration
        """

        now = datetime.utcnow()
        # set the request token duration parameter, default is one hour
        default_duration = now + timedelta(hours=1)
        duration = timedelta(days=days, hours=hours, minutes=minutes)
        duration_sec = duration.total_seconds()

        if duration_sec > 0:
            duration = now + duration
        else:
            logging.debug("Duration was not provided for token, defaulting to 1 hour...")
            duration = default_duration

        return duration.isoformat()

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
