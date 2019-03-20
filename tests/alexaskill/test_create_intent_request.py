import os
import unittest
from unittest.mock import patch

from alexaskill.json_handles import read_json
from alexaskill.json_request_handler import create_json_intent_request
import alexaskill.create_user_request
from tests.alexaskill.tools.get_json_request_attributes import GetAttributes, get_session_attributes

USER_JSON_REQUEST = read_json(os.path.join('tests', 'data', 'user_json_request'))


class TestIntentRequest(unittest.TestCase):

    @patch('alexaskill.create_user_request.create_json_request', return_value=USER_JSON_REQUEST)
    def test_create_json_intent_request(self, create_json_request_mock):
        alexaskill.create_user_request.create_json_request = create_json_request_mock
        device_id, application_id, session_attributes, request = get_session_attributes('Alexa_Intent_Request')
        request_attributes = GetAttributes(**request)
        intent_attributes = GetAttributes(**request_attributes.intent)
        request_object = {"type": request_attributes.type, "requestId": request_attributes.requestId,
                          "timestamp": request_attributes.timestamp, "locale": request_attributes.locale,
                          "intent": intent_attributes}

        user_intent_request = create_json_intent_request(session=GetAttributes(**session_attributes),
                                                         request=GetAttributes(**request_object),
                                                         device_id=device_id)
        self.assertEqual(create_json_request_mock.call_count, 1)
        self.assertEqual(user_intent_request["intent"]["name"], "booking.meeting_room")
        self.assertDictEqual(user_intent_request, read_json(os.path.join('tests', 'data', 'user_intent_request')))

    @patch('alexaskill.create_user_request.create_json_request', return_value=USER_JSON_REQUEST)
    def test_that_create_json_intent_raise_exception_if_resolution_status_does_not_exist_for_custom_entity(
            self, create_json_request_mock):
        alexaskill.create_user_request.create_json_request = create_json_request_mock
        alexaskill.create_user_request.create_json_request = create_json_request_mock
        device_id, application_id, session_attributes, request = \
            get_session_attributes('Alexa_Intent_without_resolution_status')
        request_attributes = GetAttributes(**request)
        intent_attributes = GetAttributes(**request_attributes.intent)
        request_object = {"type": request_attributes.type, "requestId": request_attributes.requestId,
                          "timestamp": request_attributes.timestamp, "locale": request_attributes.locale,
                          "intent": intent_attributes}

        with self.assertRaises(Exception):
            create_json_intent_request(session=GetAttributes(**session_attributes),
                                       request=GetAttributes(**request_object),
                                       device_id=device_id)


if __name__ == '__main__':
    unittest.main()
