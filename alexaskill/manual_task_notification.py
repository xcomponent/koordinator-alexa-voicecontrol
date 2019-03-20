#!/usr/bin/python
# -*- coding:utf-8 -*-

import logging
import os
from dateutil import parser
from datetime import datetime
import pytz
import tzlocal

from alexaskill.json_handles import save_json, read_json

from alexaskill.scripts_koor.cc_scenario import check_manual_task_notification
from alexaskill.scripts_koor.cc_scenario import complete_manual_task, error_manual_task
from alexaskill.levenshtein_distance import levenshtein_distance
from alexaskill.json_request_handler import create_json_request

from configuration.koordinator_webhook_alexa_settings import FLASK_SERVER_HOST, SKILL_FLASK_SERVER_PORT

from flask import Flask

from flask_cors import CORS

from flask_ask import Ask, statement, question, session, request, context

app2 = Flask(__name__)
CORS(app2)

ask2 = Ask(app2, "/")

logging.getLogger("flask_ask").setLevel(logging.DEBUG)

generated_data_path = os.getcwd() + '\\alexaskill\\data\\generated\\'


@ask2.launch
def launch_skill():
    """
    Handles launch skill request
    :return: launch text response to Alexa from chat bot response
    """
    welcome_text = "Bienvenue chez notre agent de notification koordinator. Voulez-vous savoir si vous avez des notifications de tâches manuelles?"
    return question(welcome_text)


@ask2.intent("AMAZON.NoIntent")
def handle_stop_intent():
    """
    Handles stop intent by sending intent information to chat bot interface and receiving response from it
    :return: stop text response to Alexa from chat bot response
    """
    stop_text = "D'accord. Au revoir."
    delete_generated_files(generated_data_path, session.sessionId)
    return statement(stop_text)


@ask2.intent("ManualTaskValidation")
def handle_validate_task_intent():
    user_request = create_json_request(session, request, context.System.device.deviceId)
    print("Manual task validation", user_request)
    msg = ""
    workflow_name = extract_entity(user_request, "wkfName")
    time = extract_entity(user_request, "time")
    tsk_name = extract_entity(user_request, "tName")
    task_name, task_id, scenario_name = extract_task_scenario(user_request, workflow_name, time, tsk_name)
    if task_name == "" and task_id == "" and scenario_name == "":
        msg = "Désolée, je n'ai pas compris votre demande."
    print(task_name, task_id, scenario_name)
    validation_status = complete_manual_task(task_id)
    if validation_status:
        msg = "J'ai validé la tâche manuelle " + task_name + " du scénario " \
              + scenario_name + ". Voulez-vous savoir si vous avez d'autres notifications?"

    question_response = "?" in msg
    if question_response:
        return question(msg)
    delete_generated_files(generated_data_path, session.sessionId)
    return statement(msg)


@ask2.intent("ManualTaskCancellation")
def handle_cancel_task_intent():
    user_request = create_json_request(session, request, context.System.device.deviceId)
    print("Manual task cancellation", user_request)
    msg = ""
    workflow_name = extract_entity(user_request, "workflowName")
    time = extract_entity(user_request, "t")
    tsk_name = extract_entity(user_request, "taskName")
    task_name, task_id, scenario_name = extract_task_scenario(user_request, workflow_name, time, tsk_name)
    if task_name == "" and task_id == "" and scenario_name == "":
        msg = "Désolée, je n'ai pas compris votre demande."
    print(task_name, task_id, scenario_name)
    cancel_status = error_manual_task(task_id)
    if cancel_status:
        msg = "D'accord j'annule la tâche manuelle  " + task_name + " du scénario " \
              + scenario_name + ". Voulez-vous savoir si vous avez d'autres notifications?"

    question_response = "?" in msg
    if question_response:
        return question(msg)
    delete_generated_files(generated_data_path, session.sessionId)
    return statement(msg)


@ask2.intent("CheckNotification")
def handle_check_notification_intent():
    user_request = create_json_request(session, request, context.System.device.deviceId)
    print(user_request)
    workflow_name = extract_entity(user_request, "workflowName")
    session_id = session.sessionId
    generated_json_path = generated_data_path + session_id
    first_check_notification_request = not os.path.exists(generated_json_path + '__by_task.json')
    print("workflow_name", workflow_name)
    print("first_check_notification_request", first_check_notification_request)
    if workflow_name == "" and not first_check_notification_request:
        msg = "D'accord, voulez-vous la valider ou l'annuler?"
    elif workflow_name == "" and first_check_notification_request:
        task_notifications, all_notifications = check_manual_task_notification()
        save_json(generated_json_path, all_notifications)
        save_json(generated_json_path + "_by_workflow", task_notifications)
        print("task_notifications", task_notifications)
        print("all_notifications", all_notifications)
        if task_notifications == {} and all_notifications == []:
            msg = "Vous n'avez aucune notification. Au revoir"
        elif task_notifications is not None:
            scenario_names = list(task_notifications.keys())
            if len(task_notifications) == 1:
                notifications = task_notifications[scenario_names[0]]
                if len(notifications) == 1:
                    msg = "Vous avez une notification de la tâche manuelle " + notifications[0]["inputData"][
                        "taskName"] + " du scénario " + scenario_names[0] + ". Cette tâche a été crée par " \
                          + notifications[0]["userName"] + " à " + convert_to_local_time(notifications[0]["creationDate"]) \
                          + ". Voulez-vous agir sur cette tâche?"
                    save_json(generated_json_path + "_by_task", notifications[0])
                else:
                    creation_time = []
                    task_names = []
                    for notif in notifications:
                        creation_time.append(convert_to_local_time(notif["creationDate"]))
                        task_names.append(notif["inputData"]["taskName"])
                    msg = "Vous avez " + str(len(task_names)) + " notifications du scénario " + scenario_names[0] + \
                          ". Elles concernent les tâches : " + ", ".join(task_names[:-1]) + " et " + task_names[-1] + \
                          " qui ont été crées à " + ", ".join(creation_time[:-1]) + " et " + creation_time[-1] + \
                          ", respectivement par " + notifications[0]["userName"] + ". Voulez-vous agir sur l'une de ces tâches?"
                    save_json(generated_json_path + "_by_workflow_by_task", notifications)
            elif len(task_notifications) == 2:
                notifications_1 = task_notifications[scenario_names[0]]
                notifications_2 = task_notifications[scenario_names[1]]
                creation_times_1 = []
                task_names_1 = []
                for notif in notifications_1:
                    creation_times_1.append(convert_to_local_time(notif["creationDate"]))
                    task_names_1.append(notif["inputData"]["taskName"])
                creation_times_2 = []
                task_names_2 = []
                for notif in notifications_2:
                    creation_times_2.append(convert_to_local_time(notif["creationDate"]))
                    task_names_2.append(notif["inputData"]["taskName"])
                if len(notifications_1) == 1 and len(notifications_2) == 1:
                    creation_time_1 = creation_times_1[0]
                    task_name_1 = task_names_1[0]
                    creation_time_2 = creation_times_2[0]
                    task_name_2 = task_names_2[0]
                    msg = "Vous avez une notification de la tâche manuelle " + task_name_1 + \
                          " du scénario " + scenario_names[0] + ". Cette tâche a été crée par " \
                          + notifications_1[0]["userName"] + " à " + creation_time_1 + ". Et vous avez une notification de la tâche manuelle " + task_name_2 + \
                          " du scénario " + scenario_names[1] + ". Cette tâche a été crée par " \
                          + notifications_2[0]["userName"] + " à " + creation_time_2 + ". Voulez-vous agir sur l'une de ces tâches?"
                elif len(notifications_1) == 1 and len(notifications_2) > 1:
                    creation_time_1 = creation_times_1[0]
                    task_name_1 = task_names_1[0]
                    msg = "Vous avez une notification de la tâche manuelle " + task_name_1 + \
                          " du scénario " + scenario_names[0] + ". Cette tâche a été crée par " \
                          + notifications_1[0]["userName"] + " à " + creation_time_1 + ". Et vous avez " + str(len(task_names_2)) \
                          + " notifications du scénario " + scenario_names[1] + ". Elles concernent les tâches : " +\
                          ", ".join(task_names_2[:-1]) + " et " + task_names_2[-1] + " qui ont été crées à " + \
                          ", ".join(creation_times_2[:-1]) + " et " + creation_times_2[-1] + \
                          ", respectivement par " + notifications_2[0]["userName"] + ". Voulez-vous agir sur l'une de ces tâches?"
                elif len(notifications_1) > 1 and len(notifications_2) == 1:
                    creation_time_2 = creation_times_2[0]
                    task_name_2 = task_names_2[0]
                    msg = "Vous avez " + str(len(task_names_1)) + " notifications du scénario " + scenario_names[0] + \
                          ". Elles concernent les tâches : " + ", ".join(task_names_1[:-1]) + " et " + task_names_1[
                              -1] + " qui ont été crées à " + ", ".join(creation_times_1[:-1]) + " et à " + creation_times_1[-1] + \
                          ", respectivement par " + notifications_1[0]["userName"] + ". Et vous avez une notification de la tâche manuelle " + task_name_2 + \
                          " du scénario " + scenario_names[1] + ". Cette tâche a été crée par " \
                          + notifications_2[0]["userName"] + " à " + creation_time_2 + ". Voulez-vous agir sur l'une de ces tâches?"
                else:
                    msg = "Vous avez " + str(len(task_names_1)) + " notifications du scénario " + scenario_names[0] + \
                          ". Elles concernent les tâches : " + ", ".join(task_names_1[:-1]) + " et " + task_names_1[
                              -1] + " qui ont été crées à " + ", ".join(creation_times_1[:-1]) + " et à " + creation_times_1[-1] + \
                          ", respectivement par " + notifications_1[0]["userName"] + ". Et vous avez " + str(len(task_names_2)) \
                          + " notifications du scénario " + scenario_names[1] + ". Elles concernent les tâches : " +\
                          ", ".join(task_names_2[:-1]) + " et " + task_names_2[-1] + " qui ont été crées à " + \
                          ", ".join(creation_times_2[:-1]) + " et " + creation_times_2[-1] + \
                          ", respectivement par " + notifications_2[0]["userName"] + ". Voulez-vous agir sur l'une de ces tâches?"
            else:
                msg_list = []
                for name in scenario_names:
                    len_task_notif = len(task_notifications[name])
                    if len_task_notif == 1:
                        msg_list.append("une notification du scénario " + name)
                    else:
                        msg_list.append(str(len(task_notifications[name])) + " notifications du scénario " + name)
                msg = "Vous avez " + ", ".join(msg_list[:-1]) + " et " + msg_list[-1] + ". Quel scénario vous intéresse?"
    elif workflow_name != "":
        notifications_by_workflow = read_json(generated_json_path + "_by_workflow")
        task_scenario_names = list(notifications_by_workflow.keys())
        correct_workflow_name = extract_coorect_name_with_ld(workflow_name, task_scenario_names)
        print(correct_workflow_name)
        workflow_tasks = notifications_by_workflow[correct_workflow_name]
        task_names = []
        creation_times = []
        for task in workflow_tasks:
            task_names.append(task["inputData"]["taskName"])
            creation_times.append(convert_to_local_time(task["creationDate"]))
        if len(workflow_tasks) == 1:
            msg = "Vous avez une notification de la tâche manuelle " + task_names[0] + \
                  " du scénario " + correct_workflow_name + " en attente de votre validation. Cette tâche a été crée par " \
                    + workflow_tasks[0]["userName"] + " à " + creation_times[0] + ". Voulez-vous agir sur cette tâche?"
            save_json(generated_json_path + "_by_task", workflow_tasks[0])
        else:
            msg = "Vous avez " + str(len(task_names)) + " notifications du scénario " + correct_workflow_name + \
                ". Elles concernent les tâches : " + ", ".join(task_names[:-1]) + " et " + task_names[-1] + \
                " qui ont été crées à " + ", ".join(creation_times[:-1]) + " et " + creation_times[-1] + \
                ", respectivement par " + workflow_tasks[0]["userName"] + ". Voulez-vous agir sur l'une de ces tâches?"
            save_json(generated_json_path + "_by_workflow_by_task", workflow_tasks)
    else:
        msg = "Désolée, je n'ai pas compris votre demande."

    question_response = "?" in msg
    if question_response:
        return question(msg)
    delete_generated_files(generated_data_path, session.sessionId)
    return statement(msg)


def create_workflow_notifications_json(notifications):
    notifications_json = {}
    for notification in notifications:
        notification_json = {
            "workflow_name": notification["inputData"]["scenarioInstanceName"],
            "workflow_instance_id": notification["workflowInstanceId"],
            "task_instance_id": notification["id"],
            "creation_date": notification["creationDate"],
            "user_name": notification["userName"],
            "task_name": notification["inputData"]["taskName"],
            "task_description": notification["inputData"]["description"]
        }

    return notifications_json


def delete_generated_files(generated_data_path, session_id):
    for file in os.listdir(generated_data_path):
        if session_id in file:
            os.remove(os.path.join(generated_data_path, file))


dico = {"zéro": 0, "un": 1, "deux": 2, "trois": 3, "quatre": 4, "cinq": 5, "six": 6, "sept": 7, "huit": 8, "neuf": 9, "dix": 10}


def convert_to_local_time(utc_date):
    local_timezone = tzlocal.get_localzone()
    utc_time = parser.parse(utc_date)
    local_time = utc_time.replace(tzinfo=pytz.utc).astimezone(local_timezone)
    start_time = datetime.strftime(local_time, '%H:%M')
    return start_time


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


def extract_coorect_name_with_ld(name, name_list):
    list_ld = [(levenshtein_distance(n, name), n) for n in name_list]
    min_ld = min([x[0] for x in list_ld])
    task_name = [x[1] for x in list_ld if x[0] == min_ld]
    return task_name[0]


def extract_task_scenario(user_request, workflow_name, time, tsk_name):
    task_name = ""
    task_id = ""
    scenario_name = ""
    session_id = user_request["attributes"]["alexa_sessionId"]
    generated_json_path = generated_data_path + session_id
    all_notifications_json = os.path.exists(generated_json_path + '.json')
    many_notifications_by_scenario_json = os.path.exists(generated_json_path + '_by_workflow_by_task.json')
    one_notification_by_scenario_json = os.path.exists(generated_json_path + '_by_task.json')
    if one_notification_by_scenario_json:
        task_notification = read_json(generated_json_path + '_by_task')
        task_id = task_notification["id"]
        task_name = task_notification["inputData"]["taskName"]
        scenario_name = task_notification["inputData"]["scenarioInstanceName"]
    elif many_notifications_by_scenario_json:
        if tsk_name != "":
            task_notifications = read_json(generated_json_path + '_by_workflow_by_task')
            task_names = []
            for notif in task_notifications:
                task_names.append(notif["inputData"]["taskName"])
            correct_task_name = extract_coorect_name_with_ld(tsk_name, task_names)
            for notif in task_notifications:
                if notif["inputData"]["taskName"] == correct_task_name:
                    task_id = notif["id"]
            task_name = correct_task_name
            scenario_name = task_notifications[0]["inputData"]["scenarioInstanceName"]
    elif workflow_name != "":
        task_notifications = read_json(generated_json_path)
        task_scenario_json = read_json(generated_json_path + "_by_workflow")
        task_scenario_names = list(task_scenario_json.keys())
        correct_workflow_name = extract_coorect_name_with_ld(workflow_name, task_scenario_names)
        for notification in task_notifications:
            if notification["inputData"]["scenarioInstanceName"] == correct_workflow_name:
                task_name = notification["inputData"]["taskName"]
                task_id = notification["id"]
        scenario_name = correct_workflow_name
    elif time != "":
        all_notifications = read_json(generated_json_path)
        for notification in all_notifications:
            create_time = convert_to_local_time(notification["creationDate"])
            if create_time == time:
                task_name = notification["inputData"]["taskName"]
                task_id = notification["id"]
                scenario_name = notification["inputData"]["scenarioInstanceName"]

    return task_name, task_id, scenario_name


def main():
    if 'ASK_VERIFY_REQUESTS' in os.environ:
        verify = str(os.environ.get('ASK_VERIFY_REQUESTS', '')).lower()
        if verify == 'false':
            app2.config['ASK_VERIFY_REQUESTS'] = False
    app2.config.update(SESSION_COOKIE_NAME="session1")
    app2.run(port=SKILL_FLASK_SERVER_PORT, host=FLASK_SERVER_HOST, debug=True, threaded=True)
