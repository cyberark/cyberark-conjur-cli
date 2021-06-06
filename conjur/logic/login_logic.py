# -*- coding: utf-8 -*-

"""
LoginLogic module

This module is the business logic for writing user-specific configuration
information to the user's machine
"""

# Builtins
import logging

# Internals
from conjur.api.endpoints import ConjurEndpoint
from conjur.errors import CertificateVerificationException
from conjur.interface.credentials_store_interface import CredentialsStoreInterface
from conjur.wrapper.http_wrapper import invoke_endpoint, HttpVerb

class LoginLogic:
    """
    LoginLogic

    This class holds the business logic for populating the
    netrc configuration details needed to login to Conjur
    """
    def __init__(self, credentials_provider: CredentialsStoreInterface):
        self.credentials_provider = credentials_provider

    @classmethod
    # pylint: disable=line-too-long,logging-fstring-interpolation
    def get_api_key(cls, ssl_verify:bool, credential_data, password:str, conjurrc):
        """
        Method to fetch the user/host's API key from Conjur
        """
        params = {
            'url': conjurrc.conjur_url,
            'account': conjurrc.conjur_account
        }

        if ssl_verify is False:
            certificate_path = False
        elif ssl_verify and credential_data.machine.startswith("https"):
            # Catches the case where a user does not run in insecure mode but the
            # .conjurrc cert_file entry is empty
            if conjurrc.cert_file == '' and ssl_verify:
                raise CertificateVerificationException

            certificate_path = conjurrc.cert_file

        # pylint: disable=logging-fstring-interpolation
        logging.debug(f"Attempting to fetch '{credential_data.login}' API key from Conjur...")
        api_key = invoke_endpoint(HttpVerb.GET,
                                  ConjurEndpoint.LOGIN,
                                  params,
                                  auth=(credential_data.login, password),
                                  ssl_verify=certificate_path).text

        logging.debug("API key retrieved from Conjur")
        return api_key

    def save(self, credential_data):
        """
        Method to save credentials during login
        """
        self.credentials_provider.save(credential_data)
