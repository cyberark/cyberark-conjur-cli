# -*- coding: utf-8 -*-
"""
HostFactoryController

This Module represents the Presentation Layer for the HostFactory command
"""
# Builtins
import http
import logging
import sys
import traceback

# Third party
import requests

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
        try:
            result = self.hostfactory_logic.create_host(create_host_data)
            sys.stdout.write(result + '\n')
            logging.debug("Successfully created host using hostfactory: host_id:"
                          f"'{create_host_data.host_id}'")
        except requests.exceptions.HTTPError as server_error:
            logging.debug(traceback.format_exc())
            # pylint: disable=no-member
            if hasattr(server_error.response, 'status_code') \
                    and server_error.response.status_code == http.HTTPStatus.UNAUTHORIZED:
                raise Exception("Cannot create a host using the Host Factory token provided."
                                f" Reason: {server_error}. Check that the token is valid"
                                "/has not been revoked and try again.")

    def revoke_token(self, token: str):
        """
        Method that facilitates token revocation call to the logic
        """
        if token is None:
            raise MissingRequiredParameterException('Missing required parameters')

        logging.debug("Attempting to revoke a token")
        response = self.hostfactory_logic.revoke_token(token)

        if response == http.HTTPStatus.NO_CONTENT:
            sys.stdout.write(f'Token \'{token}\' has been revoked.\n')

        logging.debug(f'Successfully revoked token'
                      f', return code: {response}')
