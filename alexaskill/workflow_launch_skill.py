#!/usr/bin/python
# -*- coding:utf-8 -*-

import logging
import os

from alexaskill.scripts_koor.cc_scenario import start_workflow, start_workflow_in_azure

from alexaskill.json_request_handler import create_json_request

from configuration.koordinator_webhook_alexa_settings import FLASK_SERVER_HOST, SKILL_FLASK_SERVER_PORT

from flask import Flask

from flask_cors import CORS

from flask_ask import Ask, statement, question, session, request, context

app1 = Flask(__name__)

CORS(app1)

ask1 = Ask(app1, "/service1")


logging.getLogger("flask_ask").setLevel(logging.DEBUG)


@ask1.launch
def launch_skill():
    """
    Handles launch skill request
    :return: launch text response to Alexa from chat bot response
    """
    welcome_text = "Bienvenue chez notre agent de lancement de scénario. Quelle scénario voulez-vous lancer?"
    return question(welcome_text)


@ask1.intent("AMAZON.StopIntent")
def handle_stop_intent():
    """
    Handles stop intent by sending intent information to chat bot interface and receiving response from it
    :return: stop text response to Alexa from chat bot response
    """
    stop_text = "D'accord. Au revoir."
    return statement(stop_text)


@ask1.intent("LaunchWorkflow")
def handle_workflow_launch_intent():
    """
    Handles workflow launch query
    :return: launch text response or a sugestion of workflow if the first workflow doesn't exist
    """
    user_request = create_json_request(session, request, context.System.device.deviceId)
    logging.info(user_request)
    workflow_name = extract_entity(user_request, "workflowName")
    msg = launch_workflow(workflow_name)
    question_response = "?" in msg
    if question_response:
        return question(msg)
    return statement(msg)


@ask1.intent("AMAZON.NoIntent")
def handle_no_intent():
    return statement("D'accord, merci et à bientôt.")


dico = {"zéro": 0, "un": 1, "deux": 2, "trois": 3, "quatre": 4, "cinq": 5, "six": 6, "sept": 7, "huit": 8, "neuf": 9, "dix": 10}


def launch_workflow(workflow_name):
    if workflow_name != "":
        logging.info("workflow name", workflow_name)
        workflow_list_name, wkf_name, starting_status = start_workflow(workflow_name)
        # workflow_list_name, wkf_name, starting_status = start_workflow_in_azure(workflow_name)
        if starting_status <= 205:
            if not workflow_list_name:
                msg = "D'accord, je lance le scénario " + wkf_name + ". Voulez-vous lancer un autre scénario?"
            else:
                if len(workflow_list_name) > 1:
                    msg = "J'ai trouvé " + str(len(workflow_list_name)) + " scénarios qui ont des noms similaires au nom du scénario que vous voulez lancer." \
                          " Les noms de ces scénarios sont " + ", ".join(
                        workflow_list_name[:-1]) + " et " + workflow_list_name[-1] + ". Lequel de ces scénarios voulez-vous lancer ?"
        else:
            msg = "Le scénario " + workflow_name + " n'a pas pu être lancé."
    else:
        msg = "D'accord, quelle scénario voulez-vous lancer?"

    return msg


def extract_entity(user_request, entity_name):
    entities = user_request["intent"]["entities"]
    for entity in entities:
        if entity["name"] == entity_name:
            workflow_name = entity["value"]
    if workflow_name.find(" ") > 0:
        for ch in workflow_name.split():
            if ch in dico.keys():
                workflow_name = workflow_name.replace(ch, str(dico[ch]))
    return workflow_name.replace(" ", "")


def main():
    if 'ASK_VERIFY_REQUESTS' in os.environ:
        verify = str(os.environ.get('ASK_VERIFY_REQUESTS', '')).lower()
        if verify == 'false':
            app1.config['ASK_VERIFY_REQUESTS'] = False
    app1.run(port=SKILL_FLASK_SERVER_PORT, host=FLASK_SERVER_HOST, debug=True, threaded=True)
