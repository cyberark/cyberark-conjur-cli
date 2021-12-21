import unittest

from conjur.api.models import SslVerificationMode
from conjur.constants import DEFAULT_CERTIFICATE_FILE
from conjur.util import util_functions as utils
from conjur.data_object import ConjurrcData


class UserInputDataTest(unittest.TestCase):

    def test_get_ssl_verification_meta_data_from_conjurrc_no_ssl(self):
        data = ConjurrcData(conjur_url="https://foo.com", account="some_account", cert_file="cert")
        res = utils.get_ssl_verification_meta_data_from_conjurrc(False, data)
        self.assertEquals(res.mode, SslVerificationMode.INSECURE)

    def test_get_ssl_verification_meta_data_from_conjurrc_self_sign(self):
        data = ConjurrcData(conjur_url="https://foo.com", account="some_account",
                            cert_file=DEFAULT_CERTIFICATE_FILE)
        res = utils.get_ssl_verification_meta_data_from_conjurrc(True, data)
        self.assertEquals(res.mode, SslVerificationMode.SELF_SIGN)

    def test_get_ssl_verification_meta_data_from_conjurrc_trust_store(self):
        data = ConjurrcData(conjur_url="https://foo.com", account="some_account", cert_file="")
        res = utils.get_ssl_verification_meta_data_from_conjurrc(True, data)
        self.assertEquals(res.mode, SslVerificationMode.TRUST_STORE)

    def test_get_ssl_verification_meta_data_from_conjurrc_ca_bundle(self):
        data = ConjurrcData(conjur_url="https://foo.com", account="some_account",
                            cert_file="cert")
        res = utils.get_ssl_verification_meta_data_from_conjurrc(True, data)
        self.assertEquals(res.mode, SslVerificationMode.CA_BUNDLE)
