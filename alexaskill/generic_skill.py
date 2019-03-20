#!/usr/bin/python
# -*- coding:utf-8 -*-

import logging
import os
import datetime
import json
import requests
from queue import Queue, Empty
from threading import RLock, Thread

from alexaskill.json_request_handler import create_json_request

from configuration.koordinator_webhook_alexa_settings import bot_messaging_url, bot_response_url

from configuration.koordinator_webhook_alexa_settings import FLASK_SERVER_HOST, SKILL_FLASK_SERVER_PORT

from flask import Flask

from flask_cors import CORS

from flask_ask import Ask, statement, question, session, request, context

app = Flask(__name__)
CORS(app)

ask = Ask(app, "/")

skill_queue = Queue()

logging.getLogger("flask_ask").setLevel(logging.DEBUG)


@ask.launch
def launch_skill():
    """
    Handles launch skill request
    :return: launch text response to Alexa from chat bot response
    """
    welcome_text = "Bienvenue chez notre agent de réservation de salle de réunion" \
                   "Vous voulez réserver quelle salle de réunion et pour quand?"
    return question(welcome_text)


@ask.intent("AMAZON.StopIntent")
def handle_stop_intent():
    """
    Handles stop intent by sending intent information to chat bot interface and receiving response from it
    :return: stop text response to Alexa from chat bot response
    """
    stop_text = "D'accord. Au revoir."
    return statement(stop_text)


@ask.default_intent
def handle_all_intents():
    """
    Retrieves intent and entities information from Alexa json
    Creates user json and send it to chat bot interface
    Receives chat bot response
    :return: text response to Alexa from chat bot response
    """
    logging.info('Start time', datetime.datetime.now().time())
    user_request = create_json_request(session, request, context.System.device.deviceId)
    print("user request", user_request)
    response_text = handle_user_request(user_request)
    logging.info('End time', datetime.datetime.now().time())
    question_response = "?" in response_text
    if question_response:
        return question(response_text)
    return statement(response_text)


def handle_user_request(user_request):
    session_queue = get_chat_queue(user_request['attributes']['alexa_sessionId'])
    send_alexa_request(user_request)
    response_text = wait_bot_response(session_queue, timeout=7)
    return response_text


def wait_bot_response(session_queue, timeout):
    try:
        bot_response = session_queue.get(True, timeout=timeout)
        if bot_response:
            text_list = bot_response["text_data"]
        if not text_list:
            raise Exception('Intent response is empty')
        response_text = " ".join(text_list)
    except Empty:
        response_text = "Renouvelez votre demande plus tard. A bientôt."
    return response_text


_cache_messages = dict()
_cache_lock = RLock()


def send_alexa_request(user_request):
    """
    Send message to the chat bot
    :param user_request: user request information
    :return:
    """
    headers = {'content-type': 'application/json'}
    response = requests.post(bot_messaging_url, data=json.dumps(user_request), headers=headers)
    response.raise_for_status()


def get_chat_queue(session_id) -> Queue:
    with _cache_lock:
        if session_id in _cache_messages:
            cache = _cache_messages[session_id]
        else:
            cache = _cache_messages[session_id] = Queue()

    return cache


@app.before_first_request
def start_skill_listener():
    def start_runner():
        while True:
            try:
                logging.info('Get bot response')
                response = requests.get(bot_response_url)
                if response.status_code == 200:
                    data = response.json()["messages"]
                    logging.info('Received responses: ', data)
                    for msg in data:
                        if msg["type"] == "text":
                            session_queue = get_chat_queue(msg["attributes"]["alexa_sessionId"])
                            session_queue.put(msg)
            except:
                logging.info('Response not yet get')

    logging.info('Started runner')
    thread = Thread(target=start_runner)
    thread.start()


def main():
    if 'ASK_VERIFY_REQUESTS' in os.environ:
        verify = str(os.environ.get('ASK_VERIFY_REQUESTS', '')).lower()
        if verify == 'false':
            app.config['ASK_VERIFY_REQUESTS'] = False
    app.run(port=SKILL_FLASK_SERVER_PORT, host=FLASK_SERVER_HOST, debug=True, threaded=True)
