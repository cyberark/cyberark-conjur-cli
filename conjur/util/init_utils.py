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
    InvalidFilePermissionsException, ConflictingParametersException


def validate_init_action_ssl_verification_input(ca_path, is_self_signed, ssl_verify):
    """
    Validate the input related to ssl verification for the init action
    """
    use_ca_bundle = False
    if ca_path:
        use_ca_bundle = True
    options = [use_ca_bundle, is_self_signed, not ssl_verify]
    if sum(options) > 1:
        raise ConflictingParametersException

    if use_ca_bundle:
        if not os.path.exists(ca_path):
            raise FileNotFoundException

        try:
            # pylint: disable=unspecified-encoding
            with open(ca_path, 'r'):
                pass
        except Exception:
            # pylint: disable=raise-missing-from
            raise InvalidFilePermissionsException


def get_ssl_verification_meta_data_from_cli_params(ca_path,
                                                   is_self_signed,
                                                   ssl_verify) -> SslVerificationMetadata:
    """
    Create SslVerificationMetadata according to input
    @param ca_path:
    @param is_self_signed:
    @param ssl_verify:
    @return: SslVerificationMetadata
    """
    if ca_path:
        return SslVerificationMetadata(SslVerificationMode.CA_BUNDLE, ca_path)
    if is_self_signed:
        return SslVerificationMetadata(SslVerificationMode.SELF_SIGN, DEFAULT_CERTIFICATE_FILE)
    if not ssl_verify:
        return SslVerificationMetadata(SslVerificationMode.INSECURE)
    return SslVerificationMetadata(SslVerificationMode.TRUST_STORE)
