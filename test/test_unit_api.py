import json
import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock
from urllib import parse

from conjur_api.models import SslVerificationMetadata, SslVerificationMode, CreateTokenData
from conjur.constants import DEFAULT_CERTIFICATE_FILE

from conjur.data_object.conjurrc_data import ConjurrcData
from conjur.errors import MissingRequiredParameterException
from conjur.wrapper.http_wrapper import HttpVerb
from conjur.api.endpoints import ConjurEndpoint

from conjur.api import Api
from conjur.resource import Resource
from conjur.logic.credential_provider.file_credentials_provider import FileCredentialsProvider
from conjur.data_object.credentials_data import CredentialsData

MOCK_RESOURCE_LIST = [
    {
        'a': 'a value',
        'b': 'b value',
        'id': 'first:id',
        'c': 'c value',
    },
    {
        'x': 'x value',
        'y': 'y value',
        'id': 'second:id',
        'z': 'z value',
    },
]

MOCK_BATCH_GET_RESPONSE = '{"myaccount:variable:foo": "a", "myaccount:variable:bar": "b"}'
MOCK_POLICY_CHANGE_OBJECT = {
    "created_roles": {
        "myorg:user:alice": {
            "id": "myorg:user:alice",
            "api_key": "apikey1"
        },
        "myorg:user:bob": {
            "id": "myorg:user:bob",
            "api_key": "apikey2"
        }
    },
    "version": 4
}

MOCK_HOSTFACTORY_OBJECT = CreateTokenData(host_factory="some_host_factory", cidr="1.2.3.4,0.0.0.0",
                                          days=1)
MOCK_HOSTFACTORY_WITHOUT_CIDR_OBJECT = CreateTokenData(host_factory="some_host_factory", days=1)
MockCredentials = CredentialsData(login='myuser', password='mypass')


def create_api(url='http://localhost', account='default',
               ssl_verification_mode=SslVerificationMode.SELF_SIGN,
               cert_path=DEFAULT_CERTIFICATE_FILE):
    return Api(conjurrc_data=ConjurrcData(conjur_url=url, account=account, cert_file=cert_path),
               ssl_verification_mode=ssl_verification_mode,
               credentials_provider=FileCredentialsProvider())


def create_ssl_verification_metadata(ssl_verification_mode=SslVerificationMode.SELF_SIGN,
                                     cert_path=DEFAULT_CERTIFICATE_FILE):
    return SslVerificationMetadata(ssl_verification_mode, cert_path)


class ApiTest(unittest.TestCase):
    class MockClientResponse():
        def __init__(self, text='myretval', content='mycontent'):
            setattr(self, 'content', content.encode('utf-8'))
            setattr(self, 'text', text)

    POLICY_FILE = './test/test_config/policies/variables.yml'

    def verify_http_call(self, http_client, method, endpoint, *args,
                         ssl_verification_metadata=None, api_token='apitoken', auth=None, query=None,
                         account='default', headers={}, **kwargs):

        params = {
            'url': 'http://localhost',
            'account': account,
        }

        for name, value in kwargs.items():
            params[name] = value

        extra_args = {}
        for extra_arg_name in ['api_token', 'auth', 'query', 'headers']:
            if locals()[extra_arg_name]:
                extra_args[extra_arg_name] = locals()[extra_arg_name]

        http_client.assert_called_once_with(method, endpoint, params, *args,
                                            **extra_args,
                                            ssl_verification_metadata=ssl_verification_metadata)

    def test_new_client_throws_error_when_no_url(self):
        with self.assertRaises(Exception):
            Api(login_id='mylogin', api_key='apikey', ssl_verify=False)

    # Hostfactory - create token

    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse())
    def test_host_factory_create_token_invokes_http_client_correctly(self, mock_http_client):
        api = create_api()

        def mock_auth():
            return 'apitoken'

        api.authenticate = mock_auth

        api.create_token(MOCK_HOSTFACTORY_OBJECT)
        MOCK_EXPECTED_HOSTFACTORY_PARAM = parse.urlencode(MOCK_HOSTFACTORY_OBJECT.to_dict(),
                                                          doseq=True)

        self.verify_http_call(mock_http_client, HttpVerb.POST, ConjurEndpoint.HOST_FACTORY_TOKENS,
                              MOCK_EXPECTED_HOSTFACTORY_PARAM,
                              query={},
                              api_token='apitoken',
                              headers={'Content-Type': 'application/x-www-form-urlencoded'},
                              ssl_verification_metadata=create_ssl_verification_metadata())

    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse())
    def test_host_factory_create_token_with_no_cidr_invokes_http_client_correctly(self,
                                                                                  mock_http_client):
        api = create_api()

        def mock_auth():
            return 'apitoken'

        api.authenticate = mock_auth

        api.create_token(MOCK_HOSTFACTORY_WITHOUT_CIDR_OBJECT)
        MOCK_EXPECTED_HOSTFACTORY_PARAM = parse.urlencode(
            MOCK_HOSTFACTORY_WITHOUT_CIDR_OBJECT.to_dict(),
            doseq=True)

        self.verify_http_call(mock_http_client, HttpVerb.POST, ConjurEndpoint.HOST_FACTORY_TOKENS,
                              MOCK_EXPECTED_HOSTFACTORY_PARAM,
                              query={},
                              api_token='apitoken',
                              headers={'Content-Type': 'application/x-www-form-urlencoded'},
                              ssl_verification_metadata=create_ssl_verification_metadata())

    @patch('conjur.logic.credential_provider.FileCredentialsProvider.load',
           return_value=MockCredentials)
    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse())
    def test_new_client_delegates_ssl_verify_flag(self, mock_http_client, mock_creds):
        create_api().login()
        self.verify_http_call(mock_http_client, HttpVerb.GET, ConjurEndpoint.USERNAME,
                              auth=('myuser', 'mypass'),
                              api_token=False,
                              ssl_verification_metadata=create_ssl_verification_metadata())

    @patch('conjur.logic.credential_provider.FileCredentialsProvider.load',
           return_value=MockCredentials)
    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse())
    def test_new_client_overrides_ssl_verify_flag_with_ca_bundle_if_provided(self,
                                                                             mock_http_client,
                                                                             mock_cres):
        create_api().login()
        self.verify_http_call(mock_http_client, HttpVerb.GET, ConjurEndpoint.USERNAME,
                              auth=('myuser', 'mypass'),
                              api_token=False,
                              ssl_verification_metadata=create_ssl_verification_metadata())

    @patch('conjur.logic.credential_provider.FileCredentialsProvider.load',
           return_value=MockCredentials)
    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse())
    def test_login_invokes_http_client_correctly(self, mock_http_client, mock_creds):
        create_api().login()
        self.verify_http_call(mock_http_client, HttpVerb.GET, ConjurEndpoint.USERNAME,
                              auth=('myuser', 'mypass'),
                              api_token=False,
                              ssl_verification_metadata=create_ssl_verification_metadata())

    @patch('conjur.logic.credential_provider.FileCredentialsProvider.load',
           return_value=CredentialsData("machine", login=""))
    def test_login_throws_error_when_password_not_provided(self, mock_creds):
        with self.assertRaises(MissingRequiredParameterException):
            create_api().login()

    @patch('conjur.logic.credential_provider.FileCredentialsProvider.load',
           return_value=MockCredentials)
    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse())
    def test_login_saves_login_id(self, mock1, mock2):
        api = create_api()

        api.login()

        self.assertEquals(api.login_id, 'myuser')

    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse())
    def test_if_api_token_is_missing_fetch_a_new_one(self, mock_http_client):
        api = create_api()
        api.authenticate = MagicMock(return_value='mytoken')

        self.assertEquals(api.api_token, 'mytoken')
        api.authenticate.assert_called_once_with()

    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse())
    def test_if_api_token_is_not_expired_dont_fetch_new_one(self, mock_http_client):
        api = create_api()
        api.authenticate = MagicMock(return_value='mytoken')

        token = api.api_token
        api.authenticate = MagicMock(return_value='newtoken')

        self.assertEquals(api.api_token, 'mytoken')

    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse())
    def test_if_api_token_is_expired_fetch_new_one(self, mock_http_client):
        api = create_api()
        api.authenticate = MagicMock(return_value='mytoken')

        api.api_token
        api.api_token_expiration = datetime.now()

        api.authenticate = MagicMock(return_value='newtoken')

        self.assertEquals(api.api_token, 'newtoken')

    # Get variable

    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse())
    def test_get_variable_invokes_http_client_correctly(self, mock_http_client):
        api = create_api()

        def mock_auth():
            return 'apitoken'

        api.authenticate = mock_auth

        api.get_variable('myvar')

        self.verify_http_call(mock_http_client, HttpVerb.GET, ConjurEndpoint.SECRETS,
                              kind='variable',
                              identifier='myvar',
                              query={},
                              ssl_verification_metadata=create_ssl_verification_metadata())

    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse())
    def test_get_variable_with_version_invokes_http_client_correctly(self, mock_http_client):
        api = create_api()

        def mock_auth():
            return 'apitoken'

        api.authenticate = mock_auth

        api.get_variable('myvar', '1')

        self.verify_http_call(mock_http_client, HttpVerb.GET, ConjurEndpoint.SECRETS,
                              kind='variable',
                              identifier='myvar',
                              query={'version': '1'},
                              ssl_verification_metadata=create_ssl_verification_metadata())

    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse())
    def test_get_variable_passes_down_ssl_verify_param(self, mock_http_client):
        api = create_api(ssl_verification_mode=SslVerificationMode.CA_BUNDLE,
                         cert_path='verify')
        ssl_verification_metadata = create_ssl_verification_metadata(
            ssl_verification_mode=SslVerificationMode.CA_BUNDLE,
            cert_path='verify')

        # ssl_verify='verify')

        def mock_auth():
            return 'apitoken'

        api.authenticate = mock_auth

        api.get_variable('myvar')

        self.verify_http_call(mock_http_client, HttpVerb.GET, ConjurEndpoint.SECRETS,
                              kind='variable',
                              identifier='myvar',
                              query={},
                              ssl_verification_metadata=ssl_verification_metadata)

    # Set variable

    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse())
    def test_set_variable_invokes_http_client_correctly(self, mock_http_client):
        api = create_api()

        def mock_auth():
            return 'apitoken'

        api.authenticate = mock_auth

        api.set_variable('myvar', 'myvalue')

        self.verify_http_call(mock_http_client, HttpVerb.POST, ConjurEndpoint.SECRETS,
                              'myvalue',
                              kind='variable',
                              identifier='myvar',
                              ssl_verification_metadata=create_ssl_verification_metadata())

    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse())
    def test_set_variable_passes_down_ssl_verify_param(self, mock_http_client):
        cert_path = 'verify'
        ssl_verification_metadata = create_ssl_verification_metadata(cert_path=cert_path)
        api = create_api(cert_path=cert_path)

        def mock_auth():
            return 'apitoken'

        api.authenticate = mock_auth

        api.set_variable('myvar', 'myvalue')
        self.verify_http_call(mock_http_client, HttpVerb.POST, ConjurEndpoint.SECRETS,
                              'myvalue',
                              kind='variable',
                              identifier='myvar',
                              ssl_verification_metadata=ssl_verification_metadata)

    # Policy load

    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse(text='{}'))
    def test_load_policy_invokes_http_client_correctly(self, mock_http_client):
        api = create_api()

        def mock_auth():
            return 'apitoken'

        api.authenticate = mock_auth

        api.load_policy_file('mypolicyname', self.POLICY_FILE)

        policy_data = None
        with open(self.POLICY_FILE, 'r') as content_file:
            policy_data = content_file.read()

        self.verify_http_call(mock_http_client, HttpVerb.POST, ConjurEndpoint.POLICIES,
                              policy_data,
                              identifier='mypolicyname',
                              ssl_verification_metadata=create_ssl_verification_metadata())

    @patch('conjur.api.api.invoke_endpoint',
           return_value=MockClientResponse(text=json.dumps(MOCK_POLICY_CHANGE_OBJECT)))
    def test_load_policy_converts_returned_data_to_expected_objects(self, mock_http_client):
        api = create_api()

        def mock_auth():
            return 'apitoken'

        api.authenticate = mock_auth

        output = api.load_policy_file('mypolicyname', self.POLICY_FILE)
        self.assertEqual(output, MOCK_POLICY_CHANGE_OBJECT)

    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse(text='{}'))
    def test_load_policy_passes_down_ssl_verify_parameter(self, mock_http_client):
        api = create_api(ssl_verification_mode=SslVerificationMode.CA_BUNDLE,
                         cert_path="ssl_verify")

        # ssl_verify='ssl_verify')

        def mock_auth():
            return 'apitoken'

        api.authenticate = mock_auth

        api.load_policy_file('mypolicyname', self.POLICY_FILE)

        policy_data = None
        ssl_verification_metadata = create_ssl_verification_metadata(cert_path="ssl_verify",
                                                                     ssl_verification_mode=SslVerificationMode.CA_BUNDLE)
        with open(self.POLICY_FILE, 'r') as content_file:
            policy_data = content_file.read()

        self.verify_http_call(mock_http_client, HttpVerb.POST, ConjurEndpoint.POLICIES,
                              policy_data,
                              identifier='mypolicyname',
                              ssl_verification_metadata=ssl_verification_metadata)

    # Policy replace

    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse(text='{}'))
    def test_replace_policy_invokes_http_client_correctly(self, mock_http_client):
        api = create_api()

        def mock_auth():
            return 'apitoken'

        api.authenticate = mock_auth

        api.replace_policy_file('mypolicyname', self.POLICY_FILE)

        policy_data = None
        with open(self.POLICY_FILE, 'r') as content_file:
            policy_data = content_file.read()

        self.verify_http_call(mock_http_client, HttpVerb.PUT, ConjurEndpoint.POLICIES,
                              policy_data,
                              identifier='mypolicyname',
                              ssl_verification_metadata=create_ssl_verification_metadata())

    @patch('conjur.api.api.invoke_endpoint',
           return_value=MockClientResponse(text=json.dumps(MOCK_POLICY_CHANGE_OBJECT)))
    def test_replace_policy_converts_returned_data_to_expected_objects(self, mock_http_client):
        api = create_api()

        def mock_auth():
            return 'apitoken'

        api.authenticate = mock_auth

        output = api.replace_policy_file('mypolicyname', self.POLICY_FILE)
        self.assertEqual(output, MOCK_POLICY_CHANGE_OBJECT)

    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse(text='{}'))
    def test_replace_policy_passes_down_ssl_verify_parameter(self, mock_http_client):
        api = create_api(cert_path='ssl_verify')

        def mock_auth():
            return 'apitoken'

        api.authenticate = mock_auth

        api.replace_policy_file('mypolicyname', self.POLICY_FILE)

        policy_data = None
        with open(self.POLICY_FILE, 'r') as content_file:
            policy_data = content_file.read()

        self.verify_http_call(mock_http_client, HttpVerb.PUT, ConjurEndpoint.POLICIES,
                              policy_data,
                              identifier='mypolicyname',
                              ssl_verification_metadata=create_ssl_verification_metadata(cert_path='ssl_verify'))

    # Policy update

    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse(text='{}'))
    def test_update_policy_invokes_http_client_correctly(self, mock_http_client):
        api = create_api()

        def mock_auth():
            return 'apitoken'

        api.authenticate = mock_auth

        api.update_policy_file('mypolicyname', self.POLICY_FILE)

        policy_data = None
        with open(self.POLICY_FILE, 'r') as content_file:
            policy_data = content_file.read()

        self.verify_http_call(mock_http_client, HttpVerb.PATCH, ConjurEndpoint.POLICIES,
                              policy_data,
                              identifier='mypolicyname',
                              ssl_verification_metadata=create_ssl_verification_metadata())

    @patch('conjur.api.api.invoke_endpoint',
           return_value=MockClientResponse(text=json.dumps(MOCK_POLICY_CHANGE_OBJECT)))
    def test_update_policy_converts_returned_data_to_expected_objects(self, mock_http_client):
        api = create_api()

        def mock_auth():
            return 'apitoken'

        api.authenticate = mock_auth

        output = api.update_policy_file('mypolicyname', self.POLICY_FILE)
        self.assertEqual(output, MOCK_POLICY_CHANGE_OBJECT)

    # Get variables

    @patch('conjur.api.api.invoke_endpoint',
           return_value=MockClientResponse(content='{"foo": "a", "bar": "b"}'))
    def test_get_variables_invokes_http_client_correctly(self, mock_http_client):
        api = create_api()

        def mock_auth():
            return 'apitoken'

        api.authenticate = mock_auth

        api.get_variables('myvar', 'myvar2')

        self.verify_http_call(mock_http_client, HttpVerb.GET, ConjurEndpoint.BATCH_SECRETS,
                              query={
                                  'variable_ids': 'default:variable:myvar,default:variable:myvar2'
                              },
                              ssl_verification_metadata=create_ssl_verification_metadata())

    @patch('conjur.api.api.invoke_endpoint',
           return_value=MockClientResponse(content=MOCK_BATCH_GET_RESPONSE))
    def test_get_variables_converts_returned_data_to_expected_objects(self, mock_http_client):
        api = create_api(account='myaccount')

        def mock_auth():
            return 'apitoken'

        api.authenticate = mock_auth

        output = api.get_variables('myvar', 'myvar2')
        self.assertEqual(output,
                         {
                             'foo': 'a',
                             'bar': 'b',
                         })

    @patch('conjur.api.api.invoke_endpoint',
           return_value=MockClientResponse(content='{"foo": "a", "bar": "b"}'))
    def test_get_variables_passes_down_ssl_verify_parameter(self, mock_http_client):
        api = create_api(ssl_verification_mode=SslVerificationMode.CA_BUNDLE,
                         cert_path='sslverify')
        ssl_verification_metadata = create_ssl_verification_metadata(
            ssl_verification_mode=SslVerificationMode.CA_BUNDLE,
            cert_path='sslverify')

        def mock_auth():
            return 'apitoken'

        api.authenticate = mock_auth

        api.get_variables('myvar', 'myvar2')

        self.verify_http_call(mock_http_client, HttpVerb.GET, ConjurEndpoint.BATCH_SECRETS,
                              query={
                                  'variable_ids': 'default:variable:myvar,default:variable:myvar2'
                              },
                              ssl_verification_metadata=ssl_verification_metadata)

    # List resources

    @patch('conjur.api.api.invoke_endpoint', \
           return_value=MockClientResponse(text=json.dumps(MOCK_RESOURCE_LIST)))
    def test_get_resources_invokes_http_client_correctly(self, mock_http_client):
        api = create_api()

        def mock_auth():
            return 'apitoken'

        api.authenticate = mock_auth

        api.resources_list()

        self.verify_http_call(mock_http_client, HttpVerb.GET, ConjurEndpoint.RESOURCES,
                              query={},
                              ssl_verification_metadata=create_ssl_verification_metadata())

    @patch('conjur.api.api.invoke_endpoint', \
           return_value=MockClientResponse(text=json.dumps(MOCK_RESOURCE_LIST)))
    def test_get_resources_with_constraints_invokes_http_client_correctly(self, mock_http_client):
        api = create_api()

        def mock_auth():
            return 'apitoken'

        api.authenticate = mock_auth

        api.resources_list({'limit': 1})

        self.verify_http_call(mock_http_client, HttpVerb.GET, ConjurEndpoint.RESOURCES,
                              query={'limit': 1},
                              ssl_verification_metadata=create_ssl_verification_metadata())

    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse(content=json.dumps({})))
    def test_whoami_invokes_http_client_correctly(self, mock_http_client):
        api = create_api()

        def mock_auth():
            return 'apitoken'

        api.authenticate = mock_auth

        api.whoami()

        self.verify_http_call(mock_http_client, HttpVerb.GET, ConjurEndpoint.WHOAMI,
                              ssl_verification_metadata=create_ssl_verification_metadata())

    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse(content=json.dumps({})))
    def test_rotate_personal_api_key_invokes_http_client_correctly(self, mock_http_client):
        api = create_api()

        def mock_auth():
            return 'apitoken'

        api.authenticate = mock_auth

        api.rotate_personal_api_key("mylogin", "somepass")

        self.verify_http_call(mock_http_client, HttpVerb.PUT, ConjurEndpoint.ROTATE_API_KEY,
                              api_token='',
                              auth=('mylogin', 'somepass'),
                              ssl_verification_metadata=create_ssl_verification_metadata())

    @patch('conjur.api.api.invoke_endpoint', \
           return_value=MockClientResponse(content=json.dumps({})))
    def test_rotate_other_api_key_invokes_http_client_correctly(self, mock_http_client):
        api = create_api()

        def mock_auth():
            return 'apitoken'

        api.authenticate = mock_auth

        api.rotate_other_api_key(Resource(kind='user', identifier="somename"))

        self.verify_http_call(mock_http_client, HttpVerb.PUT, ConjurEndpoint.ROTATE_API_KEY,
                              query={'role': 'user:somename'},
                              ssl_verification_metadata=create_ssl_verification_metadata())

    @patch('conjur.api.api.invoke_endpoint', \
           return_value=MockClientResponse(content=json.dumps({})))
    def test_rotate_other_api_key_can_raise_exception_when_resource_is_invalid(self,
                                                                               mock_http_client):
        api = create_api()

        def mock_auth():
            return 'apitoken'

        api.authenticate = mock_auth
        with self.assertRaises(Exception):
            api.rotate_other_api_key(Resource(kind='someinvalidresource', identifier="somename"))

    @patch('conjur.api.api.invoke_endpoint', \
           return_value=MockClientResponse(content=json.dumps({})))
    def test_change_password_invokes_http_client_correctly(self, mock_http_client):
        api = create_api()

        def mock_auth():
            return 'apitoken'

        api.authenticate = mock_auth

        api.change_personal_password("someloggedinuser", "somecurrentpass", "somenewpass")

        self.verify_http_call(mock_http_client, HttpVerb.PUT, ConjurEndpoint.CHANGE_PASSWORD,
                              "somenewpass",
                              api_token='',
                              auth=('someloggedinuser', 'somecurrentpass'),
                              ssl_verification_metadata=create_ssl_verification_metadata())
