
def create_json_request(session, request, device_id):
    if not session:
        raise Exception("Invalid request - Session information is missing")
    if not request:
        raise Exception("Invalid request - Request information is missing")
    if not device_id:
        raise Exception("Invalid request - device identity is missing")
    json_information = {
        "stream": device_id,
        "user_id": session.user.userId,
        "language": request.locale[:2],
        "attributes": {
            "alexa_skillId": session.application.applicationId,
            "alexa_sessionId": session.sessionId,
            "alexa_requestId": request.requestId
        }
    }
    return json_information

