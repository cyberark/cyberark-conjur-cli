# -*- coding: utf-8 -*-
"""
HostFactoryController

This Module represents the Presentation Layer for the HostFactory command
"""
import logging
import sys

# Internals
from conjur.errors import MissingRequiredParameterException
from conjur.data_object.create_token_data import CreateTokenData
from conjur.logic.hostfactory_logic import HostFactoryLogic


# pylint: disable=too-few-public-methods,logging-fstring-interpolation
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
            raise MissingRequiredParameterException('Missing required parameters')

        if create_token_data.host_factory is None:
            raise MissingRequiredParameterException("Missing required parameter, 'host_factory'")

        if create_token_data.count == 0 or create_token_data.count < 0:
            raise MissingRequiredParameterException("Missing required parameter 'count' "
                                                    "or it is not in the correct format")

        logging.debug(f"Creating token for hostfactory '{create_token_data.host_factory}'...")

        result = self.hostfactory_logic.create_token(create_token_data)
        sys.stdout.write(result + '\n')
        logging.debug("Successfully created token for hostfactory "
                      f"'{create_token_data.host_factory}'")
