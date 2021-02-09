import json
import unittest
from datetime import datetime
from unittest.mock import patch, MagicMock

from conjur.wrapper.http_wrapper import HttpVerb
from conjur.api.endpoints import ConjurEndpoint

from conjur.api import Api
from conjur.resource import Resource

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

class ApiTest(unittest.TestCase):
    class MockClientResponse():
        def __init__(self, text='myretval', content='mycontent'):
            setattr(self, 'content', content.encode('utf-8'))
            setattr(self, 'text', text)

    POLICY_FILE = './test/test_config/policies/variables.yml'

    def verify_http_call(self, http_client, method, endpoint, *args,
            ssl_verify=None, api_token='apitoken', auth=None, query=None,
            account='default', **kwargs):

        params = {
            'url': 'http://localhost',
            'account': account,
        }

        for name, value in kwargs.items():
            params[name] = value

        extra_args = {}
        for extra_arg_name in ['api_token', 'auth', 'query']:
            if locals()[extra_arg_name]:
                extra_args[extra_arg_name] = locals()[extra_arg_name]

        http_client.assert_called_once_with(method, endpoint, params, *args,
                                            **extra_args,
                                            ssl_verify=ssl_verify)

    def test_new_client_throws_error_when_no_url(self):
        with self.assertRaises(Exception):
            Api(login_id='mylogin', api_key='apikey', ssl_verify=False)

    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse())
    def test_new_client_delegates_ssl_verify_flag(self, mock_http_client):
        Api(url='http://localhost', ssl_verify=True).login('myuser', 'mypass')
        self.verify_http_call(mock_http_client, HttpVerb.GET, ConjurEndpoint.LOGIN,
                              auth=('myuser', 'mypass'),
                              api_token=False,
                              ssl_verify=True)

    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse())
    def test_new_client_overrides_ssl_verify_flag_with_ca_bundle_if_provided(self, mock_http_client):
        Api(url='http://localhost', ssl_verify=True,
                  ca_bundle='cabundle').login('myuser', 'mypass')
        self.verify_http_call(mock_http_client, HttpVerb.GET, ConjurEndpoint.LOGIN,
                              auth=('myuser', 'mypass'),
                              api_token=False,
                              ssl_verify='cabundle')


    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse())
    def test_login_invokes_http_client_correctly(self, mock_http_client):
        Api(url='http://localhost').login('myuser', 'mypass')
        self.verify_http_call(mock_http_client, HttpVerb.GET, ConjurEndpoint.LOGIN,
                              auth=('myuser', 'mypass'),
                              api_token=False,
                              ssl_verify=True)

    def test_login_throws_error_when_username_not_provided(self):
        with self.assertRaises(RuntimeError):
            Api(url='http://localhost').login(None, 'mypass')

    def test_login_throws_error_when_password_not_provided(self):
        with self.assertRaises(RuntimeError):
            Api(url='http://localhost').login('myuser', None)

    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse())
    def test_login_saves_login_id(self, _):
        api = Api(url='http://localhost')

        api.login('myuser', 'mypass')

        self.assertEquals(api.login_id, 'myuser')

    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse())
    def test_if_api_token_is_missing_fetch_a_new_one(self, mock_http_client):
        api = Api(url='http://localhost')
        api.authenticate = MagicMock(return_value='mytoken')

        self.assertEquals(api.api_token, 'mytoken')
        api.authenticate.assert_called_once_with()

    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse())
    def test_if_account_is_empty_throw_an_error(self, mock_http_client):
        empty_values = [ None, "" ]
        for empty_value in empty_values:
            with self.subTest(account=empty_value):
                with self.assertRaises(RuntimeError):
                    api = Api(url='http://localhost', account=empty_value)

    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse())
    def test_if_api_token_is_not_expired_dont_fetch_new_one(self, mock_http_client):
        api = Api(url='http://localhost')
        api.authenticate = MagicMock(return_value='mytoken')

        token = api.api_token
        api.authenticate = MagicMock(return_value='newtoken')

        self.assertEquals(api.api_token, 'mytoken')

    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse())
    def test_if_api_token_is_expired_fetch_new_one(self, mock_http_client):
        api = Api(url='http://localhost')
        api.authenticate = MagicMock(return_value='mytoken')

        api.api_token
        api.api_token_expiration = datetime.now()

        api.authenticate = MagicMock(return_value='newtoken')

        self.assertEquals(api.api_token, 'newtoken')

    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse())
    def test_authenticate_invokes_http_client_correctly(self, mock_http_client):
        Api(url='http://localhost', login_id='mylogin', api_key='apikey').authenticate()

        self.verify_http_call(mock_http_client, HttpVerb.POST, ConjurEndpoint.AUTHENTICATE,
                              'apikey',
                              login='mylogin',
                              api_token=False,
                              ssl_verify=True)

    def test_authenticate_throws_error_without_login_id_specified(self):
        with self.assertRaises(RuntimeError):
            Api(url='http://localhost', api_key='apikey').authenticate()

    def test_authenticate_throws_error_without_api_key_specified(self):
        with self.assertRaises(RuntimeError):
            Api(url='http://localhost', login_id='mylogin').authenticate()

    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse())
    def test_account_info_is_passed_down_to_http_call(self, mock_http_client):
        Api(url='http://localhost',
                  account='myacct',
                  login_id='mylogin',
                  api_key='apikey').authenticate()

        self.verify_http_call(mock_http_client, HttpVerb.POST, ConjurEndpoint.AUTHENTICATE,
                              'apikey',
                              login='mylogin',
                              account='myacct',
                              api_token=False,
                              ssl_verify=True)

    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse())
    def test_authenticate_passes_down_ssl_verify_param(self, mock_http_client):
        Api(url='http://localhost', login_id='mylogin', api_key='apikey',
                  ssl_verify='verify').authenticate()

        self.verify_http_call(mock_http_client, HttpVerb.POST, ConjurEndpoint.AUTHENTICATE,
                              'apikey',
                              api_token=False,
                              login='mylogin',
                              ssl_verify='verify')

    # Get variable

    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse())
    def test_get_variable_invokes_http_client_correctly(self, mock_http_client):
        api = Api(url='http://localhost', login_id='mylogin', api_key='apikey')
        def mock_auth():
            return 'apitoken'
        api.authenticate = mock_auth

        api.get_variable('myvar')

        self.verify_http_call(mock_http_client, HttpVerb.GET, ConjurEndpoint.SECRETS,
                              kind='variable',
                              identifier='myvar',
                              query={},
                              ssl_verify=True)

    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse())
    def test_get_variable_with_version_invokes_http_client_correctly(self, mock_http_client):
        api = Api(url='http://localhost', login_id='mylogin', api_key='apikey')
        def mock_auth():
            return 'apitoken'
        api.authenticate = mock_auth

        api.get_variable('myvar', '1')

        self.verify_http_call(mock_http_client, HttpVerb.GET, ConjurEndpoint.SECRETS,
                              kind='variable',
                              identifier='myvar',
                              query={'version': '1'},
                              ssl_verify=True)

    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse())
    def test_get_variable_passes_down_ssl_verify_param(self, mock_http_client):
        api = Api(url='http://localhost', login_id='mylogin', api_key='apikey',
                        ssl_verify='verify')
        def mock_auth():
            return 'apitoken'
        api.authenticate = mock_auth

        api.get_variable('myvar')

        self.verify_http_call(mock_http_client, HttpVerb.GET, ConjurEndpoint.SECRETS,
                              kind='variable',
                              identifier='myvar',
                              query={},
                              ssl_verify='verify')

    # Set variable

    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse())
    def test_set_variable_invokes_http_client_correctly(self, mock_http_client):
        api = Api(url='http://localhost', login_id='mylogin', api_key='apikey')
        def mock_auth():
            return 'apitoken'
        api.authenticate = mock_auth

        api.set_variable('myvar', 'myvalue')

        self.verify_http_call(mock_http_client, HttpVerb.POST, ConjurEndpoint.SECRETS,
                              'myvalue',
                              kind='variable',
                              identifier='myvar',
                              ssl_verify=True)

    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse())
    def test_set_variable_passes_down_ssl_verify_param(self, mock_http_client):
        api = Api(url='http://localhost', login_id='mylogin', api_key='apikey',
                        ssl_verify='verify')
        def mock_auth():
            return 'apitoken'
        api.authenticate = mock_auth

        api.set_variable('myvar', 'myvalue')

        self.verify_http_call(mock_http_client, HttpVerb.POST, ConjurEndpoint.SECRETS,
                              'myvalue',
                              kind='variable',
                              identifier='myvar',
                              ssl_verify='verify')

    # Policy load

    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse(text='{}'))
    def test_load_policy_invokes_http_client_correctly(self, mock_http_client):
        api = Api(url='http://localhost', login_id='mylogin', api_key='apikey')
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
                              ssl_verify=True)

    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse(text=json.dumps(MOCK_POLICY_CHANGE_OBJECT)))
    def test_load_policy_converts_returned_data_to_expected_objects(self, mock_http_client):
        api = Api(url='http://localhost', login_id='mylogin', api_key='apikey')
        def mock_auth():
            return 'apitoken'
        api.authenticate = mock_auth

        output = api.load_policy_file('mypolicyname', self.POLICY_FILE)
        self.assertEqual(output, MOCK_POLICY_CHANGE_OBJECT)

    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse(text='{}'))
    def test_load_policy_passes_down_ssl_verify_parameter(self, mock_http_client):
        api = Api(url='http://localhost', login_id='mylogin', api_key='apikey', ssl_verify='ssl_verify')
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
                              ssl_verify='ssl_verify')

    # Policy replace

    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse(text='{}'))
    def test_replace_policy_invokes_http_client_correctly(self, mock_http_client):
        api = Api(url='http://localhost', login_id='mylogin', api_key='apikey')
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
                              ssl_verify=True)

    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse(text=json.dumps(MOCK_POLICY_CHANGE_OBJECT)))
    def test_replace_policy_converts_returned_data_to_expected_objects(self, mock_http_client):
        api = Api(url='http://localhost', login_id='mylogin', api_key='apikey')
        def mock_auth():
            return 'apitoken'
        api.authenticate = mock_auth

        output = api.replace_policy_file('mypolicyname', self.POLICY_FILE)
        self.assertEqual(output, MOCK_POLICY_CHANGE_OBJECT)

    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse(text='{}'))
    def test_replace_policy_passes_down_ssl_verify_parameter(self, mock_http_client):
        api = Api(url='http://localhost', login_id='mylogin', api_key='apikey', ssl_verify='ssl_verify')
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
                              ssl_verify='ssl_verify')

    # Policy update

    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse(text='{}'))
    def test_update_policy_invokes_http_client_correctly(self, mock_http_client):
        api = Api(url='http://localhost', login_id='mylogin', api_key='apikey')
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
                              ssl_verify=True)

    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse(text=json.dumps(MOCK_POLICY_CHANGE_OBJECT)))
    def test_update_policy_converts_returned_data_to_expected_objects(self, mock_http_client):
        api = Api(url='http://localhost', login_id='mylogin', api_key='apikey')
        def mock_auth():
            return 'apitoken'
        api.authenticate = mock_auth

        output = api.update_policy_file('mypolicyname', self.POLICY_FILE)
        self.assertEqual(output, MOCK_POLICY_CHANGE_OBJECT)

    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse(text='{}'))
    def test_update_policy_passes_down_ssl_verify_parameter(self, mock_http_client):
        api = Api(url='http://localhost', login_id='mylogin', api_key='apikey', ssl_verify='ssl_verify')
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
                              ssl_verify='ssl_verify')

    # Get variables

    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse(content='{"foo": "a", "bar": "b"}'))
    def test_get_variables_invokes_http_client_correctly(self, mock_http_client):
        api = Api(url='http://localhost', login_id='mylogin', api_key='apikey')
        def mock_auth():
            return 'apitoken'
        api.authenticate = mock_auth

        api.get_variables('myvar', 'myvar2')

        self.verify_http_call(mock_http_client, HttpVerb.GET, ConjurEndpoint.BATCH_SECRETS,
                              query={
                                  'variable_ids': 'default:variable:myvar,default:variable:myvar2'
                              },
                              ssl_verify=True)

    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse(content=MOCK_BATCH_GET_RESPONSE))
    def test_get_variables_converts_returned_data_to_expected_objects(self, mock_http_client):
        api = Api(url='http://localhost', login_id='mylogin', api_key='apikey', account='myaccount')
        def mock_auth():
            return 'apitoken'
        api.authenticate = mock_auth

        output = api.get_variables('myvar', 'myvar2')
        self.assertEqual(output,
                         {
                             'foo': 'a',
                             'bar': 'b',
                         })

    @patch('conjur.api.api.invoke_endpoint', return_value=MockClientResponse(content='{"foo": "a", "bar": "b"}'))
    def test_get_variables_passes_down_ssl_verify_parameter(self, mock_http_client):
        api = Api(url='http://localhost', login_id='mylogin', api_key='apikey', ssl_verify='sslverify')
        def mock_auth():
            return 'apitoken'
        api.authenticate = mock_auth

        api.get_variables('myvar', 'myvar2')

        self.verify_http_call(mock_http_client, HttpVerb.GET, ConjurEndpoint.BATCH_SECRETS,
                              query={
                                  'variable_ids': 'default:variable:myvar,default:variable:myvar2'
                              },
                              ssl_verify='sslverify')

    # List resources

    @patch('conjur.api.api.invoke_endpoint', \
           return_value=MockClientResponse(content=json.dumps(MOCK_RESOURCE_LIST)))
    def test_get_resources_invokes_http_client_correctly(self, mock_http_client):
        api = Api(url='http://localhost', login_id='mylogin', api_key='apikey')
        def mock_auth():
            return 'apitoken'
        api.authenticate = mock_auth

        api.resources_list()

        self.verify_http_call(mock_http_client, HttpVerb.GET, ConjurEndpoint.RESOURCES,
                              query={},
                              ssl_verify=True)

    @patch('conjur.api.api.invoke_endpoint', \
           return_value=MockClientResponse(content=json.dumps(MOCK_RESOURCE_LIST)))
    def test_get_resources_with_constraints_invokes_http_client_correctly(self, mock_http_client):
        api = Api(url='http://localhost', login_id='mylogin', api_key='apikey')
        def mock_auth():
            return 'apitoken'
        api.authenticate = mock_auth

        api.resources_list({'limit':1})

        self.verify_http_call(mock_http_client, HttpVerb.GET, ConjurEndpoint.RESOURCES,
                              query={'limit': 1},
                              ssl_verify=True)

    @patch('conjur.api.api.invoke_endpoint', \
           return_value=MockClientResponse(content=json.dumps({})))
    def test_whoami_invokes_http_client_correctly(self, mock_http_client):
        api = Api(url='http://localhost', login_id='mylogin', api_key='apikey')
        def mock_auth():
            return 'apitoken'
        api.authenticate = mock_auth

        api.whoami()

        self.verify_http_call(mock_http_client, HttpVerb.GET, ConjurEndpoint.WHOAMI,
                              ssl_verify=True)

    @patch('conjur.api.api.invoke_endpoint', \
           return_value=MockClientResponse(content=json.dumps({})))
    def test_rotate_personal_api_key_invokes_http_client_correctly(self, mock_http_client):
        api = Api(url='http://localhost', login_id='mylogin', api_key='apikey')
        def mock_auth():
            return 'apitoken'
        api.authenticate = mock_auth

        api.rotate_personal_api_key("mylogin", "somepass")

        self.verify_http_call(mock_http_client, HttpVerb.PUT, ConjurEndpoint.ROTATE_API_KEY,
                              auth=('mylogin', 'somepass'),
                              ssl_verify=True)

    @patch('conjur.api.api.invoke_endpoint', \
           return_value=MockClientResponse(content=json.dumps({})))
    def test_rotate_other_api_key_invokes_http_client_correctly(self, mock_http_client):
        api = Api(url='http://localhost', login_id='mylogin', api_key='apikey')
        def mock_auth():
            return 'apitoken'
        api.authenticate = mock_auth

        api.rotate_other_api_key(Resource(type_='user', name="somename"))

        self.verify_http_call(mock_http_client, HttpVerb.PUT, ConjurEndpoint.ROTATE_API_KEY,
                              query={'role': 'user:somename'},
                              ssl_verify=True)

    @patch('conjur.api.api.invoke_endpoint', \
           return_value=MockClientResponse(content=json.dumps({})))
    def test_rotate_other_api_key_can_raise_exception_when_resource_is_invalid(self, mock_http_client):
        api = Api(url='http://localhost', login_id='mylogin', api_key='apikey')
        def mock_auth():
            return 'apitoken'
        api.authenticate = mock_auth
        with self.assertRaises(Exception):
            api.rotate_other_api_key(Resource(type_='someinvalidresource', name="somename"))

    @patch('conjur.api.api.invoke_endpoint', \
           return_value=MockClientResponse(content=json.dumps({})))
    def test_change_password_invokes_http_client_correctly(self, mock_http_client):
        api = Api(url='http://localhost', login_id='mylogin', api_key='apikey')
        def mock_auth():
            return 'apitoken'
        api.authenticate = mock_auth

        api.change_personal_password("someloggedinuser", "somecurrentpass", "somenewpass")

        self.verify_http_call(mock_http_client, HttpVerb.PUT, ConjurEndpoint.CHANGE_PASSWORD,
                              "somenewpass",
                              auth=('someloggedinuser', 'somecurrentpass'),
                              ssl_verify=True)
