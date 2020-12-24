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
import conjur.constants

class InitController:
    """
    InitController

    This class represents the Presentation Layer for the init command
    """
    force_overwrite = False
    conjurrc_data = None
    init_logic = None

    def __init__(self, conjurrc_data, init_logic, force):
        self.conjurrc_data = conjurrc_data
        self.init_logic = init_logic
        self.force_overwrite = force

    def load(self):
        """
        Method that facilitates all method calls in this class
        """
        fetched_certificate = self.get_server_certificate()
        self.write_certificate(fetched_certificate)

        self.get_account_info(self.conjurrc_data)

        self.write_conjurrc()

        sys.stdout.write("Configuration initialized successfully!\n")
        sys.stdout.write("To begin using the CLI, log in to the Conjur server by " \
                         "running `conjur login`\n")

    def get_server_certificate(self):
        """
        Method to get the certificate from the Conjur endpoint detailed by the user
        """
        # pylint: disable=line-too-long
        if self.conjurrc_data.appliance_url is None:
            self.conjurrc_data.appliance_url = input("Enter the URL of your Conjur server: ").strip()
            if self.conjurrc_data.appliance_url == '':
                # pylint: disable=raise-missing-from
                raise RuntimeError("Error: URL is required")


        url = urlparse(self.conjurrc_data.appliance_url)

        # TODO: Factor out the following URL validation to ConjurrcData class
        # and add integration tests
        # At this time, providing ports is not supported and
        # all urls must start with HTTPS.
        if url.port is not None or url.scheme != 'https':
            raise RuntimeError(f"Error: undefined behavior. Reason: The Conjur url format provided "
                   f"'{self.conjurrc_data.appliance_url}' is not supported. "
                   "Consider adding HTTPS as the prefix and remove the port if provided")

        if self.conjurrc_data.cert_file is not None:
            # Return None because we do not need to fetch the certificate
            return None

        # pylint: disable=logging-fstring-interpolation
        logging.debug(f"Initiating a TLS connection with '{self.conjurrc_data.appliance_url}'")
        fingerprint, fetched_certificate = self.init_logic.get_certificate(url.hostname, url.port)

        sys.stdout.write(f"\nThe server's certificate SHA-1 fingerprint is:\n{fingerprint}\n")
        sys.stdout.write("\nTo verify this certificate, it is recommended to run the following " \
                         "command on the Conjur server:\n" \
                         "openssl x509 -fingerprint -noout -in ~conjur/etc/ssl/conjur.pem\n\n")
        trust_certificate = input("Trust this certificate? [no]: ").strip()
        if trust_certificate.lower() != 'yes':
            raise RuntimeError("You decided not to trust the certificate")

        return fetched_certificate

    def get_account_info(self, conjurrc_data):
        """
        Method to fetch the account from the user
        """
        if conjurrc_data.account is None:
            try:
                self.init_logic.fetch_account_from_server(self.conjurrc_data)
            # pylint: disable=broad-except,logging-fstring-interpolation
            except Exception as error:
                # pylint: disable=line-too-long,logging-fstring-interpolation
                logging.debug(f"Unable to fetch the account from the Conjur server. Reason: {error}")
                # If there was a problem fetching the account from the server, we will request one
                conjurrc_data.account = input("Enter your organization account name: ").strip()

                if conjurrc_data.account is None or conjurrc_data.account == '':
                    # pylint: disable=raise-missing-from
                    raise RuntimeError("Error: account is required")

    def write_certificate(self, fetched_certificate):
        """
        Method to write the certificate fetched from the Conjur endpoint on the user's machine
        """
        url = urlparse(self.conjurrc_data.appliance_url)
        # pylint: disable=line-too-long
        if self.conjurrc_data.cert_file is None and url.scheme == "https":
            # pylint: disable=line-too-long
            self.conjurrc_data.cert_file = conjur.constants.DEFAULT_CERTIFICATE_FILE
            is_file_written = self.init_logic.write_certificate_to_file(fetched_certificate,
                                                                       self.conjurrc_data.cert_file,
                                                                       self.force_overwrite)
            if not is_file_written:
                self.__ensure_overwrite_file(self.conjurrc_data.cert_file)
                self.init_logic.write_certificate_to_file(fetched_certificate,
                                                          self.conjurrc_data.cert_file,
                                                          True)

            sys.stdout.write(f"Certificate written to {conjur.constants.DEFAULT_CERTIFICATE_FILE}\n\n")

    def write_conjurrc(self):
        """
        Method to write the conjurrc configuration on the user's machine
        """
        is_file_written = self.init_logic.write_conjurrc(conjur.constants.DEFAULT_CONFIG_FILE,
                                               self.conjurrc_data,
                                               self.force_overwrite)
        if not is_file_written:
            self.__ensure_overwrite_file(conjur.constants.DEFAULT_CONFIG_FILE)
            self.init_logic.write_conjurrc(conjur.constants.DEFAULT_CONFIG_FILE,
                                           self.conjurrc_data,
                                           True)
        sys.stdout.write(f"Configuration written to {conjur.constants.DEFAULT_CONFIG_FILE}\n\n")

    @staticmethod
    def __ensure_overwrite_file(config_file):
        force_overwrite = input(f"File {config_file} exists. " \
                                f"Overwrite? [yes]: ").strip()
        if force_overwrite != '' and force_overwrite.lower() != 'yes':
            raise Exception(f"Not overwriting {config_file}")
