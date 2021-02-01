import unittest
from unittest.mock import MagicMock, patch
import requests

from conjur.errors import OperationNotCompletedException, InvalidPasswordComplexityException
from conjur.user import UserController, UserInputData
from conjur.user.user_logic import UserLogic

class UserControllerTest(unittest.TestCase):
    user_logic = UserLogic
    user_input_data = UserInputData(action='rotate-api-key', id='someuser', new_password=None)

    def test_user_controller_constructor(self):
        mock_user_logic = None
        mock_user_input_data = None
        user_controller = UserController(mock_user_logic, mock_user_input_data)

        assert user_controller.user_logic == mock_user_logic
        assert user_controller.user_input_data == mock_user_input_data

    def test_operation_failure_raises_error(self):
        mock_user_logic = UserLogic
        user_controller = UserController(mock_user_logic, self.user_input_data)
        mock_user_logic.rotate_api_key = MagicMock(side_effect=OperationNotCompletedException)
        with self.assertRaises(OperationNotCompletedException):
            user_controller.rotate_api_key()

    def test_change_password_can_raise_authn_error(self):
        # mock the status code of the error received
        mock_response = MagicMock()
        mock_response.status_code=401

        mock_user_logic = UserLogic
        user_controller = UserController(mock_user_logic, self.user_input_data)
        user_controller.prompt_for_password = MagicMock()
        mock_user_logic.change_personal_password = MagicMock(side_effect=requests.exceptions.HTTPError(response=mock_response))
        with self.assertRaises(requests.exceptions.HTTPError):
            user_controller.change_personal_password()

    def test_change_password_can_raise_invalid_complexity_error(self):
        # mock the status code of the error received
        mock_response = MagicMock()
        mock_response.status_code=422

        mock_user_logic = UserLogic
        user_controller = UserController(mock_user_logic, self.user_input_data)
        user_controller.prompt_for_password = MagicMock()
        mock_user_logic.change_personal_password = MagicMock(side_effect=requests.exceptions.HTTPError(response=mock_response))
        with self.assertRaises(InvalidPasswordComplexityException):
            user_controller.change_personal_password()

    '''
    Verifies that the user is prompted to input their password and check_password_validity is called once
    '''
    def test_user_does_not_provide_password_prompts_for_one_and_is_verified(self):
        mock_user_logic = UserLogic
        mock_user_data = UserInputData(action='someaction', id='someuser', new_password=None)
        user_controller = UserController(mock_user_logic, mock_user_data)
        with patch('getpass.getpass', return_value='somepass'):
            user_controller.check_password_validity = MagicMock()
            user_controller.prompt_for_password()

            self.assertEquals(mock_user_data.new_password, 'somepass')
            user_controller.check_password_validity.assert_called_once()

    def test_empty_password_prompts_user_for_password_and_sets_it(self):
        mock_user_logic = UserLogic
        mock_user_data = UserInputData(action='someaction', id='someuser', new_password='')
        user_controller = UserController(mock_user_logic, mock_user_data)
        with patch('getpass.getpass', return_value='somepass'):
            user_controller.check_password_validity()
            self.assertEquals(mock_user_data.new_password, 'somepass')
