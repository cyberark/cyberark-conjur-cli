# -*- coding: utf-8 -*-

"""
SSLService module

This module is for all SSL operations
"""
# Third party
import logging
import os
import socket
from OpenSSL import SSL
from OpenSSL.crypto import FILETYPE_PEM, dump_certificate

_tls_methods = {
    "1.0": SSL.TLSv1_METHOD,
    "1.1": SSL.TLSv1_1_METHOD,
    "1.2": SSL.TLSv1_2_METHOD
}

# pylint: disable=too-few-public-methods
class SSLService:
    """
    SSLService

    This class is a service for connecting to the Conjur socket
    and fetching the certificate
    """
    @classmethod
    def get_certificate(cls, hostname, port):
        """
        Method for connecting to Conjur to fetch the certificate chain
        """
        sock = cls.__connect(hostname, port)
        chain = sock.get_peer_cert_chain()
        fingerprint = chain[0].digest("sha1").decode("utf-8")
        # pylint: disable=line-too-long
        # Format the certificate chain to make it easier to later write to a file
        readable_certificate = "".join([str(dump_certificate(FILETYPE_PEM, cert), "utf-8") for cert in chain])
        return fingerprint, readable_certificate

    @classmethod
    def __connect(cls, hostname, port):
        """
        Method for opening a socket to the Conjur server
        """
        # Makes the TLS version configurable through an ENV variable
        if os.getenv('TLS_VERSION') in _tls_methods:
            ctx = SSL.Context(method=_tls_methods[os.getenv('TLS_VERSION')])
        else:
            # Despite its name, SSLv23_METHOD is the alias for PROTOCOL_TLS which allows for
            # negotiation between different TLS versions and chooses the highest supported server
            # protocol. See https://docs.python.org/3/library/ssl.html#ssl.PROTOCOL_SSLv23
            # specifically PROTOCOL_SSLv23 and PROTOCOL_TLS
            ctx = SSL.Context(method=SSL.SSLv23_METHOD)
            # Using SSLv23 by default enables all types of negotiation and we want to limit
            # negotiation to only 1.2 and 1.3 versions
            ctx.set_options(SSL.OP_NO_SSLv2)
            ctx.set_options(SSL.OP_NO_SSLv3)
            ctx.set_options(SSL.OP_NO_TLSv1)
            ctx.set_options(SSL.OP_NO_TLSv1_1)

        # We set the following to false because we want to fetch the
        # certificates and not use them to validate yet
        ctx.check_hostname = False
        ctx.verify_mode = False
        # pylint: disable = line-too-long
        # Taken from https://gist.github.com/brandond/f3d28734a40c49833176207b17a44786#file-sslscan-py-L17
        conjur_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conjur_sock = SSL.Connection(context=ctx, socket=conjur_sock)
        conjur_sock.connect((hostname, port))
        conjur_sock.do_handshake()

        logging.debug("TLS connection established. " \
                      "Fetching certificate from Conjur server")

        return conjur_sock
