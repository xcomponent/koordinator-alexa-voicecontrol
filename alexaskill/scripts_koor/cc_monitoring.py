#!/usr/bin/env python
# cc_monitoring.py - call the API functions exposed by Command Center

"""The 'cc' model (for Command Center) lets us work at the python level. Inputs
and outputs to and from these functions are either simples types or python
objects, but never json. The cc module translates to and from json as required,
so the clients never have to do it.
"""

import sys
import time
import json
import uuid
from alexaskill.scripts_koor import cc_common
from alexaskill.scripts_koor import cc_polling
from alexaskill.scripts_koor import post
from alexaskill.scripts_koor import k

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

api_url = f'http://{cc_common.server_url}/monitoringservice'

# =============================================================================
# Low level functions
# =============================================================================

# -----------------------------------------------------------------------------
# Get all the scenario instances
# -----------------------------------------------------------------------------

def get_scenario_instances():
    url = api_url + '/api/WorkflowInstances'
    status, data = post.httpRequest(url, 'GET', None)
    if status == 200:
        # Return value is an array of WorkflowInstances.
        obj = json.loads(data)
        wkf_inst = [k.WorkflowInstance.from_json_decoded(o) for o in obj]
        return status, wkf_inst
    return status, data

# -----------------------------------------------------------------------------
# Get scenario's last version
# -----------------------------------------------------------------------------

def scen_get_id_version(name):
    url = api_url + '/api/Search'

    # Cancelled has two query parameters
    query_params = dict(
        workspaceName = 'DefaultWorkspace',
    )
    
    status, data = post.httpRequest(url, 'GET', None, fields=query_params)
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
    url = api_url + '/api/Start'
    data = json.dumps(start_wkf, cls=k.KJsonEncoder, indent=4)
    status, x = post.httpRequest(url, 'POST', data)
    return(status)

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

# -----------------------------------------------------------------------------
# main
# -----------------------------------------------------------------------------

if __name__ == '__main__':
    pass
