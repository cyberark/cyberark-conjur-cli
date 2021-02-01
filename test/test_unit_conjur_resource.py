import unittest

from conjur.resource import Resource

class ConjurResourceDataTest(unittest.TestCase):

    def test_full_id_returns_pair_properly(self):
        mock_resource = Resource(type_="sometype", name="somename")
        resource_pair = mock_resource.full_id()

        assert resource_pair == "sometype:somename"

    def test_host_input_data_rotate_api_key_is_printed_as_dict_properly(self):
        EXPECTED_REP_OBJECT="'type': 'sometype', 'name': 'somename'"
        mock_resource = Resource(type_="sometype", name="somename")

        self.assertEquals(str(EXPECTED_REP_OBJECT), mock_resource.__repr__())
