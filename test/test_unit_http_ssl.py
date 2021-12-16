import ssl
import unittest

from enum import Enum
from typing import Union
from unittest.mock import patch, call, MagicMock

from aiohttp import ClientSSLError
from aiohttp.client_reqrep import ConnectionKey
from asynctest import CoroutineMock, patch

from aiohttp import BasicAuth

from conjur.errors import HttpSslError, CertificateHostnameMismatchException
from conjur.wrapper.http_wrapper import HttpVerb, invoke_endpoint

from unittest import TestCase

invalid_badssl_endpoints = [
    "https://expired.badssl.com",
    "https://incomplete-chain.badssl.com",
    # "https://invalid-expected-sct.badssl.com",
    # "https://known-interception.badssl.com",
    "https://no-common-name.badssl.com",
    # "https://no-sct.badssl.com",
    "https://no-subject.badssl.com",
    # "https://pinning-test.badssl.com",  # Currently supported but shouldn't.
    "https://reversed-chain.badssl.com",
    # "https://revoked.badssl.com",  # Currently supported but shouldn't.
    "https://self-signed.badssl.com",
    "https://untrusted-root.badssl.com",
    "https://wrong.host.badssl.com",
    "https://dh-composite.badssl.com",
    "https://dh1024.badssl.com",
    "https://dh480.badssl.com",
    "https://dh512.badssl.com",
    # "https://static-rsa.badssl.com",  # Currently supported but shouldn't.
    # "https://ssl-v2.badssl.com",
    # "https://ssl-v3.badssl.com",
    # "https://tls-v1-0.badssl.com",
    # "https://tls-v1-1.badssl.com",
    "https://3des.badssl.com",
    "https://null.badssl.com",
    "https://rc4-md5.badssl.com",
    "https://rc4.badssl.com"
]

valid_badssl_endpoints = [
    "https://ecc256.badssl.com",
    "https://ecc384.badssl.com",
    "https://extended-validation.badssl.com",
    "https://rsa2048.badssl.com",
    "https://rsa4096.badssl.com",
    "https://rsa8192.badssl.com",
    "https://sha256.badssl.com",
    "https://sha384.badssl.com",
    "https://sha512.badssl.com",
    # "https://tls-v1-2.badssl.com",
    "https://cbc.badssl.com"
]


class TestDemonstrateSubtest(TestCase):
    class MockEndpoint(Enum):
        BADSSL_URL = "{url}"

    def test_http_wrapper_get_invalid_badssl_endpoints_throws_ssl_exception(self):
        for badssl_url in invalid_badssl_endpoints:
            with self.subTest(msg=f"Validate SSL cert of '{badssl_url}' is not valid"):
                expected_exceptions = (HttpSslError, CertificateHostnameMismatchException)
                with self.assertRaises(expected_exceptions):
                    invoke_endpoint(HttpVerb.GET,
                                    endpoint=self.MockEndpoint.BADSSL_URL,
                                    params={'url': badssl_url},
                                    ssl_verify=True,
                                    check_errors=False)

    def test_http_wrapper_get_valid_badssl_endpoints_successfully(self):
        for badssl_url in valid_badssl_endpoints:
            with self.subTest(msg=f"Validate SSL cert of '{badssl_url}' is valid"):
                invoke_endpoint(HttpVerb.GET,
                                endpoint=self.MockEndpoint.BADSSL_URL,
                                params={'url': badssl_url},
                                ssl_verify=True,
                                check_errors=False)
