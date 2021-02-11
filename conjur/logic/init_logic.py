# -*- coding: utf-8 -*-

"""
InitLogic module

This module is the business logic for writing configuration information
to the user's machine as well as fetching certificates from Conjur
"""

# Builtins
import logging
import os.path

# Third party
import shutil

import requests
import yaml

from conjur.constants import DEFAULT_CONFIG_FILE, DEFAULT_CERTIFICATE_BUNDLE_FILE
from conjur.api.endpoints import ConjurEndpoint
from conjur.wrapper.http_wrapper import invoke_endpoint, HttpVerb

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
            logging.debug("Successfully fetched certificate")
        except Exception as error:
            raise Exception(f"Unable to retrieve certificate from {hostname}:{port}. " \
                            f"Reason: {str(error)}") from error

        return fingerprint, readable_certificate

    @staticmethod
    def fetch_account_from_server(conjurrc_data):
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
            certificate_path = os.path.join(os.path.dirname(DEFAULT_CONFIG_FILE),
                                          "conjur-server.pem")

        else:
            certificate_path = conjurrc_data.cert_file

        logging.debug("Attempting to fetch the account from the Conjur server")

        store = requests.certs.where()
        with open(certificate_path) as certificate_file:
                loaded_certificate = certificate_file.read()

        # We copy the contents of the CA bundle on the machine and append to it the certificate
        # that was fetched from the server so that certificate validation can take place.
        # We make a duplicate of the ca bundles to avoid changing the file system of the user.
        shutil.copy(store, DEFAULT_CERTIFICATE_BUNDLE_FILE)
        with open(DEFAULT_CERTIFICATE_BUNDLE_FILE, 'a') as bundle:
            bundle.write('\n'+loaded_certificate)

        response = invoke_endpoint(HttpVerb.GET,
                                   ConjurEndpoint.INFO,
                                   params,
                                   ssl_verify=DEFAULT_CERTIFICATE_BUNDLE_FILE).json()
        conjurrc_data.account = response['configuration']['conjur']['account']

        # pylint: disable=logging-fstring-interpolation
        logging.debug(f"Account '{conjurrc_data.account}' "\
                      "successfully fetched from the Conjur server")

    @classmethod
    def write_certificate_to_file(cls, fetched_certificate, cert_file_path, force_overwrite_flag):
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
    def write_conjurrc(cls, conjurrc_file_path, conjurrc_data, force_overwrite_flag):
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
                if value is not None:
                    _pretty_print_object[str(attr)]=value

            config_fp.write("---\n")
            yaml.dump(_pretty_print_object, config_fp)
        return is_written
