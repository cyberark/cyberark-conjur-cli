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

# Internals
from conjur.errors import MissingRequiredParameterException, InvalidHostFactoryTokenException
from conjur_api.errors.errors import HttpError, HttpStatusError
from conjur_api.models import CreateTokenData, CreateHostData
from conjur.logic.hostfactory_logic import HostFactoryLogic

# pylint: disable=too-few-public-methods,logging-fstring-interpolation
INVALID_TOKEN_ERROR = "Cannot create host using Host " \
                      "Factory token provided." \
                      " Reason: {}. " \
                      "Check that the token is valid" \
                      "/has not been revoked and try again."


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

        logging.debug(f"Creating Host Factory token '{create_token_data.host_factory}'...")

        result = self.hostfactory_logic.create_token(create_token_data)
        sys.stdout.write(result + '\n')
        logging.debug("Successfully created Host Factory token "
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
            logging.debug("Successfully created host using Host Factory: host_id:"
                          f"'{create_host_data.host_id}'")
        except HttpStatusError as server_error:
            logging.debug(traceback.format_exc())
            if server_error.status == http.HTTPStatus.UNAUTHORIZED:
                raise InvalidHostFactoryTokenException(
                    INVALID_TOKEN_ERROR.format(server_error)) from server_error
        except HttpError:
            logging.debug(traceback.format_exc())

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

        logging.debug(f'Successfully revoked Host Factory token'
                      f', return code: {response}')
