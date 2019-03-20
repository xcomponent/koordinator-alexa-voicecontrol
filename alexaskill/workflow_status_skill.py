#!/usr/bin/python
# -*- coding:utf-8 -*-

import logging
import os

from alexaskill.scripts_koordinator.cc_scenario import start_workflow_in_azure, scenario_status

from dateutil import parser
from datetime import datetime
import pytz
import tzlocal

from alexaskill.json_request_handler import create_json_request

from alexaskill.json_handles import save_json, read_json

from configuration.koordinator_webhook_alexa_settings import FLASK_SERVER_HOST, SKILL_FLASK_SERVER_PORT

from flask import Flask

from flask_cors import CORS

from flask_ask import Ask, statement, question, session, request, context

app2 = Flask(__name__)
CORS(app2)

ask2 = Ask(app2, "/service2")

logging.getLogger("flask_ask").setLevel(logging.DEBUG)


@ask2.launch
def launch_skill():
    """
    Handles launch skill request
    :return: launch text response to Alexa from chat bot response
    """
    welcome_text = "Bienvenue chez notre agent de suivi koordinator. Quel scénario vous intéresse ?"
    return question(welcome_text)


@ask2.intent("AMAZON.StopIntent")
def handle_stop_intent():
    """
    Handles stop intent by sending intent information to chat bot interface and receiving response from it
    :return: stop text response to Alexa from chat bot response
    """
    stop_text = "D'accord. Au revoir."
    return statement(stop_text)


@ask2.intent("AMAZON.NoIntent")
def handle_no_intent():
    return statement("D'accord, à bientôt.")


def delete_generated_files(generated_data_path, session_id):
    for file in os.listdir(generated_data_path):
        if session_id in file:
            os.remove(os.path.join(generated_data_path, file))


def extract_generated_json(generated_data_path, session_id, time_or_status):
    try:
        for file in os.listdir(generated_data_path):
            if session_id in file and time_or_status in file:
                print("file", file)
                json_path = os.path.join(generated_data_path, file)
        json_name, json_extension = os.path.splitext(json_path)
    except:
        return None
    return json_name


def convert_to_local_time(utc_date):
    local_timezone = tzlocal.get_localzone()
    utc_time = parser.parse(utc_date)
    local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(local_timezone)
    start_time = datetime.strftime(local_time, '%H:%M')
    return start_time


@ask2.intent("WorkflowStatus")
def handle_workflow_status_intent():
    msg = ""
    session_id = session.sessionId
    generated_data_path = os.getcwd() + '\\alexaskill\\data\\generated\\'
    generated_json_path = generated_data_path + session_id
    user_request = create_json_request(session, request, context.System.device.deviceId)
    print(user_request)
    wkf_name = extract_entity(user_request, "workflowName")
    time = extract_entity(user_request, "time")
    workflow_status = extract_entity(user_request, "instanceStatus")
    workflow_path = generated_json_path + "_"
    if wkf_name != "":
        print("wkf name", wkf_name)
        workflow_list_name, running_workflows, finished_workflows = scenario_status(wkf_name)
        if type(workflow_list_name) != list:
            workflow_name = workflow_list_name
            running_workflows_time = []
            error_workflows_time = []
            error_workflows_pos = []
            if running_workflows == None and finished_workflows == None:
                return statement("le scénario qui vous intéresse n'existe.")
            elif running_workflows == [] and finished_workflows == []:
                return statement("Aucune instance du scénario " + workflow_list_name + " n'a été lancée aujourd'hui. Etes-vous intéressé par un autre scénario?")
            else:
                if len(running_workflows) != 0:
                    for wkf in running_workflows:
                        run_start_time = convert_to_local_time(wkf["startDate"])
                        running_workflows_time.append(run_start_time)
                        run_start_time_json = run_start_time.replace(":", "-")
                        save_json(workflow_path + "running_" + run_start_time_json, create_workflow_json(wkf, workflow_name))
                if len(finished_workflows) != 0:
                    for wkf in range(0, len(finished_workflows)):
                        if len(finished_workflows[wkf]["errorTasks"]) != 0:
                            err_start_time = convert_to_local_time(finished_workflows[wkf]["startDate"])
                            error_workflows_time.append(err_start_time)
                            error_workflows_pos.append(wkf)
                            err_start_time_json = err_start_time.replace(":", "-")
                            save_json(workflow_path + "error_" + err_start_time_json, create_workflow_json(finished_workflows[wkf], workflow_name))
                running_workflows_number = len(running_workflows_time)
                error_workflows_number = len(error_workflows_time)
                if running_workflows_number > 1 and error_workflows_number > 1:
                    msg = "Il y a " + str(running_workflows_number) + " instances du scénario " + workflow_list_name + " en cours d'exécution. Elles ont été lancées" \
                            " aujourd'hui à " + ", ".join(running_workflows_time[:-1]) + " et " + running_workflows_time[-1] + \
                          ". Et il y a " + str(error_workflows_number) + " instances de ce scénario finies en état d'erreur. Ces instances ont " \
                            "été lancées aujourd'hui à " + ", ".join(error_workflows_time[:-1]) + " et " + error_workflows_time[-1] + \
                          " . Voulez-vous avoir plus de détails sur l'une de ces instances?"
                elif running_workflows_number > 1 and error_workflows_number == 1:
                    msg = "Il y a " + str(running_workflows_number) + " instances du scénario " + workflow_list_name + " en cours d'exécution. Elles ont été lancées" \
                        " aujourd'hui à " + ", ".join(running_workflows_time[:-1]) + " et " + running_workflows_time[-1] + \
                          ". Et il y a une instance de ce scénario finie en état d'erreur. Elle a été " \
                        "lancée aujourd'hui à " + error_workflows_time[0] + \
                          " . Voulez-vous avoir plus de détails sur l'une de ces instances?"
                elif running_workflows_number == 1 and error_workflows_number > 1:
                    msg = "Il y a une instance du scénario " + workflow_list_name + " en cours d'exécution. Elle a été lancée" \
                        " aujourd'hui à " + running_workflows_time[0] + \
                          ". Et il y a " + str(error_workflows_number) + " instances de ce scénario finies en état d'erreur. Ces instances ont " \
                        "été lancées aujourd'hui à " + ", ".join(error_workflows_time[:-1]) + " et " + error_workflows_time[-1] + \
                          " . Voulez-vous avoir plus de détails sur l'une de ces instances?"
                elif running_workflows_number > 1 and error_workflows_number == 0:
                    msg = "Il y a " + str(running_workflows_number) + " instances de ce scénario en cours d'exécution. Elles ont été lancées" \
                            " aujourd'hui à " + ", ".join(running_workflows_time[:-1]) + " et " + running_workflows_time[-1] + \
                            " . Voulez-vous avoir plus de détails sur l'une de ces instances?"
                elif error_workflows_number > 1 and running_workflows_number == 0:
                    msg = "Il y a " + str(error_workflows_number) + " instances de ce scénario en cours d'erreur. Elles ont été lancées" \
                            " aujourd'hui à " + ", ".join(error_workflows_time[:-1]) + " et " + error_workflows_time[-1] + \
                            " . Voulez-vous avoir plus de détails sur l'une de ces instances?"
                elif running_workflows_number == 1 and error_workflows_number == 1:
                    msg = "Il y a une instance de ce scénario en cours d'exécution qui a été lancée" \
                          " aujourd'hui à " + running_workflows_time[0] + " et une instance finie en état d'erreur lancée aujourd'hui à " \
                          + error_workflows_time[0] + " . Voulez-vous avoir plus de détails sur l'une de ces instances?"
                elif running_workflows_number == 1 and error_workflows_number == 0:
                    running_tasks_name = extract_task_names(running_workflows[0], "runningTasks")
                    if len(running_tasks_name) > 1:
                        msg = "Il y a une instance de ce scénario en cours d'exécution. Elle a été lancée" \
                              " aujourd'hui à " + running_workflows_time[0] + ". Et les tâches de cette instance qui " \
                                "sont en cours d'exécution sont : " + ", ".join(running_tasks_name[:-1]) + " et " \
                              + running_tasks_name[-1] + ". Etes-vous intéressé par un autre scénario?"
                    else:
                        msg = "Il y a une instance de ce scénario en cours d'exécution. Elle a été lancée" \
                              " aujourd'hui à " + running_workflows_time[0] + ". Et la tâche de cette instance qui " \
                                "est en cours d'exécution est : " + running_tasks_name[0] + ". Etes-vous intéressé par un autre scénario?"
                elif running_workflows_number == 0 and error_workflows_number == 1:
                    error_tasks_name = extract_task_names(finished_workflows[error_workflows_pos[0]], "errorTasks")
                    if len(error_tasks_name) > 1:
                        msg = "Il y a une instance de ce scénario en état d'erreur. Elle a été lancée" \
                              " aujourd'hui à " + error_workflows_time[0] + ". Et les tâches de cette instance qui " \
                                "sont en état d'erreur sont : " + ", ".join(error_tasks_name[:-1]) + " et " + \
                                error_tasks_name[-1] + ". Etes-vous intéressé par un autre scénario?"
                    else:
                        msg = "Il y a une instance de ce scénario en état d'erreur. Elle a été lancée" \
                              " aujourd'hui à " + error_workflows_time[0] + ". Et la tâche de cette instance qui " \
                                "est en état d'erreur est : " + error_tasks_name[0] + ". Etes-vous intéressé par un autre scénario?"
        else:
            msg = "J'ai trouvé " + str(len(workflow_list_name)) + " scénarios qui ont des noms similaires au nom du scénario qui vous intéresse." \
                    " Les noms de ces scénarios sont " + ", ".join(workflow_list_name[:-1]) + " et " + workflow_list_name[-1]\
                  + ". Lequel de ces scénarios qui vous intéresse ?"

    if time != "":
        print("instance launched time", time)
        time_json = time.replace(":", "-")
        print("generated data path", generated_data_path)
        print(session_id)
        print(time)
        print(time_json)
        workflow_json_path = extract_generated_json(generated_data_path, session_id, time_json)
        if not workflow_json_path:
            msg = "Il n'y a aucune instance lancée à cet heure. Etes-vous intéressé par un autre scénario?"
        else:
            workflow_json = read_json(workflow_json_path)
            msg = extract_tasks_name(workflow_json)

    if workflow_status != "":
        if workflow_status == "exécution" or workflow_status == "s'exécuter" or workflow_status == "d'exécution":
            workflow_json_path = extract_generated_json(generated_data_path, session_id, "running")
        else:
            workflow_json_path = extract_generated_json(generated_data_path, session_id, "error")
        if not workflow_json_path:
            msg = "Il n'y a aucune instance lancée à cet état. Etes-vous intéressé par un autre scénario?"
        else:
            workflow_json = read_json(workflow_json_path)
            msg = extract_tasks_name(workflow_json)

    if wkf_name == "" and time == "" and workflow_status == "":
        msg = "Quel scénario vous intéresse?"

    question_response = "?" in msg
    if question_response:
        return question(msg)
    delete_generated_files(generated_data_path, session_id)
    return statement(msg)


def extract_tasks_name(workflow_json):
    if workflow_json["status"] == "Running":
        running_tasks_name = workflow_json["running_tasks"]
        if len(running_tasks_name) > 1:
            print(running_tasks_name)
            msg = "Les tâches en cours d'exécution de cette instance sont : " + \
                  ", ".join(running_tasks_name[:-1]) + " et " + running_tasks_name[-1] + \
                  ". Etes-vous intéressé par un autre scénario?"
        else:
            msg = "C'est la tâche " + running_tasks_name[0] + " de cet instance qui est en cours d'exécution" + \
                  ". Etes-vous intéressé par un autre scénario?"
    else:
        error_tasks_name = workflow_json["error_tasks"]
        if len(error_tasks_name) > 1:
            msg = "Les tâches qui sont en état d'erreur de cette instance sont : " + \
                  ", ".join(error_tasks_name[:-1]) + " et " + error_tasks_name[-1] + \
                  ". Etes-vous intéressé par un autre scénario?"
        else:
            msg = "La tâche qui est en état d'erreur de cette instance est : " + error_tasks_name[0] +\
                  ". Etes-vous intéressé par un autre scénario?"
    return msg


# @ask2.intent("LaunchErrorWorkflow")
# def handle_workflow_status_intent():
  #  session_id = session.sessionId
   # generated_json_path = os.getcwd() + '\\alexaskill\\data\\generated\\' + session_id
    #user_request = create_json_request(session, request, context.System.device.deviceId)
    #logging.info(user_request)
    #wkf_name = extract_entity(user_request, "workflowName")
    #if wkf_name == "":
     #   workflow_name = read_json(generated_json_path)["workflow_name"]
    #else:
     #   workflow_name = wkf_name
    #msg = launch_error_workflow(workflow_name)
    #question_response = "?" in msg
    #if question_response:
     #   return question(msg)
    #return statement(msg)


dico = {"zéro": 0, "un": 1, "deux": 2, "trois": 3, "quatre": 4, "cinq": 5, "six": 6, "sept": 7, "huit": 8, "neuf": 9, "dix": 10}


def launch_error_workflow(workflow_name):
    workflow_list_name, wkf_name, starting_status = start_workflow_in_azure(workflow_name)
    if starting_status <= 205:
        if not workflow_list_name:
            msg = "D'accord, je relance le scénario " + wkf_name + "."
        else:
            if len(workflow_list_name) > 1:
                msg = "J'ai trouvé plusieurs scénarios qui ont des noms similaires au nom du scénario que vous voulez relancer." \
                      " Les noms de ces scénarios sont " + ", ".join(
                    workflow_list_name[:-1]) + " et " + workflow_list_name[-1] + ". Lequel de ces scénarios voulez-vous relancer?"
    else:
        msg = "Le scénario " + workflow_name + " n'a pas pu être relancé."

    return msg


def extract_entity(user_request, entity_name):
    entities = user_request["intent"]["entities"]
    name = ""
    for entity in entities:
        if entity["name"] == entity_name:
            name = entity["value"]
    if name.find(" ") > 0:
        for ch in name.split():
            if ch in dico.keys():
                name = name.replace(ch, str(dico[ch]))
    return name.replace(" ", "")


def extract_task_names(workflow, task_type):
    tasks_name = []
    for task in workflow[task_type]:
        print("task ", task)
        tasks_name.append(task["description"])
    return list(set(tasks_name))


def create_workflow_json(workflow, workflow_name):
    running_tasks_name = extract_task_names(workflow, "runningTasks")
    error_tasks_name = extract_task_names(workflow, "errorTasks")

    workflow_json = {
        "workflow_name": workflow_name,
        "status": workflow["status"],
        "start_date": workflow["startDate"],
        "running_tasks": running_tasks_name,
        "error_tasks": error_tasks_name
    }
    return workflow_json


def main():
    if 'ASK_VERIFY_REQUESTS' in os.environ:
        verify = str(os.environ.get('ASK_VERIFY_REQUESTS', '')).lower()
        if verify == 'false':
            app2.config['ASK_VERIFY_REQUESTS'] = False
    app2.config.update(SESSION_COOKIE_NAME="session1")
    app2.run(port=SKILL_FLASK_SERVER_PORT, host=FLASK_SERVER_HOST, debug=True, threaded=True)
