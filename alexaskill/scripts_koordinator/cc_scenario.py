#!/usr/bin/env python
# cc_scenario.py - call the API functions exposed by Command Center
#
# This file corresponds to Command Center software version 2.2.1-B71

"""The 'cc' model (for Command Center) lets us work at the python level. Inputs
and outputs to and from these functions are either simples types or python
objects, but never json. The cc module translates to and from json as required,
so the clients never have to do it.
"""

import sys
from dateutil import parser
from datetime import datetime
import time
import json
import uuid
import requests
from alexaskill.scripts_koordinator import common
from alexaskill.scripts_koordinator import cc_common
from alexaskill.scripts_koordinator import cc_polling
from alexaskill.scripts_koordinator import cc_monitoring
from alexaskill.scripts_koordinator import post
from alexaskill.scripts_koordinator import k
from alexaskill.levenshtein_distance import levenshtein_distance, common_characters

# -----------------------------------------------------------------------------
# I want stdout to be unbuffered, always
# -----------------------------------------------------------------------------


class Unbuffered(object):
    def __init__(self, stream):
        self.stream = stream

    def write(self, data):
        self.stream.write(data)
        self.stream.flush()

    def __getattr__(self, attr):
        return getattr(self.stream, attr)


sys.stdout = Unbuffered(sys.stdout)

# -----------------------------------------------------------------------------
# Global settings
# -----------------------------------------------------------------------------

api_url = 'http://localhost:443/workflowsservice'

# =============================================================================
# Low level functions
# =============================================================================

# -----------------------------------------------------------------------------
# Get all the scenario definitions
# -----------------------------------------------------------------------------

def get_scenarios():
    url = api_url + '/api/Search'
    status, data = post.httpRequest(url, 'GET', None)
    if status == 200:
        # Return value is an array of WorkflowDefinitions.
        obj = json.loads(data)
        wkf_defs = [k.WorkflowDefinition.from_json_decoded(o) for o in obj]
        return status, wkf_defs
    return status, data

# -----------------------------------------------------------------------------
# Get scenario's last version
# -----------------------------------------------------------------------------

def scen_get_id_version(name):
    #url = api_url + '/api/scenario-definitions'
    url = "http://localhost:7060/api/scenario-definitions"

    # Cancelled has two query parameters
    query_params = dict(
        workspaceName='BusinessAnalysts',
        returnAllWorkflowDefinitionVersions='false',
    )

    r = requests.get(url + '/api/scenario-definitions',
                     auth=common.auth, params=query_params)
    # status, data = post.httpRequest(url, 'GET', None, fields=query_params)
    status = r.status_code
    data = r.text
    print(r.status_code)
    if status == 200:
        # Return value is an array of WorkflowDefinitions.
        obj = json.loads(data)
        wkf_defs = [k.WorkflowDefinition.from_json_decoded(o) for o in obj]
        # same workflow definition can have several versions
        idv_list = [(x.id, x.versionNumber) for x in wkf_defs if x.name == name]

        vmax = 0
        for x in idv_list:
            if x[1] > vmax:
                vmax = x[1]
        return status, x[0], vmax
    return status, data


def scen_get_id_version_using_levenshtein(name, url):
     # url = api_url + '/api/scenario-definitions'

    # Cancelled has two query parameters
    query_params = dict(
        workspaceName='BusinessAnalysts',
        returnAllWorkflowDefinitionVersions='false',
    )

    r = requests.get(url,
                        auth=common.auth, params=query_params)
    #status, data = post.httpRequest(url, 'GET', None, fields=query_params)
    status = r.status_code
    data = r.text
    if status == 200:
        # Return value is an array of WorkflowDefinitions.
        obj = json.loads(data)
        wkf_defs = [k.WorkflowDefinition.from_json_decoded(o) for o in obj]
        # same workflow definition can have several versions
        idv_list = [(x.id, x.versionNumber, x.name) for x in wkf_defs if x.name.lower() == name.lower()]
        if idv_list == []:
            idv_list_ld = [(levenshtein_distance(x.name, name), x.id, x.versionNumber, x.name) for x in wkf_defs]
            min_ld = min([x[0] for x in idv_list_ld])
            wkf_list = [x[3] for x in idv_list_ld if x[0] == min_ld]
            idv = list(set(wkf_list))
            idv_list = [(x[1], x[2], x[3]) for x in idv_list_ld if x[0] == min_ld]
            if len(idv) > 1:
                if len(name) >= min_ld:
                    wkf_common_characters = [(common_characters(x[2], name), x[0], x[1], x[2]) for x in idv_list]
                    max_common_charac = max([x[0] for x in wkf_common_characters])
                    wkf_list_filtered = [x[3] for x in wkf_common_characters if x[0] == max_common_charac]
                    wkf_list_filtered_u = list(set(wkf_list_filtered))
                    if len(wkf_list_filtered_u) == 1:
                        idv_list = [(x[1], x[2], x[3]) for x in wkf_common_characters if x[0] == max_common_charac]
                    if len(list(set(wkf_list_filtered))) > 1:
                        return status, list(set(wkf_list_filtered)), None, None

        vmax = 0
        for x in idv_list:
            if x[1] > vmax:
                vmax = x[1]
        return status, x[0], vmax, x[2]
    return status, data


def extract_correct_workflow_name(name, url):
    query_params = dict(
        workspaceName='BusinessAnalysts',
        returnAllWorkflowDefinitionVersions='false',
    )

    r = requests.get(url,
                     auth=common.auth, params=query_params)
    status = r.status_code
    data = r.text
    print("workflow name", name)
    print("get workflow name status", status)
    if status == 200:
        # Return value is an array of WorkflowDefinitions.
        obj = json.loads(data)
        wkf_defs = [k.WorkflowDefinition.from_json_decoded(o) for o in obj]
        # same workflow definition can have several versions
        idv_list = [(x.id, x.versionNumber, x.name) for x in wkf_defs if x.name.lower() == name.lower()]
        if idv_list == []:
            idv_list_ld = [(levenshtein_distance(x.name, name), x.id, x.versionNumber, x.name) for x in wkf_defs]
            min_ld = min([x[0] for x in idv_list_ld])
            wkf_list = [x[3] for x in idv_list_ld if x[0] == min_ld]
            idv = list(set(wkf_list))
            idv_list = [(x[1], x[2], x[3]) for x in idv_list_ld if x[0] == min_ld]
            if len(idv) > 1:
                if len(name) >= min_ld:
                    wkf_common_characters = [(common_characters(x[2], name), x[0], x[1], x[2]) for x in idv_list]
                    max_common_charac = max([x[0] for x in wkf_common_characters])
                    wkf_list_filtered = [x[3] for x in wkf_common_characters if x[0] == max_common_charac]
                    wkf_list_filtered_u = list(set(wkf_list_filtered))
                    if len(wkf_list_filtered_u) == 1:
                        idv_list = [(x[1], x[2], x[3]) for x in wkf_common_characters if x[0] == max_common_charac]
                    if len(list(set(wkf_list_filtered))) > 1:
                        return status, list(set(wkf_list_filtered)), None, None

        vmax = 0
        for x in idv_list:
            if x[1] > vmax:
                vmax = x[1]
        return status, x[0], vmax, x[2]
    return status, data


# -----------------------------------------------------------------------------
# Post a scenario definition
# -----------------------------------------------------------------------------

def post_scenario(scenario):
    url = api_url + '/api/Save'
    data = json.dumps(scenario, cls=k.KJsonEncoder, indent=4)
    # print('post_scenario')
    # print(data)
    status, x = post.httpRequest(url, 'POST', data)
    if status >= 400:
        msg = 'post_scenario: "{}" {} {}'.format(scenario.name, status, x.decode())
        raise cc_common.CcException(status, msg)
    # Return value is the saved definition
    obj = json.loads(x)
    # print('\n*** Response from the POST /api/Save')
    # print(json.dumps(obj, cls=k.KJsonEncoder, indent=4))

    return(status)

# -----------------------------------------------------------------------------
# Start a scenario run
# -----------------------------------------------------------------------------

def start_scenario(start_wkf):
    #url = (api_url
     #          + f'/api/scenario-definitions/{start_wkf.workflowDefinitionId}'
      #         + f'/versions/{start_wkf.workflowDefinitionVersionNumber}'
       #        + '/start')
    url = ("http://localhost:7060"
           + f'/api/scenario-definitions/{start_wkf.workflowDefinitionId}'
           + f'/versions/{start_wkf.workflowDefinitionVersionNumber}'
           + '/start')
    #data = json.dumps(start_wkf, cls=k.KJsonEncoder, indent=4)
    r = requests.post(url, auth=common.auth,
                      json=json.dumps(start_wkf, cls=k.KJsonEncoder))
    #status, x = post.httpRequest(url, 'POST', data)
    return(r.status_code)


def start_scenario_azure(start_wkf):
    #url = (api_url
     #          + f'/api/scenario-definitions/{start_wkf.workflowDefinitionId}'
      #         + f'/versions/{start_wkf.workflowDefinitionVersionNumber}'
       #        + '/start')
    #url = ("http://dockerxcomp.francecentral.cloudapp.azure.com:18080/workflowsservice"
     #      + f'/api/scenario-definitions/{start_wkf.workflowDefinitionId}'
      #     + f'/versions/{start_wkf.workflowDefinitionVersionNumber}'
       #    + '/start')
    url = ("http://koordinatorsalon.francecentral.cloudapp.azure.com:8080/workflowsservice"
           + f'/api/scenario-definitions/{start_wkf.workflowDefinitionId}'
           + f'/versions/{start_wkf.workflowDefinitionVersionNumber}'
           + '/start')
    #data = json.dumps(start_wkf, cls=k.KJsonEncoder, indent=4)
    #status, x = post.httpRequest(url, 'POST', data)
    print("start_wkf", start_wkf)
    r = requests.post(url, auth=common.auth,
                      json=json.dumps(start_wkf, cls=k.KJsonEncoder))
    return(r.status_code)

# -----------------------------------------------------------------------------
# Stop a scenario run
# -----------------------------------------------------------------------------


def stop_scenario(id):
    url = api_url + '/api/Stop'

    # Stop has one query parameters
    query_params = dict(
        workflowInstanceId = id,
    )
    
    status, x = post.httpRequest(url, 'POST', None, fields=query_params)
    return(status)

# -----------------------------------------------------------------------------
# Validate WorkflowDefinition
# -----------------------------------------------------------------------------

def validate_scen_def(scen_def):
    """I could use the returned list..."""
    url = api_url + '/api/ValidateWorkflowDefinition'
    data = json.dumps(scen_def, cls=k.KJsonEncoder, indent=4)
    status, x = post.httpRequest(url, 'POST', data)
    if status != 200:
        msg = 'validate_scen_def: "{}"", status: {}'.format(scen_def.name, status)
        raise cc_common.CcException(status, msg)
    return(status)

# =============================================================================
# Top level functions
# =============================================================================

# -----------------------------------------------------------------------------
# Stop all scenario instances
# -----------------------------------------------------------------------------

def stop_scenario_all():
    """Stop all running scenario instances."""
    status, wkf_inst = cc_monitoring.get_scenario_instances()
    if status == 200:
        for wi in wkf_inst:
            print('Stopping "{}", started on "{}"'.format(wi.name, wi.startDate))
            stop_scenario(wi.id)
    

# -----------------------------------------------------------------------------
# Create one scenario definition, with one task utilization, and no I/O
# -----------------------------------------------------------------------------

def create_simple_scenario(task_data):
    """Create a task definition, use it in a scenario definition."""
    # FIXME I could push the task definition, instead of relying on Alpha
    # simple task, no inputs or outputs
    tk_def = k.CatalogTaskDefinition(**task_data)

    # Generate a TaskUtilization from the definition, wrap it in an array. This
    # is the equivalent of me creating a scenario in the designer, and picking
    # this task definition from the catalog.
    task_defs = [
        k.TaskUtilization.from_catalog_task(tk_def),
    ]

    # Create a scenario definition that uses the previous task
    sc = k.WorkflowDefinition(
        str(uuid.uuid4()),
        'Zero scenario (generated)',
        'CommandCenter',
        'BusinessAnalysts',
        0,
        tasks=task_defs,
        #versionNumber=1,
        versionDescription='This is the very first version',
        live=True,
        timeoutInMillis=2*tk_def.timeOutInMillis,
    )
    print('cc_scenario: WorkflowDefinition: id={}'.format(sc.id))

    # Return the newly-created scenario object
    return sc

# -----------------------------------------------------------------------------
# Push the scenario definition, start it, poll for a task, and return it
# -----------------------------------------------------------------------------

def push_scenario_start_poll(task_data):
    """Push a scenario definition, run it, poll, return the first task."""

    # POST a scenario definition
    sc = create_simple_scenario(task_data)
    status = post_scenario(sc)
    msg = 'cc_scenario: post_scenario: status={}'.format(status)
    print(msg)
    if status >= 400:
        raise RuntimeError(msg)

    # Start the scenario
    status = start_scenario(k.StartWorkflow(sc.id, 0))
    msg = 'cc_scenario: start_scenario: status={}'.format(status)
    print(msg)
    if status >= 400:
        raise RuntimeError(msg)

    # Give it some time to start and push out the first task
    time.sleep(1)  # in seconds

    # Get the running task
    worker_id = cc_common.get_worker_id('cc_scenario')
    for i in range(5):
        status, ti = cc_polling.poll(namespace, worker_id)
        if status == 204:
            print('Task queue is empty')
            time.sleep(1)
            continue
        elif status in [401, 403]:
            # We did not succeed, so the task has not been acquired. We can't
            # send task status events, we have no task, ti is None.
            msg = 'cc_scenario: poll: status={}'.format(msg)
            print(msg)
            raise RuntimeError(msg)
        break

    # We have a task instance, compare to the task definition we used
    return ti


# -----------------------------------------------------------------------------
# start workflow function
# -----------------------------------------------------------------------------


def start_workflow(workflow_name):
    #cc_common.set_token()
    common.set_auth()
    print(f'Getting the "{workflow_name}" scenario\'s id')
    url = "http://localhost:7060/api/scenario-definitions"
    get_scen_status, id, version, wkf_name = scen_get_id_version_using_levenshtein(workflow_name, url)
    if type(id) == list:
        return id, None, get_scen_status
    print(f'Starting the "{wkf_name}" scenario')
    start_status = start_scenario(k.StartWorkflow(id, version))
    print(start_status)
    return None, wkf_name, start_status


def start_workflow_in_azure(workflow_name):
    #cc_common.set_token_azure()
    common.set_auth_azure()
    print(f'Getting the "{workflow_name}" scenario\'s id')
    # url = 'http://dockerxcomp.francecentral.cloudapp.azure.com:18080/workflowsservice/api/scenario-definitions'
    url = 'http://koordinatorsalon.francecentral.cloudapp.azure.com:8080/workflowsservice/api/scenario-definitions'
    status, id, version, wkf_name = scen_get_id_version_using_levenshtein(workflow_name, url)
    if type(id) == list:
        return id, None, status
    print(f'Starting the "{wkf_name}" scenario')
    status = start_scenario_azure(k.StartWorkflow(id, version))
    print(status)
    return None, wkf_name, status


# -----------------------------------------------------------------------------
# query scenario progress function
# -----------------------------------------------------------------------------

def scenario_status(wkf_name):
    # common.set_auth()
    common.set_auth_azure()
    # monitoring_url_azure ="http://dockerxcomp.francecentral.cloudapp.azure.com:18080/monitoringservice/api/scenario-instances"
    monitoring_url_azure = "http://koordinatorsalon.francecentral.cloudapp.azure.com:8080/monitoringservice/api/scenario-instances"

    # workflow_definition_url_azure = 'http://dockerxcomp.francecentral.cloudapp.azure.com:18080/workflowsservice/api/scenario-definitions'
    workflow_definition_url_azure = 'http://koordinatorsalon.francecentral.cloudapp.azure.com:8080/workflowsservice/api/scenario-definitions'

    monitoring_url = "http://127.0.0.1:8079/api/scenario-instances"

    workflow_definition_url = 'http://localhost:7060/api/scenario-definitions'

    status, workflow_list_name, version, workflow_name = extract_correct_workflow_name(wkf_name, workflow_definition_url_azure)
    # status, workflow_list_name, version, workflow_name = extract_correct_workflow_name(wkf_name, workflow_definition_url)
    print(status, workflow_list_name, version, workflow_name)
    if type(workflow_list_name) == list:
        return workflow_list_name, None, None

    running_query_status, running_workflows = running_scenario(workflow_name, monitoring_url_azure)
    finished_query_status, finished_workflows = finished_workflow(workflow_name, monitoring_url_azure)

    # running_query_status, running_workflows = running_scenario(workflow_name, monitoring_url)
    # finished_query_status, finished_workflows = finished_workflow(workflow_name, monitoring_url)

    return workflow_name, running_workflows, finished_workflows


def running_scenario(workflow_name, url):
    running_query_params = dict(
        workspaceName='BusinessAnalysts',
        workflowInstanceName=workflow_name,
        workflowInstanceStatus='Running'
    )

    running_data = requests.get(url, auth=common.auth, params=running_query_params)
    status = running_data.status_code
    print("running status", status)
    print("running workflow name", workflow_name)
    if status <= 205:
        running_workflow = []
        data = running_data.json()
        # print("running data", data)
        if len(data) != 0:
            # max_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).astimezone()
            for d in range(0, len(data)):
                start_date = parser.parse(data[d]["startDate"])
                if start_date.date() == datetime.now().date():
                    running_workflow.append(data[d])

        return status, running_workflow
    return status, None


def finished_workflow(workflow_name, url):
    error_query_params = dict(
        workspaceName='BusinessAnalysts',
        workflowInstanceName=workflow_name,
        workflowInstanceStatus='Finished'
    )

    finished_data = requests.get(url, auth=common.auth, params=error_query_params)
    status = finished_data.status_code
    if status <= 205:
        finished_workflow = []
        data = finished_data.json()
        if len(data) != 0:
            # max_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0).astimezone()
            for d in range(0, len(data)):
                start_date = parser.parse(data[d]["startDate"])
                if start_date.date() == datetime.now().date():
                    finished_workflow.append(data[d])

        return status, finished_workflow
    return status, None


# -----------------------------------------------------------------------------
# check task notification function
# -----------------------------------------------------------------------------


def check_manual_task_notification():
    # common.set_auth()
    common.set_auth_azure()
    task_notification_url = "http://127.0.0.1:7000/api/namespaces/POPUP_USER/task-instances"
    # task_notification_url_azure = "http://dockerxcomp.francecentral.cloudapp.azure.com:18080/pollingservice/api/namespaces/POPUP_USER/task-instances"
    task_notification_url_azure = "http://koordinatorsalon.francecentral.cloudapp.azure.com:8080/pollingservice/api/namespaces/POPUP_USER/task-instances"

    query_params = dict(
        catalogTaskDefinitionNamespace='POPUP_USER',
        workspaces=['BusinessAnalysts']
    )

    # response = requests.get(task_notification_url, auth=common.auth, params=query_params)
    response = requests.get(task_notification_url_azure, auth=common.auth, params=query_params)
    status = response.status_code
    print("notification status: ", status)
    if status == 200:
        data = response.json()
        print("notifications: ", data)
        if data == []:
            return {}, []
        today_data =[]
        task_notifications = {}
        for notification in data:
            scenario_name = notification["inputData"]["scenarioInstanceName"]
            creation_date = parser.parse(notification["creationDate"])
            if creation_date.date() == datetime.now().date():
                today_data.append(notification)
                if scenario_name in task_notifications:
                    task_notifications[scenario_name].append(notification)
                else:
                    task_notifications[scenario_name] = [notification]
        return task_notifications, today_data
    return None, None


# -----------------------------------------------------------------------------
# Complete / Cancel tasks
# -----------------------------------------------------------------------------

manual_task_update_url = 'http://127.0.0.1:9999/api/task-statuses'
# manual_task_update_url_azure = 'http://dockerxcomp.francecentral.cloudapp.azure.com:18080/taskstatusservice/api/task-statuses'
manual_task_update_url_azure = 'http://koordinatorsalon.francecentral.cloudapp.azure.com:8080/taskstatusservice/api/task-statuses'


def complete_manual_task(task_instance_id):
    task_status = {
        "taskInstanceId": task_instance_id,
        "status": "Completed"
    }
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    # response = requests.post(manual_task_update_url, auth=common.auth, json=task_status, headers=headers)
    response = requests.post(manual_task_update_url_azure, auth=common.auth, json=task_status, headers=headers)
    print("task instance id", task_instance_id)
    status = response.status_code
    print("validate manual task: ", status)
    if status <= 205:
        return True
    return False


def error_manual_task(task_instance_id):
    task_status = {
        "taskInstanceId": task_instance_id,
        "status": "Error",
        "errorLevel": "Fatal"
    }
    headers = {'Content-type': 'application/json', 'Accept': 'application/json'}
    # response = requests.post(manual_task_update_url, auth=common.auth, json=task_status, headers=headers)
    response = requests.post(manual_task_update_url_azure, auth=common.auth, json=task_status, headers=headers)
    print("task instance id", task_instance_id)
    status = response.status_code
    print("validate manual task: ", status)
    if status <= 205:
        return True
    return False


#if __name__ == '__main__':
 #   # Check cmd line args
  #  if len(sys.argv) < 2:
   #     print('usage: {} <wkf name>'.format(sys.argv[0]))
    #    exit(-1)
    # FIXML: test file existence
    #wkf_name = sys.argv[1]

    #cc_common.set_token()
    #print(f'Getting the "{wkf_name}" scenario\'s id')
    #status, id, version = scen_get_id_version(wkf_name)
    #print(f'Starting the "{wkf_name}" scenario')
    #status = start_scenario(k.StartWorkflow(id, version))
    #print(status)

