import unittest
from unittest.mock import MagicMock, patch

from conjur.errors import OperationNotCompletedException, InvalidPasswordComplexityException, \
    HttpError, HttpStatusError
from conjur.controller.user_controller import UserController
from conjur.logic.user_logic import UserLogic
from conjur.data_object.user_input_data import UserInputData


class UserControllerTest(unittest.TestCase):
    user_logic = UserLogic
    user_input_data = UserInputData(action='rotate-api-key', id='someuser', new_password=None)

    def test_user_controller_constructor(self):
        mock_user_logic = None
        mock_user_input_data = None
        user_controller = UserController(mock_user_logic, mock_user_input_data)

        assert user_controller.user_logic == mock_user_logic
        assert user_controller.user_input_data == mock_user_input_data

    @patch('conjur.logic.user_logic')
    def test_operation_failure_raises_error(self, mock_user_logic):
        user_controller = UserController(mock_user_logic, self.user_input_data)
        mock_user_logic.rotate_api_key = MagicMock(side_effect=OperationNotCompletedException)
        with self.assertRaises(OperationNotCompletedException):
            user_controller.rotate_api_key()

    @patch('conjur.logic.user_logic')
    def test_login_rotate_api_key_can_raise_operation_not_completed_exception(self, mock_user_logic):
        mock_user_logic.rotate_api_key = MagicMock(side_effect=OperationNotCompletedException)
        mock_user_controller = UserController(mock_user_logic, self.user_input_data)
        with self.assertRaises(OperationNotCompletedException):
            mock_user_controller.rotate_api_key()

    @patch('conjur.logic.user_logic')
    def test_change_password_can_raise_authn_error(self, mock_user_logic):
        user_controller = UserController(mock_user_logic, self.user_input_data)
        user_controller.prompt_for_password = MagicMock()
        mock_user_logic.change_personal_password = MagicMock(
            side_effect=HttpStatusError(status=401))
        with self.assertRaises(HttpError):
            user_controller.change_personal_password()

    @patch('conjur.logic.user_logic')
    def test_change_password_can_raise_invalid_complexity_error(self, mock_user_logic):
        # mock the status code of the error received
        mock_response = MagicMock()
        mock_response.status_code = 422
        user_controller = UserController(mock_user_logic, self.user_input_data)
        user_controller.prompt_for_password = MagicMock()
        mock_user_logic.change_personal_password = MagicMock(
            side_effect=HttpError(response=mock_response))
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
