# -*- coding: utf-8 -*-
import sys

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

        if create_token_data.expiration is None:
            raise MissingRequiredParameterException('expiration cannot be empty!')

        if create_token_data.count == 0:
            raise MissingRequiredParameterException('count cannot be zero!')

        result = self.hostfactory_logic.create_token(create_token_data)
        sys.stdout.write(result + '\n')
