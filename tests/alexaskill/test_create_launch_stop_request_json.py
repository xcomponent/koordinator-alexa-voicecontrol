import os
import unittest
from unittest.mock import patch

from alexaskill.json_handles import read_json
from alexaskill.json_request_handler import create_json_launch_request, create_json_stop_request
import alexaskill.create_user_request
from tests.alexaskill.tools.get_json_request_attributes import GetAttributes, get_session_attributes

USER_JSON_REQUEST = read_json(os.path.join('tests', 'data', 'user_json_request'))


class TestLaunchStopRequest(unittest.TestCase):

    @patch('alexaskill.create_user_request.create_json_request', return_value=USER_JSON_REQUEST)
    def test_create_json_launch_request(self, create_json_request_mock):
        alexaskill.create_user_request.create_json_request = create_json_request_mock
        device_id, application_id, session_attributes, request_attributes = get_session_attributes(
            'Alexa_Launch_Request')
        user_launch_request = create_json_launch_request(GetAttributes(**session_attributes),
                                                         GetAttributes(**request_attributes),
                                                         device_id)
        self.assertEqual(create_json_request_mock.call_count, 1)
        self.assertEqual(user_launch_request["event"], "START")
        self.assertDictEqual(user_launch_request, read_json(os.path.join('tests', 'data', 'user_launch_request')))

    @patch('alexaskill.create_user_request.create_json_request', return_value=USER_JSON_REQUEST)
    def test_create_json_stop_request(self, create_json_request_mock):
        alexaskill.create_user_request.create_json_request = create_json_request_mock
        device_id, application_id, session_attributes, request_attributes = get_session_attributes(
            'Alexa_Stop_Request')
        print(session_attributes, request_attributes)
        user_stop_request = create_json_stop_request(GetAttributes(**session_attributes),
                                                     GetAttributes(**request_attributes),
                                                     device_id)
        self.assertEqual(create_json_request_mock.call_count, 1)
        self.assertEqual(user_stop_request["event"], "STOP")
        self.assertDictEqual(user_stop_request, read_json(os.path.join('tests', 'data', 'user_stop_request')))


if __name__ == '__main__':
    unittest.main()
