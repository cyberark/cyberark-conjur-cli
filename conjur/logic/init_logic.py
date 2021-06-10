# -*- coding: utf-8 -*-

"""
InitLogic module

This module is the business logic for writing configuration information
to the user's machine as well as fetching certificates from Conjur
"""

# Builtins
import logging
import os.path
import socket
# Third party
import yaml

from conjur.constants import DEFAULT_CONFIG_FILE
from conjur.api.endpoints import ConjurEndpoint
from conjur.wrapper.http_wrapper import invoke_endpoint, HttpVerb
from conjur.api.ssl_client import SSLClient
from conjur.data_object import ConjurrcData

DEFAULT_PORT = 443

# pylint: disable=raise-missing-from
class InitLogic:
    """
    InitLogic

    This class holds the business logic for populating the
    conjurrc configuration details needed to connect to Conjur
    """
    def __init__(self, ssl_service:SSLClient):
        self.ssl_service = ssl_service

    def get_certificate(self, hostname:str, port):
        """
        Method for connecting to Conjur to fetch the certificate chain
        """
        if port is None:
            port = DEFAULT_PORT
        try:
            fingerprint, readable_certificate = self.ssl_service.get_certificate(hostname, port)
            logging.debug("Successfully fetched certificate")
        except socket.gaierror as error:
            raise ConnectionToConjurFailedException(f"Unable to resolve server DNS {hostnme}:{port}. "
                            f"Reason: {str(error)}") from error
        except socket.timeout as error:
            raise ConnectionToConjurFailedException(f"Unable to connect to server {hostnme}:{port}. "
                            f"Reason: {str(error)}") from error
        except Exception as error:
            raise RetrieveCertificateException(f"Unable to retrieve certificate from {hostname}:{port}. "
                            f"Reason: {str(error)}") from error

        return fingerprint, readable_certificate

    @classmethod
    def fetch_account_from_server(cls, conjurrc_data:ConjurrcData):
        """
        Fetches the account from the Conjur Enterprise server by making a
        request to the /info endpoint. This endpoint only exists in the
        Conjur Enterprise server
        """
        params = {
            'url': conjurrc_data.conjur_url
        }
        # If the user provides us with the certificate path, we will use it
        # to make a request to /info
        if conjurrc_data.cert_file is None and conjurrc_data.conjur_url.startswith("https"):
            certificate_path = os.path.join(os.path.dirname(DEFAULT_CONFIG_FILE),
                                          "conjur-server.pem")
        else:
            certificate_path = conjurrc_data.cert_file

        logging.debug("Attempting to fetch the account from the Conjur server...")
        response = invoke_endpoint(HttpVerb.GET,
                                   ConjurEndpoint.INFO,
                                   params,
                                   ssl_verify=certificate_path).json()
        conjurrc_data.conjur_account = response['configuration']['conjur']['account']

        # pylint: disable=logging-fstring-interpolation
        logging.debug(f"Account '{conjurrc_data.conjur_account}' "
                      "successfully fetched from the Conjur server")

    @classmethod
    def write_certificate_to_file(cls, fetched_certificate:str, cert_file_path:str,
            force_overwrite_flag:bool) -> bool :
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
    def write_conjurrc(cls, conjurrc_file_path:str, conjurrc_data:ConjurrcData,
                       force_overwrite_flag:bool) -> bool :
        """
        Method for writing the conjurrc configuration
        details needed to create a connection to Conjur
        """
        is_written = True
        if not force_overwrite_flag and os.path.exists(conjurrc_file_path):
            return not is_written

        with open(conjurrc_file_path, 'w') as config_fp:
            _pretty_print_object = {}

            # Ensures that there are no None fields written to conjurrc
            for attr,value in conjurrc_data.__dict__.items():
                _pretty_print_object[str(attr)] = value

            config_fp.write("---\n")
            yaml.dump(_pretty_print_object, config_fp)
        return is_written
