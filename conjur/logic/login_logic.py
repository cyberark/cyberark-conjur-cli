# -*- coding: utf-8 -*-

"""
LoginLogic module

This module is the business logic for writing user-specific configuration
information to the user's machine
"""

# Builtins
import logging

# SDK
from conjur_api import Client
from conjur_api.models import SslVerificationMetadata, CredentialsData
from conjur_api.interface import CredentialsProviderInterface
from conjur_api.providers import SimpleCredentialsProvider

# Internals
from conjur.errors import CertificateVerificationException, HttpSslError
from conjur.data_object import ConjurrcData


class LoginLogic:
    """
    LoginLogic

    This class holds the business logic for populating the
    netrc configuration details needed to login to Conjur
    """

    def __init__(self, credentials_provider: CredentialsProviderInterface):
        self.credentials_provider = credentials_provider

    # pylint: disable=logging-fstring-interpolation
    def get_api_key(self,
                    ssl_verification_metadata: SslVerificationMetadata,
                    credential_data: CredentialsData,
                    password: str,
                    conjurrc: ConjurrcData) -> str:
        """
        Method to fetch the user/host's API key from Conjur
        """
        # pylint: disable=logging-fstring-interpolation,raise-missing-from
        logging.debug(f"Attempting to fetch '{credential_data.username}' API key from Conjur...")
        try:
            credentials_provider = SimpleCredentialsProvider()
            credentials_provider.save(CredentialsData(machine=conjurrc.conjur_url,
                                                      username=credential_data.username,
                                                      password=password))
            client = Client(conjurrc_data=conjurrc,
                            ssl_verification_mode=ssl_verification_metadata.mode,
                            credentials_provider=credentials_provider)
            api_key = client.login()
        except HttpSslError:
            if not conjurrc.cert_file and not ssl_verification_metadata.is_insecure_mode:
                raise CertificateVerificationException
        logging.debug("API key retrieved from Conjur")
        return api_key

    def save(self, credential_data: CredentialsData):
        """
        Method to save credentials during login
        """
        self.credentials_provider.save(credential_data)
