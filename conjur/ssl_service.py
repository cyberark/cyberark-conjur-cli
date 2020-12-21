# -*- coding: utf-8 -*-

"""
SSLService module

This module is for all SSL operations
"""
# Third party
import logging
import socket
from OpenSSL import SSL
from OpenSSL.crypto import FILETYPE_PEM, dump_certificate

DEFAULT_PORT = 443

class SSLService:
    """
    SSLHelper
    This class is a service for connecting to the Conjur socket
    and fetching the certificate
    ...
    """
    @staticmethod
    def connect(hostname, port):
        """
        Method for opening a socket to the Conjur server
        """
        ctx = SSL.Context(method=SSL.TLSv1_2_METHOD)
        # We set the following to false because we want to fetch the
        # certificates and not use them to validate yet
        ctx.check_hostname = False
        ctx.verify_mode = False

        conjur_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conjur_sock = SSL.Connection(context=ctx, socket=conjur_sock)
        conjur_sock.connect((hostname, port))
        conjur_sock.do_handshake()

        logging.info("TLS Connection established. " \
                     "Fetching certificate from server...")

        return conjur_sock

    def get_certificate(self, hostname, port):
        """
        Method for connecting to Conjur to fetch the certificate chain
        """
        sock = self.connect(hostname, port)
        chain = sock.get_peer_cert_chain()
        cert = chain[0]
        fingerprint = cert.digest("sha1").decode("utf-8")
        # pylint: disable=line-too-long
        # Format the certificate chain to make it easier to later write to a file
        readable_certificate = "".join([str(dump_certificate(FILETYPE_PEM, cert), "utf-8") for cert in chain])

        return fingerprint, readable_certificate
