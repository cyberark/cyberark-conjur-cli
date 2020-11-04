import unittest

from conjur.endpoints import ConjurEndpoint


class EndpointsTest(unittest.TestCase):
    def test_endpoint_has_correct_authenticate_template_string(self):
        auth_endpoint = ConjurEndpoint.AUTHENTICATE.value.format(url='http://host',
                                                                 account='myacct',
                                                                 login='mylogin')
        self.assertEqual(auth_endpoint, 'http://host/authn/myacct/mylogin/authenticate')

    def test_endpoint_has_correct_login_template_string(self):
        auth_endpoint = ConjurEndpoint.LOGIN.value.format(url='http://host',
                                                          account='myacct')
        self.assertEqual(auth_endpoint, 'http://host/authn/myacct/login')

    def test_endpoint_has_correct_secrets_template_string(self):
        auth_endpoint = ConjurEndpoint.SECRETS.value.format(url='http://host',
                                                            account='myacct',
                                                            kind='varkind',
                                                            identifier='varid')
        self.assertEqual(auth_endpoint, 'http://host/secrets/myacct/varkind/varid')

    def test_endpoint_has_correct_batch_secrets_template_string(self):
        batch_endpoint = ConjurEndpoint.BATCH_SECRETS.value.format(url='http://host')
        self.assertEqual(batch_endpoint, 'http://host/secrets')

    def test_endpoint_has_correct_policy_template_string(self):
        auth_endpoint = ConjurEndpoint.POLICIES.value.format(url='http://host',
                                                             account='myacct',
                                                             identifier='polid')
        self.assertEqual(auth_endpoint, 'http://host/policies/myacct/policy/polid')

    def test_endpoint_has_correct_resources_template_string(self):
        auth_endpoint = ConjurEndpoint.RESOURCES.value.format(url='http://host',
                                                             account='myacct')
        self.assertEqual(auth_endpoint, 'http://host/resources/myacct')

    def test_endpoint_has_correct_whoami_template_string(self):
        auth_endpoint = ConjurEndpoint.WHOAMI.value.format(url='http://host',
                                                             account='myacct')
        self.assertEqual(auth_endpoint, 'http://host/whoami')
