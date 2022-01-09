# -*- coding: utf-8 -*-

"""
InitLogic module

This module is the business logic for writing configuration information
to the user's machine as well as fetching certificates from Conjur
"""

# Builtins
import logging
import os.path

from conjur_sdk.models import SslVerificationMetadata
from conjur_sdk import Client
from conjur.util.ssl_utils.errors import TLSSocketConnectionException
from conjur.util.ssl_utils import SSLClient
from conjur.data_object import ConjurrcData
from conjur.errors import ConnectionToConjurFailedException, RetrieveCertificateException

DEFAULT_PORT = 443


# pylint: disable=raise-missing-from,unspecified-encoding
class InitLogic:
    """
    InitLogic

    This class holds the business logic for populating the
    conjurrc configuration details needed to connect to Conjur
    """

    def __init__(self, ssl_service: SSLClient):
        self.ssl_service = ssl_service

    def get_certificate(self, hostname: str, port):
        """
        Method for connecting to Conjur to fetch the certificate chain
        """
        if port is None:
            port = DEFAULT_PORT
        try:
            fingerprint, readable_certificate = self.ssl_service.get_certificate(hostname, port)
            logging.debug("Successfully fetched certificate")
        except TLSSocketConnectionException as error:
            raise ConnectionToConjurFailedException(f"Unable to resolve server DNS "
                                                    f"from {hostname}:{port}. "
                                                    f"Reason: {str(error)}") from error
        except TimeoutError as error:
            raise ConnectionToConjurFailedException(f"Unable to connect to server "
                                                    f"from {hostname}:{port}. "
                                                    f"Reason: {str(error)}") from error
        except Exception as error:
            raise RetrieveCertificateException(f"Unable to retrieve certificate "
                                               f"from {hostname}:{port}. "
                                               f"Reason: {str(error)}") from error

        return fingerprint, readable_certificate

    @classmethod
    def fetch_account_from_server(cls, conjurrc_data: ConjurrcData, ssl_verification_metadata: SslVerificationMetadata):
        """
        Fetches the account from the Conjur Enterprise server by making a
        request to the /info endpoint. This endpoint only exists in the
        Conjur Enterprise server
        """
        params = {
            'url': conjurrc_data.conjur_url
        }
        logging.debug("Attempting to fetch the account from the Conjur server...")
        client = Client(conjurrc_data=conjurrc_data, ssl_verification_mode=ssl_verification_metadata.mode)
        response = client.get_server_info()  # TODO implement in SDK
        conjurrc_data.conjur_account = response['configuration']['conjur']['account']

        # pylint: disable=logging-fstring-interpolation
        logging.debug(f"Account '{conjurrc_data.conjur_account}' "
                      "successfully fetched from the Conjur server")

    @classmethod
    def write_certificate_to_file(cls, fetched_certificate: str, cert_file_path: str,
                                  force_overwrite_flag: bool) -> bool:
        """
        Method for writing certificate to a file on the user's machine
        """
        is_written = True
        if not force_overwrite_flag and os.path.exists(cert_file_path):
            return not is_written

        if fetched_certificate is not None:
            with open(cert_file_path, 'w') as config_fp:
                config_fp.write(fetched_certificate)

        return is_written

    @classmethod
    def write_conjurrc(cls, conjurrc_file_path: str, conjurrc_data: ConjurrcData,
                       force_overwrite_flag: bool) -> bool:
        """
        Method for writing the conjurrc configuration
        details needed to create a connection to Conjur
        """
        if not force_overwrite_flag and os.path.exists(conjurrc_file_path):
            return False

        conjurrc_data.write_to_file(conjurrc_file_path)
        return True
