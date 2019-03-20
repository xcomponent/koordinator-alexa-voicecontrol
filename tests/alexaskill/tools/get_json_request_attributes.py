import os
from alexaskill.json_handles import read_json


class GetAttributes:
    def __init__(self, **agent_attributes):
        for attr_name, attr_value in agent_attributes.items():
            setattr(self, attr_name, attr_value)


def get_session_attributes(alexa_json_file):
    #alexa_json = read_json(os.path.join('C:\\Users\Marwa Thlithi\\Desktop\\BookingRoomMeeting\\AlexaInvivooChatbot\\tests\\data', alexa_json_file))
    alexa_json = read_json(os.path.join('tests', 'data', alexa_json_file))
    alexa_data = GetAttributes(**alexa_json)
    session = GetAttributes(**alexa_data.session)
    application = GetAttributes(**session.application)
    user = GetAttributes(**session.user)
    session_attributes = {"new": 'true', "sessionId": session.sessionId, "application": application, "user": user}
    device_id = GetAttributes(**alexa_data.context).System['device']['deviceId']
    application_id = application.applicationId

    return device_id, application_id, session_attributes, alexa_data.request
