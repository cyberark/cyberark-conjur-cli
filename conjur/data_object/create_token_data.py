# -*- coding: utf-8 -*-

"""
VariableData module

This module represents the DTO that holds the params the user passes in.
We use this DTO to build the hostfactory create token request
"""

from datetime import timedelta, datetime

# pylint: disable=too-many-arguments,no-self-use,too-few-public-methods
from conjur.errors import MissingRequiredParameterException, InvalidFormatException


class CreateTokenData:
    """
    Used for organizing the params the user passed in to execute the CreateToken command
    """

    def __init__(self,
                 host_factory: str = "",
                 cidr: str = "",
                 days: int = 0,
                 hours: int = 0,
                 minutes: int = 0,
                 count: int = None):
        self.host_factory = host_factory
        self.cidr = cidr.split(',') if cidr is not None else []
        self.count = 1 if count is None else count

        self.days = days if days else 0
        self.hours = hours if hours else 0
        self.minutes = minutes if minutes else 0

        if self.host_factory == "":
            raise MissingRequiredParameterException("Missing required parameter, 'hostfactory-id'")

        if self.count <= 0:
            raise InvalidFormatException("Parameter 'count' is not in the correct format")

        if self.days <= 0 and self.hours <= 0 and self.minutes <= 0:
            raise InvalidFormatException("Either 'duration-days' / 'duration-hours' "
                                         "/ 'duration-minutes' are missing or not in "
                                         "the correct format. "
                                         "Solution: provide one of the required parameters or "
                                         "make sure they are positive numbers")

        self.duration = self._set_duration(self.days, self.hours, self.minutes)

    def _set_duration(self, days, hours, minutes):
        """
        Compiles the hours, days, minutes into a single duration
        """

        duration_difference = timedelta(days=days, hours=hours, minutes=minutes)
        utc_duration = datetime.utcnow() + duration_difference
        return utc_duration.isoformat()

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

    # pylint: disable=multiple-statements
    def __str__(self) -> str:
        result = []
        if self.host_factory: result.append(f"'host_factory': '{self.host_factory}'")
        if self.cidr: result.append(f"'cidr': '{self.cidr}'")
        if self.duration: result.append(f"'expiration': '{self.duration}'")
        if self.count: result.append(f"'count': '{self.count}'")
        return '{' + ', '.join(result) + '}'
