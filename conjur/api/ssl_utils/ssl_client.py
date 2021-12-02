# -*- coding: utf-8 -*-

"""
SSLClient module

This module is for all SSL operations
"""
# Builtin
from typing import Tuple
from socket import gaierror
import logging
import os
import socket

# Third party
from OpenSSL import SSL
from OpenSSL.crypto import FILETYPE_PEM, dump_certificate

# Internals
from conjur.api.ssl_utils.errors import TLSSocketConnectionException, TLSGeneralException
from conjur.api.ssl_utils.ssl_consts import CONJUR_TLS_METHODS



# pylint: disable=too-few-public-methods
class SSLClient:
    """
    SSLClient

    This class is a service for connecting to the Conjur socket
    and fetching the certificate
    """

    @classmethod
    def get_certificate(cls, hostname: str, port: int) -> Tuple[str, str]:
        """
        Method for connecting to Conjur to fetch the certificate chain
        """
        try:
            sock = cls.__connect(hostname, port)
            chain = sock.get_peer_cert_chain()
            fingerprint = chain[0].digest("sha1").decode("utf-8")
            # pylint: disable=line-too-long
            # Format the certificate chain to make it easier to later write to a file
            readable_certificate = "".join(
                [str(dump_certificate(FILETYPE_PEM, cert), "utf-8") for cert in chain])
            return fingerprint, readable_certificate
        except gaierror as socket_err:
            raise TLSSocketConnectionException(socket_err) from socket_err
        except Exception as err:
            raise TLSGeneralException(err) from err

    @classmethod
    # pylint: disable=unused-private-member
    def __connect(cls, hostname: str, port: int) -> SSL.Connection:
        """
        Method for opening a socket to the Conjur server
        """

        ctx = cls._get_ssl_context()
        # Taken from
        # https://gist.github.com/brandond/f3d28734a40c49833176207b17a44786#file-sslscan-py-L17
        conjur_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conjur_conn = SSL.Connection(context=ctx, socket=conjur_sock)
        conjur_conn.connect((hostname, port))
        # handle SNI
        conjur_conn.set_tlsext_host_name(hostname.encode())
        conjur_conn.do_handshake()

        logging.debug("TLS connection established. "
                      "Fetching certificate from Conjur server...")

        return conjur_conn

    @classmethod
    def _get_ssl_context(cls):
        tls_version = os.getenv('CONJUR_TLS_VERSION')
        # Makes the TLS version configurable through an ENV variable
        if tls_version in CONJUR_TLS_METHODS:
            # pylint: disable=logging-fstring-interpolation
            logging.debug("'CONJUR_TLS_VERSION' environment variable supplied. Establishing TLS "
                          f"v{tls_version} connection...")
            ctx = SSL.Context(method=CONJUR_TLS_METHODS[tls_version])
            if tls_version == '1.3':
                # disables all TLS versions expect for 1.3
                cls.disable_tls_versions(ctx, support_1_3=True)
        else:
            if tls_version:
                logging.debug("Warning: 'CONJUR_TLS_VERSION' environment variable supplied but "
                              "not in correct format (Example: CONJUR_TLS_VERSION=1.2)")
            # Despite its name, SSLv23_METHOD is the alias for PROTOCOL_TLS which allows for
            # negotiation between different TLS versions and chooses the highest supported server
            # protocol. See https://docs.python.org/3/library/ssl.html#ssl.PROTOCOL_SSLv23
            # specifically PROTOCOL_SSLv23 and PROTOCOL_TLS
            ctx = SSL.Context(method=SSL.SSLv23_METHOD)
            # Using SSLv23 by default enables all types of negotiation and we want to limit
            # negotiation to only 1.2 and 1.3 versions
            cls.disable_tls_versions(ctx)
        return ctx

    @classmethod
    def disable_tls_versions(cls, ctx: SSL.Context, support_1_3: bool = False):
        """
        Method for disabling TLS/SSL versions
        """
        if support_1_3:
            # disable TLS 1.2 when user requires only 1.3
            ctx.set_options(SSL.OP_NO_TLSv1_2)

        ctx.set_options(SSL.OP_NO_SSLv2)
        ctx.set_options(SSL.OP_NO_SSLv3)
        ctx.set_options(SSL.OP_NO_TLSv1)
        ctx.set_options(SSL.OP_NO_TLSv1_1)
