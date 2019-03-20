#!/usr/bin/env python
# common.py - functions shared by all the modules
#
# This file corresponds to Command Center software version 3.5.0-174

"""This model lets us work at the python level. Inputs and outputs to and from
these functions are either simples types or python objects, but never json. The
modules translates to and from json as required, so the clients never have to
do it.  """

import os
import json
from alexaskill.scripts_koordinator.BearerAuth import HTTPBearerAuth
import requests
from alexaskill.scripts_koordinator import k

#-------------------------------------------------------------------------------
# Gloabl settings
#-------------------------------------------------------------------------------

# Koordinator server URL
#server_url = 'http://localhost:8080'  # local
server_url = 'http://localhost:9009'
#server_url = 'http://ccenter.xcomponent.com'  # remote

auth = None

#-------------------------------------------------------------------------------
# Authentication - user
#-------------------------------------------------------------------------------

endpoint_url = f'{server_url}/authenticationservice'
api_url = f'{server_url}/api/users/login'


def set_auth(username='admin', password='KoordinatorAdmin'):
    global auth
    body = json.dumps(k.CredentialsInfo(username, password), cls=k.KJsonEncoder)
    #r = requests.post(endpoint_url + '/api/Users/Login',
     #                data=body, headers={'Content-type': 'application/json'})

    r = requests.post(api_url, data=body, headers={'Content-type': 'application/json'})
    if r.status_code >= 400:
        raise RuntimeError(f'[{r.status_code}] {r.text}')

    ti = k.TokenInfo.from_json_decoded(json.loads(r.text))
    auth = HTTPBearerAuth(ti.value)


# server_url_azure = 'http://dockerxcomp.francecentral.cloudapp.azure.com:18080'
server_url_azure = 'http://koordinatorsalon.francecentral.cloudapp.azure.com:8080'
endpoint_url_azure = f'{server_url_azure}/authenticationservice'


#def set_auth_azure(username='admin', password='KoordinatorAdmin'):
def set_auth_azure(username='Marwa', password='Marwa'):
    global auth
    body = json.dumps(k.CredentialsInfo(username, password), cls=k.KJsonEncoder)
    r = requests.post(endpoint_url_azure + '/api/Users/Login',
                     data=body, headers={'Content-type': 'application/json'})
    print("status code", r.status_code)
    print("data", r.text)
    if r.status_code >= 400:
        raise RuntimeError(f'[{r.status_code}] {r.text}')

    ti = k.TokenInfo.from_json_decoded(json.loads(r.text))
    auth = HTTPBearerAuth(ti.value)

#-------------------------------------------------------------------------------
# get_worker_id - generate a pid-labelled worker id
#-------------------------------------------------------------------------------

def get_worker_id(prefix):
    """Return a unique worker id, including the current pid."""
    return '{}-worker-{}'.format(prefix, os.getpid())

#-------------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    set_auth()
    print(auth.token)
