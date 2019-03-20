import os
import unittest

from alexaskill.json_handles import read_json
from alexaskill.create_user_request import create_json_request
from tests.alexaskill.tools.get_json_request_attributes import GetAttributes, get_session_attributes


class TestUserRequestJson(unittest.TestCase):

    def setUp(self):
        self.device_id_launch, self.application_id_launch, self.session_attributes_launch, \
            self.request_attributes_launch = get_session_attributes('Alexa_Launch_Request')

    def test_create_json_request(self):
        user_json_request = create_json_request(GetAttributes(**self.session_attributes_launch),
                                                GetAttributes(**self.request_attributes_launch),
                                                self.device_id_launch)
        self.assertDictEqual(user_json_request, read_json(os.path.join('tests', 'data', 'user_json_request')))

    def test_that_create_json_request_raise_exception_when_session_is_None(self):
        with self.assertRaises(Exception):
            create_json_request(session=None, request=GetAttributes(**self.request_attributes_launch),
                                device_id=self.device_id_launch)

    def test_that_create_json_request_raise_exception_when_request_is_None(self):
        with self.assertRaises(Exception):
            create_json_request(session=GetAttributes(**self.session_attributes_launch), request=None,
                                device_id=self.device_id_launch)

    def test_that_create_json_request_raise_exception_when_device_id_is_None(self):
        with self.assertRaises(Exception):
            create_json_request(session=GetAttributes(**self.session_attributes_launch),
                                request=GetAttributes(**self.request_attributes_launch),
                                device_id=None)


if __name__ == '__main__':
    unittest.main()
