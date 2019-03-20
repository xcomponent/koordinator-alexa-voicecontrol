#!/usr/bin/env python
# scenario.py - call the API functions exposed by Command Center
#
# This file corresponds to Command Center software version 3.5.0-174

"""This model lets us work at the python level. Inputs and outputs to and from
these functions are either simples types or python objects, but never json. The
modules translates to and from json as required, so the clients never have to
do it.  """

import sys
import json
import requests
from alexaskill.scripts_koordinator import common
from alexaskill.scripts_koordinator import k

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

endpoint_url = f'{common.server_url}/workflowsservice'

# -----------------------------------------------------------------------------
# Get all the scenario definitions
# -----------------------------------------------------------------------------

def get_scenarios():
    query_params = dict(
        workspaceName='DefaultWorkspace',
    )
    # Default is to return the last version only
    r = requests.get(endpoint_url + '/api/scenario-definitions',
                     auth=common.auth,
                         params=query_params)
    if r.status_code >= 400:
        raise RuntimeError(f'[{r.status_code}] {r.text}')

    # Return value is an array of WorkflowDefinitions.
    obj = json.loads(r.text)
    wkf_defs = [k.WorkflowDefinition.from_json_decoded(o) for o in obj]
    
    for w in wkf_defs:
        print(f'name="{w.name}", id="{w.id}", version={w.versionNumber}')

# -----------------------------------------------------------------------------
# Get scenario's last version
# -----------------------------------------------------------------------------

def scen_get_id_version(name):
    # The GET operation has query parameters
    query_params = dict(
        workspaceName='DefaultWorkspace',
    )
    # Default is to return the last version only
    r = requests.get(endpoint_url + '/api/scenario-definitions',
                     auth=common.auth, params=query_params)
    if r.status_code >= 400:
        raise RuntimeError(f'[{r.status_code}] {r.text}')

    # Return value is an array of WorkflowDefinitions.
    obj = json.loads(r.text)
    wkf_defs = [k.WorkflowDefinition.from_json_decoded(o) for o in obj]

    # Look for the scenario with the right name
    for w in wkf_defs:
        if w.name == name:
            return w.id, w.versionNumber
    raise ValueError(f'Scenario "{name}" does not exist.')

# -----------------------------------------------------------------------------
# Start a scenario run
# -----------------------------------------------------------------------------

def start_scenario(start_wkf):
    url = (endpoint_url
               + f'/api/scenario-definitions/{start_wkf.workflowDefinitionId}'
               + f'/versions/{start_wkf.workflowDefinitionVersionNumber}'
               + '/start')
    r = requests.post(url, auth=common.auth,
                      json=json.dumps(start_wkf, cls=k.KJsonEncoder))
    if r.status_code >= 400:
        raise RuntimeError(f'[{r.status_code}] {r.text}')

# -----------------------------------------------------------------------------
# main
# -----------------------------------------------------------------------------

if __name__ == '__main__':
    # Check cmd line args
    if len(sys.argv) < 2:
        print('usage: {} <scenario_name>'.format(sys.argv[0]))
        exit(-1)
    # FIXML: test file existence
    name = sys.argv[1]

    common.set_auth()
    get_scenarios()

    id, version = scen_get_id_version(name)
    print()
    print(f'Found "{name}": id={id}, version={version}')

    print(f'Starting the "{name}" scenario')
    start_scenario(k.StartWorkflow(id, version))

