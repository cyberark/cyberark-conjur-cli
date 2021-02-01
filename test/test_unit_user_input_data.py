import unittest

from conjur.user import UserInputData


class UserInputDataTest(unittest.TestCase):

    def test_user_input_data_constructor(self):
        mock_action = None
        mock_user_id = None
        mock_new_password = None
        user_input_data = UserInputData(action=mock_action, id=mock_user_id, new_password=mock_new_password)

        assert user_input_data.action == mock_action
        assert user_input_data.user_id == mock_user_id
        assert user_input_data.new_password == mock_new_password

    ''''
    Verifies that proper dictionary is printed when action is rotate-api-key
    '''
    def test_user_input_data_rotate_api_key_is_printed_as_dict_properly(self):
        EXPECTED_REP_OBJECT={'action': 'rotate-api-key', 'id': 'someuser'}
        mock_user_input_data = UserInputData(action='rotate-api-key', id='someuser', new_password=None)

        rep_obj = mock_user_input_data.__repr__()
        self.assertEquals(str(EXPECTED_REP_OBJECT), rep_obj)

    ''''
    Verifies that proper dictionary is printed when action is change-password
    '''
    def test_user_input_data_change_password_is_printed_as_dict_properly(self):
        EXPECTED_REP_OBJECT={'action': 'change-password', 'new_password': '****'}
        mock_user_input_data = UserInputData(action='change-password', id=None, new_password='somepassword')

        rep_obj = mock_user_input_data.__repr__()
        self.assertEquals(str(EXPECTED_REP_OBJECT), rep_obj)
