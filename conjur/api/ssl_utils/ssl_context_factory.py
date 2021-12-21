# -*- coding: utf-8 -*-

"""
SslContextFactory module
This module job is to encapsulate the creation of SSLContext in the dependent of each os environment
"""

# Builtin
import logging
import ssl
import subprocess
import platform
from functools import lru_cache

# Internals
from conjur.api.models import SslVerificationMetadata, SslVerificationMode
from conjur.errors import UnknownOSError, MacCertificatesError
from conjur.util.os_types import OSTypes
from conjur.util.util_functions import get_current_os


# pylint: disable=too-few-public-methods
def create_ssl_context(ssl_verification_metadata: SslVerificationMetadata) -> ssl.SSLContext:
    """
    Factory method to create SSLContext loaded with system RootCA's
    @return: SSLContext configured with the system certificates
    """
    os_name = platform.system()

    if ssl_verification_metadata.mode == SslVerificationMode.TRUST_STORE:
        logging.debug("Creating SSLContext from OS TrustStore for '%s'", os_name)

        current_os = get_current_os()
        if current_os == OSTypes.MAC_OS:
            ssl_context = ssl.create_default_context(cadata=_get_mac_ca_certs())
        elif current_os in (OSTypes.LINUX, OSTypes.WINDOWS):
            ssl_context = ssl.create_default_context()
        else:
            raise UnknownOSError(f"Cannot find CA certificates for OS '{os_name}'")
    else:
        ssl_context = ssl.create_default_context(cafile=ssl_verification_metadata.ca_cert_path)

    ssl_context.minimum_version = ssl.TLSVersion.TLSv1_2
    # pylint: disable=no-member
    ssl_context.verify_flags |= ssl.OP_NO_TICKET

    logging.debug("SSLContext created successfully")

    return ssl_context


@lru_cache
def _get_mac_ca_certs() -> str:
    """ Get Root CAs from mac Keychain. """
    logging.debug("Get CA certs from mac keychain")

    try:
        get_ca_certs_process = subprocess.run(
            ["security", "find-certificate", "-a", "-p", "/System/Library/Keychains/SystemRootCertificates.keychain"],
            capture_output=True,
            timeout=10,
            check=True,
            text=True)
        return get_ca_certs_process.stdout
    except Exception as ex:
        raise MacCertificatesError() from ex
