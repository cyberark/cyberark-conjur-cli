# -*- coding: utf-8 -*-
"""
HostFactoryController

This Module represents the Presentation Layer for the HostFactory command
"""

import sys
from datetime import datetime, timedelta

from conjur.errors import MissingRequiredParameterException
from conjur.data_object.create_token_data import CreateTokenData
from conjur.logic.hostfactory_logic import HostFactoryLogic


# pylint: disable=too-few-public-methods
class HostFactoryController:
    """
    HostFactoryController

    This class represents the Presentation Layer for the HostFactory command
    """

    def __init__(self, hostfactory_logic: HostFactoryLogic):
        self.hostfactory_logic = hostfactory_logic

    def create_token(self, create_token_data: CreateTokenData):
        """
        Method that facilitates create token call to the logic
        """
        if create_token_data is None:
            raise MissingRequiredParameterException('create_token_data cannot be empty!')

        if create_token_data.host_factory is None:
            raise MissingRequiredParameterException('host_factory cannot be empty!')

        if create_token_data.duration is None:
            raise MissingRequiredParameterException('expiration cannot be empty!')

        if create_token_data.count == 0:
            raise MissingRequiredParameterException('count cannot be zero!')

        # set the request token duration parameter, default is one hour
        now = datetime.utcnow()
        default_duration = now + timedelta(hours=1)
        duration = create_token_data.duration
        duration_sec = duration.total_seconds()
        duration = (now + duration if duration_sec > 0 else default_duration)
        create_token_data.duration = duration.isoformat()

        result = self.hostfactory_logic.create_token(create_token_data)
        sys.stdout.write(result + '\n')
