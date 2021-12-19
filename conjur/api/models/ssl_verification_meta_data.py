"""
SslVerificationMetaData module
This module holds the SslVerificationData class

"""
from conjur.api.errors import BadInitializationException
from conjur.api.models.ssl_verification_mode import SslVerificationMode


class SslVerificationMetaData:
    """
    A data class that is used by http_wrapper to preform TLS operations
    """

    def __init__(self, mode: SslVerificationMode, ca_cert_path: str = None):
        self.mode = mode
        self.ca_cert_path = ca_cert_path
        self._validate_input(mode, ca_cert_path)

    @staticmethod
    def _validate_input(mode: SslVerificationMode, ca_cert_path: str):
        if mode in [SslVerificationMode.WITH_CA_BUNDLE,
                    SslVerificationMode.SELF_SIGN] and not ca_cert_path:
            raise BadInitializationException(
                f"SslVerificationMetaData was initialized incorrect with "
                f"mode: {mode} and ca_cert_path: {ca_cert_path}")
