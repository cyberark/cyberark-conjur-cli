from conjur.api.ssl_utils.ssl_context_factory import SslContextFactory
from unittest import TestCase


class TestSslContextFactory(TestCase):

    def test_ssl_context_constructed_with_certs(self):
        ctx = SslContextFactory.create_platform_specific_ssl_context()
        self.assertTrue(len(ctx.get_ca_certs()) > 0,
                        msg="SslContextFactory didn't create ctx with ca_certs configured ")
