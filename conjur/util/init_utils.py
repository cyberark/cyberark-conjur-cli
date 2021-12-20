"""
init_utils module
This module is used for helper methods for the init command
It functionality will move into the init_action once we implement the cli actions pattern
"""
# Builtins
import os

# Internals
from conjur.api.models import SslVerificationMetadata
from conjur.api.models import SslVerificationMode
from conjur.constants import DEFAULT_CERTIFICATE_FILE
from conjur.errors import MissingRequiredParameterException, FileNotFoundException, \
    InvalidFilePermissionsException


# TODO edit this with the new init command UX
def validate_init_action_ssl_verification_input(ca_path, is_self_signed, ssl_verify):
    """
    Validate the input related to ssl verification for the init action
    """
    use_ca_bundle = False
    if ca_path:
        use_ca_bundle = True
    options = [use_ca_bundle, is_self_signed, not ssl_verify]
    if sum(options) > 1:
        raise MissingRequiredParameterException("Can't accept more than one of the following "
                                                "arguments:"
                                                "\n1. --ca-cert"
                                                "\n2. --self-signed"
                                                "\n3. --insecure (skip certificate validation)")

    if use_ca_bundle:
        if not os.path.exists(ca_path):
            raise FileNotFoundException(
                f"Couldn't find '{ca_path}'. Make sure correct path is provided")

        try:
            # pylint: disable=unspecified-encoding
            with open(ca_path, 'r'):
                pass
        except Exception:
            # pylint: disable=raise-missing-from
            raise InvalidFilePermissionsException(f"No read access for: {ca_path}")


def get_ssl_verification_meta_data_from_cli_params(ca_path, is_self_signed,
                                                   ssl_verify) -> SslVerificationMetadata:
    """
    Create SslVerificationMetadata according to input
    @param ca_path:
    @param is_self_signed:
    @param ssl_verify:
    @return: SslVerificationMetadata
    """
    if ca_path:
        return SslVerificationMetadata(SslVerificationMode.WITH_CA_BUNDLE, ca_path)
    if is_self_signed:
        return SslVerificationMetadata(SslVerificationMode.SELF_SIGN, DEFAULT_CERTIFICATE_FILE)
    if not ssl_verify:
        return SslVerificationMetadata(SslVerificationMode.NO_SSL)
    return SslVerificationMetadata(SslVerificationMode.WITH_TRUST_STORE)
