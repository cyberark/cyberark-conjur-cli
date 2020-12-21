# -*- coding: utf-8 -*-

"""
InitController module

This module is the controller that facilitates all init actions
required to successfully configure the conjurrc
"""

# Builtins
import logging
import os
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
    init_command_logic = None

    def __init__(self, conjurrc_data, init_command_logic, force):
        self.conjurrc_data = conjurrc_data
        self.init_command_logic = init_command_logic
        self.force_overwrite = force

    def load(self):
        """
        Method that facilitates all method calls in this class
        """
        fetched_certificate = self.get_server_certificate()
        self.get_host_info(self.conjurrc_data)
        self.write_certificate(self.init_command_logic,
                               self.conjurrc_data,
                               self.conjurrc_data.cert_file,
                               fetched_certificate)
        self.init_command_logic.write_conjurrc(conjur.constants.DEFAULT_CONFIG_FILE,
                                       self.conjurrc_data,
                                       self.force_overwrite)
        sys.stdout.write("Configuration initialized successfully!\n")
        sys.stdout.write("To begin using the CLI, log in to the Conjur server by" \
                        "running `conjur authn login`")

    def get_server_certificate(self):
        """
        Method to get the certificate from the Conjur endpoint detailed by the user
        """
        # pylint: disable=line-too-long
        if not self.conjurrc_data.appliance_url:
            self.conjurrc_data.appliance_url = input("Enter the URL of your Conjur server: ")
        url = self.conjurrc_data.appliance_url

        self.conjurrc_data.appliance_url = ''.join(url)
        url = urlparse(self.conjurrc_data.appliance_url)

        # Fetch certificate information if connection is expected over TLS
        certificate_path = self.conjurrc_data.cert_file if self.conjurrc_data.cert_file else None
        if certificate_path is not None:
            self.conjurrc_data.cert_file = ''.join(certificate_path)

        if certificate_path is None and url.scheme == "https":
            logging.info("Initiating a TLS Connection")
            fingerprint, fetched_certificate = self.init_command_logic.get_certificate(url.hostname, url.port)
            sys.stdout.write(f"\nThe server's certificate SHA-1 fingerprint is:\n{fingerprint}\n")

            sys.stdout.write("\nTo verify this certificate, it is recommended to run the following" \
                            "command on the Conjur server:\n" \
                            "openssl x509 -fingerprint -noout -in ~conjur/etc/ssl/conjur.pem\n\n")
            trust_certificate = input("Trust this certificate? [no]: ")
            if trust_certificate.lower() != 'yes':
                raise ValueError("You decided not to trust the certificate")

            return fetched_certificate
        return None

    @staticmethod
    def get_host_info(conjurrc_data):
        """
        Method to hold data from the user
        """
        if not conjurrc_data.account:
            conjurrc_data.account = input("Enter your organization account name: ")
        else:
            conjurrc_data.account = ''.join(conjurrc_data.account)

        if not conjurrc_data.account:
            raise RuntimeError("Error: account is required")

    def write_certificate(self, init_command_logic,
                          conjurrc_data, certificate_path,
                          fetched_certificate):
        """
        Method to write the certificate fetched from the Conjur endpoint on the user's machine
        """
        url = urlparse(conjurrc_data.appliance_url)
        if certificate_path is None and url.scheme == "https":
            certificate_path = os.path.join(os.path.dirname(conjur.constants.DEFAULT_CONFIG_FILE),
                                            f"conjur-{conjurrc_data.account}.pem")
            conjurrc_data.cert_file = certificate_path
            init_command_logic.write_certificate_to_file(fetched_certificate,
                                                 certificate_path,
                                                 self.force_overwrite)
