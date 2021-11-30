"""
init_utils module
This module is used for helper methods for the init command
It functionality will move into the init_action once we implement the cli actions pattern
"""
# Builtins
import os

# Internals
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
        raise MissingRequiredParameterException("SSL verification method can be one of three:"
                                                "\n1. --ca-cert with '< Full path to RootCA PEM"
                                                " file >' (recommended)"
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
            raise InvalidFilePermissionsException(f"No read access for: {ca_path}")
