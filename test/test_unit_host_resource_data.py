import unittest

from conjur.host import HostResourceData

class HostResourceDataTest(unittest.TestCase):

    def test_host_data_constructor(self):
        mock_action = None
        mock_host_to_update = None

        host_resource_data = HostResourceData(action=mock_action, host_to_update=mock_host_to_update)

        assert host_resource_data.action == mock_action
        assert host_resource_data.host_to_update == mock_host_to_update

    ''''
    Verifies that proper dictionary is printed when action is rotate-api-key
    '''
    def test_host_input_data_rotate_api_key_is_printed_as_dict_properly(self):
        EXPECTED_REP_OBJECT={'action': 'rotate-api-key', 'host': 'somehost'}
        mock_host_resource_data = HostResourceData(action='rotate-api-key', host_to_update='somehost')

        rep_obj = mock_host_resource_data.__repr__()
        self.assertEquals(str(EXPECTED_REP_OBJECT), rep_obj)

    ''''
    Verifies that proper dictionary is printed when action is rotate-api-key but host is empty
    '''
    def test_host_input_data_rotate_api_key_is_printed_as_dict_properly_when_host_is_empty(self):
        EXPECTED_REP_OBJECT={'action': 'rotate-api-key'}
        mock_host_resource_data = HostResourceData(action='rotate-api-key', host_to_update=None)

        rep_obj = mock_host_resource_data.__repr__()
        self.assertEquals(str(EXPECTED_REP_OBJECT), rep_obj)

    ''''
    Verifies that proper dictionary is printed when action is empty but host has a value
    '''
    def test_host_input_data_rotate_api_key_is_printed_as_dict_properly_when_action_is_empty(self):
        EXPECTED_REP_OBJECT={'host': 'somehost'}
        mock_host_resource_data = HostResourceData(action=None, host_to_update='somehost')

        rep_obj = mock_host_resource_data.__repr__()
        self.assertEquals(str(EXPECTED_REP_OBJECT), rep_obj)
