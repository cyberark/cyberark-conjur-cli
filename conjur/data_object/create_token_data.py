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

    def __init__(self, **arg_params):
        self.host_factory = arg_params['hostfactoryid']
        self.cidr = arg_params['cidr'] if arg_params['cidr'] else None
        self.count = arg_params['count'] if arg_params['count'] else 1

        self.expiration = self.get_expiration(
            arg_params['duration_days'] if arg_params['duration_days'] else 0,
            arg_params['duration_hours'] if arg_params['duration_hours'] else 0,
            arg_params['duration_minutes'] if arg_params['duration_minutes'] else 0,
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

    def __repr__(self) -> str:
        return f"{{'host_factory': '{self.hostfactoryid}', " \
               f"'cidr': '{self.cidr}', " \
               f"'expiration': '{self.expiration}'" \
               f"'count': '{self.count}'}} "
