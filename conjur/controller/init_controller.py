# -*- coding: utf-8 -*-

"""
InitController module

This module is the controller that facilitates all init actions
required to successfully configure the conjurrc
"""

# Builtins
import http
import logging
import sys

# Third party
from urllib.parse import urlparse
from urllib.parse import ParseResult

# SDK
from conjur_api.models import SslVerificationMetadata, SslVerificationMode

# Internals
from typing import Optional

from conjur.constants import DEFAULT_CERTIFICATE_FILE, DEFAULT_CONFIG_FILE, VALID_CONFIRMATIONS
from conjur.errors import InvalidURLFormatException, CertificateNotTrustedException, ConfirmationException, \
    MissingRequiredParameterException, OperationNotCompletedException, HttpStatusError, HttpSslError
from conjur.util import util_functions
from conjur.data_object import ConjurrcData
from conjur.logic.init_logic import InitLogic


class InitController:
    """
    InitController

    This class represents the Presentation Layer for the INIT command
    """
    force_overwrite = False
    conjurrc_data = None
    init_logic = None

    def __init__(self, conjurrc_data: ConjurrcData, init_logic: InitLogic, force: bool,
                 ssl_verification_data: SslVerificationMetadata):
        self.ssl_verification_data = ssl_verification_data

        if self.ssl_verification_data.is_insecure_mode:
            util_functions.get_insecure_warning_in_debug()
            util_functions.get_insecure_warning_in_warning()

        if self.ssl_verification_data.is_self_signed_mode:
            self._prompt_warning_for_self_signed_flow()

        self.conjurrc_data = conjurrc_data
        self.init_logic = init_logic
        self.force_overwrite = force

    def load(self):
        """
        Method that facilitates all method calls in this class
        In more details this function job is to create the conjurrcData object and write it to disk
        """
        if self.conjurrc_data.conjur_url is None:
            self.conjurrc_data.conjur_url = self._prompt_for_conjur_url()
        formatted_conjur_url = self._format_conjur_url()

        self._validate_conjur_url(formatted_conjur_url)

        self._fetch_certificate_if_needed_and_update_conjurrc(formatted_conjur_url)
        self._get_account_info_if_not_exist()
        self.write_conjurrc()
        sys.stdout.write("Successfully initialized the Conjur CLI\n")

    def _fetch_certificate_if_needed_and_update_conjurrc(self, formatted_conjur_url):
        mode = self.ssl_verification_data.mode
        if mode == SslVerificationMode.CA_BUNDLE:
            self.conjurrc_data.cert_file = self.ssl_verification_data.ca_cert_path
        elif mode == SslVerificationMode.SELF_SIGN:
            fetched_certificate = self._get_server_certificate(formatted_conjur_url)
            self._write_certificate(fetched_certificate)
        elif mode in [SslVerificationMode.INSECURE, SslVerificationMode.TRUST_STORE]:
            self.conjurrc_data.cert_file = ""

    def _prompt_for_conjur_url(self):
        """
        Method to get the Conjur server URL if not provided
        """
        # pylint: disable=line-too-long
        if self.conjurrc_data.conjur_url is None:
            conjur_url = input(
                "Enter the URL of your Conjur server (use HTTPS prefix): ").strip()
            if conjur_url == '':
                # pylint: disable=raise-missing-from
                raise InvalidURLFormatException("Error: URL is required")
        return conjur_url

    # TODO: Factor out the following URL validation to ConjurrcData class
    def _format_conjur_url(self) -> ParseResult:
        """
        Method for formatting the Conjur server URL to
        break down the URL into segments
        """
        # Chops off the '/ if supplied by the user to avoid a server error
        if self.conjurrc_data.conjur_url.endswith('/'):
            self.conjurrc_data.conjur_url = self.conjurrc_data.conjur_url[:-1]

        return urlparse(self.conjurrc_data.conjur_url)

    def _validate_conjur_url(self, conjur_url: ParseResult):
        """
        Validates the specified url

        Raises a RuntimeError in case of an invalid url format
        """
        valid_schema = ['https']
        if self.ssl_verification_data.is_insecure_mode:
            valid_schema += ['http']
        if conjur_url.scheme not in valid_schema:
            raise InvalidURLFormatException(f"Error: undefined behavior. "
                                            f" Reason: The Conjur URL format provided. "
                                            f"'{self.conjurrc_data.conjur_url}' is not supported.")

    # pylint: disable=line-too-long
    def _get_server_certificate(self, conjur_url: ParseResult) -> Optional[str]:
        """
        Get the certificate from the specified conjur_url

        Returns:
            tuple of certificate fingerprint and certificate chains or
            None if the user provided a certificate
        """
        if self.conjurrc_data.cert_file is not None:
            # Return None because we do not need to fetch the certificate
            return None

        # pylint: disable=logging-fstring-interpolation
        logging.debug(f"Initiating a TLS connection with '{self.conjurrc_data.conjur_url}'...")
        fingerprint, fetched_certificate = self.init_logic.get_certificate(conjur_url.hostname,
                                                                           conjur_url.port)

        sys.stdout.write(
            f"\nThe Conjur server's certificate SHA-1 fingerprint is:\n{fingerprint}\n")
        sys.stdout.write("\nTo verify this certificate, we recommend running the following "
                         "command on the Conjur server:\n"
                         "openssl x509 -fingerprint -noout -in ~conjur/etc/ssl/conjur.pem\n\n")
        trust_certificate = input("Trust this certificate? yes/no (Default: no): ").strip()
        if trust_certificate.lower() not in VALID_CONFIRMATIONS:
            raise CertificateNotTrustedException("You decided not to trust the certificate")

        return fetched_certificate

    # pylint: disable=line-too-long,logging-fstring-interpolation,broad-except,raise-missing-from
    def _get_account_info_if_not_exist(self):
        """
        Method to fetch the account from the user
        """
        if self.conjurrc_data.conjur_account is None:
            try:
                self.init_logic.fetch_account_from_server(self.conjurrc_data, self.ssl_verification_data)
            except HttpSslError as ssl_err:
                raise HttpSslError("SSL Error. Make sure Conjur "
                                   "server's root certificate is trusted in this machine. "
                                   "If this problem continues, visit docs for more help") from ssl_err
            except HttpStatusError as error:
                # Check for catching if the endpoint is exists. If the endpoint does not exist,
                # a 401 status code will be returned.
                # If the endpoint does not exist, the user will be prompted to enter in their account.
                if error.status == http.HTTPStatus.UNAUTHORIZED:
                    self.conjurrc_data.conjur_account = input(
                        "Enter the Conjur account name (required): ").strip()
                    if self.conjurrc_data.conjur_account is None or self.conjurrc_data.conjur_account == '':
                        raise MissingRequiredParameterException("Error: account is required")
                else:
                    raise

    def _write_certificate(self, fetched_certificate: str):
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

    @staticmethod
    def _prompt_warning_for_self_signed_flow():
        user_answer = input("Using self-signed certificates is not recommended and could lead to "
                            "exposure of sensitive data.\n Continue? yes/no (Default: no): ").strip()
        if user_answer.lower() not in VALID_CONFIRMATIONS:
            raise OperationNotCompletedException(
                "User chose not to use self-signed certificate")

    @classmethod
    def ensure_overwrite_file(cls, config_file: str):
        """
        Method to handle user overwriting logic
        """
        force_overwrite = input(f"File {config_file} exists. "
                                f"Overwrite? yes/no (Default: yes): ").strip()
        if force_overwrite != '' and force_overwrite.lower() not in VALID_CONFIRMATIONS:
            raise ConfirmationException(f"Not overwriting {config_file}")
