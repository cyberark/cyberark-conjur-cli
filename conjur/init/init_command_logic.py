# -*- coding: utf-8 -*-

"""
InitCommandLogic module

This module is the business logic for writing configuration information
to the user's machine as well as fetching certificates from Conjur
"""

# Builtins
import logging
import sys
import os.path

# Third party
import yaml

DEFAULT_PORT = 443

# pylint: disable=raise-missing-from
class InitCommandLogic:
    """
    InitCommandLogic

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
            logging.info("Certificates were fetched successfully")
        except Exception as error:
            raise Exception(f"Unable to retrieve certificate from {hostname}:{port}. " \
                            f"Reason: {str(error)}") from error

        return fingerprint, readable_certificate

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
