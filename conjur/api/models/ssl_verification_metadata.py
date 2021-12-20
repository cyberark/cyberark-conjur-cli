"""
SslVerificationMetaData module
This module holds the SslVerificationData class

"""
from conjur.api.errors import BadInitializationException
from conjur.api.models.ssl_verification_mode import SslVerificationMode


# pylint: disable=too-few-public-methods
class SslVerificationMetadata:
    """
    A data class that is used by http_wrapper to preform TLS operations
    """

    def __init__(self, mode: SslVerificationMode, ca_cert_path: str = None):
        self.mode = mode
        self.ca_cert_path = ca_cert_path
        self._validate_input()

    @property
    def is_insecure_mode(self):
        """
        @return: True, if mode is NO_SSL
        """
        return self.mode == SslVerificationMode.NO_SSL

    @property
    def is_self_signed_mode(self):
        """
        @return: True, if mode is SELF_SIGN
        """
        return self.mode == SslVerificationMode.SELF_SIGN

    def _validate_input(self):
        requires_cert_options = [SslVerificationMode.WITH_CA_BUNDLE,
                                 SslVerificationMode.SELF_SIGN]
        if self.mode in requires_cert_options and not self.ca_cert_path:
            # TODO check if file exist and have read permissions
            raise BadInitializationException(
                f"SslVerificationMetaData was initialized incorrect with "
                f"mode: {self.mode} and ca_cert_path: {self.ca_cert_path}")

    def __eq__(self, other):
        return self.mode == other.mode and self.ca_cert_path == other.ca_cert_path

    def __repr__(self):
        return str(self.__dict__)
