#!/usr/bin/env python
# cc_polling.py - call the Pollng service API's
#
# This file corresponds to Command Center software version 2.2.1-B71

"""The 'cc' model (for Command Center) lets us work at the python level. Inputs
and outputs to and from these functions are either simples types or python
objects, but never json. The cc module translates to and from json as required,
so the clients never have to do it.
"""

import time
import json
from alexaskill.scripts_koor import cc_common
from alexaskill.scripts_koor import post
from alexaskill.scripts_koor import k

#-------------------------------------------------------------------------------
# Build URL
#-------------------------------------------------------------------------------

api_url = f'{cc_common.server_url}/pollingservice'

#-------------------------------------------------------------------------------
# Cancelled taskInstanceId
#-------------------------------------------------------------------------------

def cancelled(namespace, task_instance_id):
    """Create a 'cancelled' request and send it to the 'polling' endpoint.
"""
    url = api_url + '/api/Cancelled'

    # Cancelled has two query parameters
    query_params = dict(
        catalogTaskDefinitionNamespace=namespace,
        taskInstanceId = 'x',
    )

    status, data = post.httpRequest(url, 'GET', None, fields=query_params)
    if status != 200:
        msg = ('cancelled: taskInstanceId: "{}", status: {}'
                   .format(task_instance_id, status))
        raise cc_common.CcException(status, msg)
    
    # Return value is an array of TaskInstance
    obj = json.loads(data)
    return status, k.CancellationStatus(**obj)

#-------------------------------------------------------------------------------
# Peek in the task queue
#-------------------------------------------------------------------------------

def peek(namespace):
    """Create a peek request and send it to the 'polling' endpoint.
"""
    url = api_url + '/api/Peek'

    # Peek has two query parameters
    query_params = dict(
        catalogTaskDefinitionNamespace=namespace,
        workspaces = 'DefaultWorkspace',
    )

    status, data = post.httpRequest(url, 'GET', None, fields=query_params)
    if status != 200:
        msg = 'peek: status: {}'.format(status)
        raise cc_common.CcException(status, msg)
    
    # Return value is an array of TaskInstance
    obj = json.loads(data)
    return status, [k.TaskInstance(**o) for o in obj]

#-------------------------------------------------------------------------------
# Poll the task queue, pop out if anything found
#-------------------------------------------------------------------------------

def poll(namespace, worker_id):
    """Create a 'poll' request and send it to the 'polling' endpoint.
"""
    url = api_url + '/api/Poll'

    # Poll has three query parameters
    query_params = dict(
        catalogTaskDefinitionNamespace=namespace,
        workerId=worker_id,
        workspaces='DefaultWorkspace',
    )

    # data is a string, the json representation of our data
    status, data = post.httpRequest(url, 'GET', '{}', fields=query_params)
    if status >= 400:
        msg = 'poll: status: {}'.format(status)
        raise cc_common.CcException(status, msg)
    if status == 204:
        return status, None

    # Assuming that status = 200. Return value is a TaskInstance
    obj = json.loads(data)
    return status, k.TaskInstance(**obj)

#===============================================================================
# User functions - may call upon the previous ones
#===============================================================================

#-------------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    
    # Authentify yourself
    cc_common.set_token()
    print('Received token {}'.format(post.token))

    # # Peek in the task queue
    # peek()

    # Peek in the task queue
    poll('Alpha', 'joao')
