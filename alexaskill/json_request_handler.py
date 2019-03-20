from alexaskill import create_user_request


def create_json_request(session, request, device_id):
    if request.type == 'LaunchRequest':
        request_json = create_json_launch_request(session, request, device_id)
    elif request.type == 'IntentRequest':
        if request.intent.name == 'AMAZON.StopIntent':
            request_json = create_json_stop_request(session, request, device_id)
        else:
            request_json = create_json_intent_request(session, request, device_id)
    return request_json


def create_json_launch_request(session, request, device_id):
    """
    Creates user json request for launch request
    :param session: object containing session attributes
    :param request: object containing request attributes
    :param device_id: string containing the deviceId
    :return: json of chat bot response for launch request
    """
    json_launch_request = create_user_request.create_json_request(session, request, device_id)
    json_launch_request["event"] = "START"
    return json_launch_request


def create_json_stop_request(session, request, device_id):
    """
    Creates user json request for stop request
    :param session: object containing session attributes
    :param request: object containing request attributes
    :param device_id: string containing the deviceId
    :return: json of chat bot response for stop request
    """
    json_stop_request = create_user_request.create_json_request(session, request, device_id)
    json_stop_request["event"] = "STOP"
    return json_stop_request


def create_json_intent_request(session, request, device_id):
    """
    Creates user json request for intent request
    :param session: object containing session attributes
    :param request: object containing request attributes, intent and entities
    :param device_id: string containing the deviceId
    :return: json of chat bot response for intent request
    """
    request_information = create_user_request.create_json_request(session, request, device_id)
    request_information["intent"] = {}
    intent_name = request.intent.name
    request_information["intent"]["name"] = ''.join('_' + char.lower() if char.isupper() else char
                                            for char in intent_name.replace("_", ".")).lstrip('_').replace("._", ".")
    request_information["intent"]["entities"] = []
    for key in request.intent.slots.keys():
        entity_information = {
            "name": request.intent.slots[key]['name']
        }
        if "value" in request.intent.slots[key]:
            entity_information["value"] = request.intent.slots[key]['value']
        else:
            entity_information["value"] = ""
        if "resolutions" in request.intent.slots[key]:
            try:
                if request.intent.slots[key]['resolutions']["resolutionsPerAuthority"][0]['status']['code'] \
                        == "ER_SUCCESS_MATCH":
                    entity_information["status"] = "SUCCESS_MATCH"
                else:
                    entity_information["status"] = "SUCCESS_NOT_MATCH"
            except KeyError:
                raise Exception("Resolution status for the custom entity %s of the intent %s is not found" %
                      (key, request_information["intent"]["name"]))
        request_information["intent"]["entities"].append(entity_information)
    return request_information
