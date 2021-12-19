# -*- coding: utf-8 -*-

"""
SslContextFactory module
This module job is to encapsulate the creation of SSLContext in the dependent of each os environment
"""

import logging
import ssl
from subprocess import Popen, PIPE
import platform
import os

from conjur.util.os_types import OSTypes
from conjur.util.util_functions import get_current_os


# pylint: disable=too-few-public-methods
class SslContextFactory:
    """
    Factory to create SSLContext object
    """

    @classmethod
    def create_platform_specific_ssl_context(cls) -> ssl.SSLContext:
        """
        Factory method to create SSLContext loaded with system RootCA's
        @return: SSLContext configured with the system certificates
        """
        ctx = ssl.create_default_context()
        if len(ctx.get_ca_certs()) > 0:
            return ctx
        current_platform = get_current_os()
        if current_platform == OSTypes.MAC_OS:
            cls._configure_ctx_for_mac(ctx)
        elif current_platform == OSTypes.LINUX:
            cls._configure_ctx_for_linux(ctx)
        elif current_platform == OSTypes.WINDOWS:
            # Windows certs should already be configured in SSLContext
            pass
        else:
            logging.debug("Platform %s not supported", platform.system())
        return ctx

    @staticmethod
    def _configure_ctx_for_mac(ctx):
        """
        load RootCA's to SSLContext in mac environment
        @param ctx:
        @return: ctx loaded with mac system RootCA's
        """
        mac_cmd_to_fetch_root_certificates = ["security",
                                              "find-certificate",
                                              "-a",
                                              "-p",
                                              "/System/Library/Keychains/SystemRootCertificates.keychain"]

        with Popen(mac_cmd_to_fetch_root_certificates, stdout=PIPE, stderr=PIPE) as process:
            stdout, _ = process.communicate()
            ctx.load_verify_locations(cadata=stdout.decode('unicode_escape'))

    @staticmethod
    def _configure_ctx_for_linux(ctx):
        """
        load RootCA's to SSLContext in linux environments
        @param ctx:
        @return: ctx loaded with mac system RootCA's
        """
        # Taken from https://golang.org/src/crypto/x509/root_linux.go
        certificate_file_locations = [
            "/etc/ssl/certs/ca-certificates.crt",  # Debian/Ubuntu/Gentoo etc.
            "/etc/pki/tls/certs/ca-bundle.crt",  # Fedora/RHEL 6
            "/etc/ssl/ca-bundle.pem",  # OpenSUSE
            "/etc/pki/tls/cacert.pem",  # OpenELEC
            "/etc/pki/ca-trust/extracted/pem/tls-ca-bundle.pem",  # CentOS/RHEL 7
            "/etc/ssl/cert.pem"  # Alpine Linux
        ]
        for file_path in certificate_file_locations:
            if os.path.isfile(file_path):
                ctx.load_verify_locations(cafile=file_path)
                break
