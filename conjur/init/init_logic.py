# -*- coding: utf-8 -*-

"""
InitLogic module

This module is the business logic for writing configuration information
to the user's machine as well as fetching certificates from Conjur
"""

# Builtins
import logging
import sys
import os.path

# Third party
import yaml

import conjur.constants
from conjur.endpoints import ConjurEndpoint
from conjur.http import invoke_endpoint, HttpVerb

DEFAULT_PORT = 443

# pylint: disable=raise-missing-from
class InitLogic:
    """
    InitLogic

    This class holds the business logic for populating the
    conjurrc configuration details needed to connect to Conjur
    """
    def __init__(self, ssl_service):
        self.ssl_service = ssl_service

    def get_certificate(self, hostname, port):
        """
        Method for connecting to Conjur to fetch the certificate chain
        """
        if port is None:
            port = DEFAULT_PORT
        try:
            fingerprint, readable_certificate = self.ssl_service.get_certificate(hostname, port)
            logging.debug("Certificate were fetched successfully")
        except Exception as error:
            raise Exception(f"Unable to retrieve certificate from {hostname}:{port}. " \
                            f"Reason: {str(error)}") from error

        return fingerprint, readable_certificate

    @staticmethod
    def fetch_account_from_server(conjurrc_data, fetched_certificate):
        """
        Fetches the account from the DAP server by making a request to the /info endpoint.
        This endpoint only exists in the DAP server
        """
        params = {
            'url': conjurrc_data.appliance_url
        }
        # If the user provides us with the certificate path, we will use it
        # to make a request to /info
        if conjurrc_data.cert_file is None and conjurrc_data.appliance_url.startswith("https"):
            temp_cert_path = os.path.join(os.path.dirname(conjur.constants.DEFAULT_CONFIG_FILE),
                                          "conjur-client.pem")
            with open(temp_cert_path, 'w') as config_fp:
                config_fp.write(fetched_certificate)
        else:
            temp_cert_path = conjurrc_data.cert_file

        try:
            logging.debug("Attempting to fetch the account from the Conjur server")
            response = invoke_endpoint(HttpVerb.GET, ConjurEndpoint.INFO,
                                       params,
                                       ssl_verify=temp_cert_path).json()
            conjurrc_data.account = response['configuration']['conjur']['account']

            if conjurrc_data.cert_file is None:
                os.remove(temp_cert_path)
            # pylint: disable=logging-fstring-interpolation
            logging.debug(f"Account '{conjurrc_data.account}' "\
                          "successfully fetched from the Conjur server")
        # pylint: disable=broad-except
        except Exception:
            logging.debug("Unable to fetch the account from the Conjur server")
            # If there was a problem fetching the account from the server, we will request one
            conjurrc_data.account = input("Enter your organization account name: ")

    def write_certificate_to_file(self, fetched_certificate, cert_file_path, force_overwrite_flag):
        """
        Method for writing certificate details to a file on the user's machine
        """
        if fetched_certificate is not None:
            self._overwrite_file_if_exists(cert_file_path, force_overwrite_flag)
            with open(cert_file_path, 'w') as config_fp:
                config_fp.write(fetched_certificate)

            sys.stdout.write(f"Wrote certificate to {cert_file_path}\n\n")

    def write_conjurrc(self, conjurrc_file_path, conjurrc_data, force_overwrite_flag):
        """
        Method for writing the conjurrc configuration
        details needed to create a connection to Conjur
        """
        self._overwrite_file_if_exists(conjurrc_file_path, force_overwrite_flag)

        with open(conjurrc_file_path, 'w') as config_fp:
            _pretty_print_object = {}

            # Ensures that there are no None fields written to conjurrc
            for attr,value in conjurrc_data.__dict__.items():
                if value is not None:
                    _pretty_print_object[str(attr)]=value

            config_fp.write("---\n")
            yaml.dump(_pretty_print_object, config_fp)

        sys.stdout.write(f"Wrote configuration to {conjurrc_file_path}\n\n")

    @staticmethod
    def _overwrite_file_if_exists(config_file, force_overwrite_flag):
        if os.path.isfile(config_file) and force_overwrite_flag is False:
            force_overwrite = input(f"File {config_file} exists. " \
                                    f"Overwrite [yes]: ")
            if force_overwrite != '' and force_overwrite.lower() != 'yes':
                raise Exception(f"Not overwriting {config_file}")
