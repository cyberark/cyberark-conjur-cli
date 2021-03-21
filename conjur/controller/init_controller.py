# -*- coding: utf-8 -*-

"""
InitController module

This module is the controller that facilitates all init actions
required to successfully configure the conjurrc
"""

# Builtins
import logging
import sys

# Third party
from urllib.parse import urlparse

# Internals
from conjur.constants import DEFAULT_CERTIFICATE_FILE, DEFAULT_CONFIG_FILE, VALID_CONFIRMATIONS
from conjur.errors import CertificateHostnameMismatchException
from conjur.util import util_functions

class InitController:
    """
    InitController

    This class represents the Presentation Layer for the INIT command
    """
    force_overwrite = False
    conjurrc_data = None
    init_logic = None

    def __init__(self, conjurrc_data, init_logic, force, ssl_verify):
        self.ssl_verify = ssl_verify
        if self.ssl_verify is False:
            util_functions.get_insecure_warning()

        self.conjurrc_data = conjurrc_data
        self.init_logic = init_logic
        self.force_overwrite = force

    def load(self):
        """
        Method that facilitates all method calls in this class
        """
        if self.ssl_verify is True:
            fetched_certificate = self.get_server_certificate()
            # For a uniform experience, regardless if the certificate is self-signed
            # or CA-signed, we will write the certificate on the machine
            self.write_certificate(fetched_certificate)
        else:
            self.conjurrc_data.cert_file=""

        self.get_account_info(self.conjurrc_data)
        self.write_conjurrc()

        sys.stdout.write("Configuration was initialized successfully.\n")
        sys.stdout.write("To begin using the Conjur CLI, log in to the Conjur server by "
                         "running `conjur login`\n")

    def get_server_certificate(self):
        """
        Method to get the certificate from the Conjur endpoint detailed by the user
        """
        # pylint: disable=line-too-long
        if self.conjurrc_data.conjur_url is None:
            self.conjurrc_data.conjur_url = input("Enter the URL of your Conjur server (use HTTPS prefix): ").strip()
            if self.conjurrc_data.conjur_url == '':
                # pylint: disable=raise-missing-from
                raise RuntimeError("Error: URL is required")

        # Chops off the '/ if supplied by the user to avoid a server error
        if self.conjurrc_data.conjur_url.endswith('/'):
            self.conjurrc_data.conjur_url=self.conjurrc_data.conjur_url[:-1]

        url = urlparse(self.conjurrc_data.conjur_url)

        # TODO: Factor out the following URL validation to ConjurrcData class
        # and add integration tests
        if url.scheme != 'https':
            raise RuntimeError(f"Error: undefined behavior. Reason: The Conjur URL format provided "
                   f"'{self.conjurrc_data.conjur_url}' is not supported.")

        if self.conjurrc_data.cert_file is not None:
            # Return None because we do not need to fetch the certificate
            return None

        # pylint: disable=logging-fstring-interpolation
        logging.debug(f"Initiating a TLS connection with '{self.conjurrc_data.conjur_url}'...")
        fingerprint, fetched_certificate = self.init_logic.get_certificate(url.hostname, url.port)

        sys.stdout.write(f"\nThe Conjur server's certificate SHA-1 fingerprint is:\n{fingerprint}\n")
        sys.stdout.write("\nTo verify this certificate, it is recommended to run the following "
                         "command on the Conjur server:\n"
                         "openssl x509 -fingerprint -noout -in ~conjur/etc/ssl/conjur.pem\n\n")
        trust_certificate = input("Trust this certificate? (Default=no): ").strip()
        if trust_certificate.lower() not in VALID_CONFIRMATIONS:
            raise RuntimeError("You decided not to trust the certificate")

        return fetched_certificate

    # pylint: disable=line-too-long,logging-fstring-interpolation,broad-except,raise-missing-from
    def get_account_info(self, conjurrc_data):
        """
        Method to fetch the account from the user
        """
        if conjurrc_data.conjur_account is None:
            try:
                self.init_logic.fetch_account_from_server(self.conjurrc_data)
            except CertificateHostnameMismatchException:
                raise
            except Exception as error:
                # Check for catching if the endpoint is exists. If the endpoint does not exist,
                # a 401 status code will be returned.
                # If the endpoint does not exist, the user will be prompted to enter in their account.
                # pylint: disable=no-member
                if hasattr(error.response, 'status_code') and str(error.response.status_code) == '401':
                    conjurrc_data.conjur_account = input("Enter the Conjur account name (required): ").strip()
                    if conjurrc_data.conjur_account is None or conjurrc_data.conjur_account == '':
                        raise RuntimeError("Error: account is required")
                else:
                    raise

    def write_certificate(self, fetched_certificate):
        """
        Method to write the certificate fetched from the Conjur endpoint on the user's machine
        """
        url = urlparse(self.conjurrc_data.conjur_url)
        # pylint: disable=line-too-long
        if self.conjurrc_data.cert_file is None and url.scheme == "https":
            self.conjurrc_data.cert_file = DEFAULT_CERTIFICATE_FILE
            is_file_written = self.init_logic.write_certificate_to_file(fetched_certificate,
                                                                       self.conjurrc_data.cert_file,
                                                                       self.force_overwrite)
            if not is_file_written:
                self.ensure_overwrite_file(self.conjurrc_data.cert_file)
                self.init_logic.write_certificate_to_file(fetched_certificate,
                                                          self.conjurrc_data.cert_file,
                                                          True)

            sys.stdout.write(f"Certificate written to {DEFAULT_CERTIFICATE_FILE}\n\n")

    def write_conjurrc(self):
        """
        Method to write the conjurrc configuration on the user's machine
        """
        is_file_written = self.init_logic.write_conjurrc(DEFAULT_CONFIG_FILE,
                                                         self.conjurrc_data,
                                                         self.force_overwrite)
        if not is_file_written:
            self.ensure_overwrite_file(DEFAULT_CONFIG_FILE)
            self.init_logic.write_conjurrc(DEFAULT_CONFIG_FILE,
                                           self.conjurrc_data,
                                           True)
        sys.stdout.write(f"Configuration written to {DEFAULT_CONFIG_FILE}\n\n")

    @classmethod
    def ensure_overwrite_file(cls, config_file):
        """
        Method to handle user overwriting logic
        """
        force_overwrite = input(f"File {config_file} exists. "
                                f"Overwrite? (Default=yes): ").strip()
        if force_overwrite != '' and force_overwrite.lower() not in VALID_CONFIRMATIONS:
            raise Exception(f"Not overwriting {config_file}")
