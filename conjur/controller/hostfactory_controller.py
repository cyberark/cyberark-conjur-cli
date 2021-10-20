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
from conjur.data_object.create_host_data import CreateHostData
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

        logging.debug(f"Creating token for hostfactory '{create_token_data.host_factory}'...")

        result = self.hostfactory_logic.create_token(create_token_data)
        sys.stdout.write(result + '\n')
        logging.debug("Successfully created token for hostfactory "
                      f"'{create_token_data.host_factory}'")

    def create_host(self, create_host_data: CreateHostData):
        """
        Method that facilitates create token call to the logic
        """
        if create_host_data is None:
            raise MissingRequiredParameterException('Missing required parameters')

        logging.debug(f"Creating host: '{create_host_data.host_id}'...")
        result = self.hostfactory_logic.create_host(create_host_data)
        sys.stdout.write(result + '\n')
        logging.debug("Successfully created host using hostfactory: host_id:"
                      f"'{create_host_data.host_id}'")
