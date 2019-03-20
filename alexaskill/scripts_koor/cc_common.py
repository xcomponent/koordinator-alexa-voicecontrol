#!/usr/bin/env python
# cc_common.py - functions shared by all the modules
#
# This file corresponds to Command Center software version 2.2.1-B71

"""The 'cc' model (for Command Center) lets us work at the python level. Inputs
and outputs to and from these functions are either simples types or python
objects, but never json. The cc module translates to and from json as required,
so the clients never have to do it.
"""

# I should bring the code from post.py in here

import os
import time
import json
from alexaskill.scripts_koor import post
from alexaskill.scripts_koor import k
import requests

#-------------------------------------------------------------------------------
# Build URL
#-------------------------------------------------------------------------------

server_url = 'http://localhost:9009'
#server_url = 'http://10.91.87.208:443'

#api_url = f'{server_url}/authenticationservice/api/Users/Login'
api_url = f'{server_url}/api/users/login'

#-------------------------------------------------------------------------------
# Authentication - user. To enable other calls, not to be tested for itself.
#-------------------------------------------------------------------------------

def set_token(username='admin', password='KoordinatorAdmin'):
    body_param = k.CredentialsInfo(username, password)
    
    data = json.dumps(body_param, cls=k.KJsonEncoder)
    status, x = post.httpRequest(api_url, 'POST', data)
    #user_pass_dict = {'user': username,
     #         'passwd': password,
      #        'api_type': 'json'}
    #sess = requests.Session()
    #sess.headers.update({'User-Agent' : 'I am testing Alexa:sentdex'})
    #resp = sess.post(api_url, data=user_pass_dict)
    #status = resp.status_code
    #print('status={}, data={}'.format(status, x))
    print(status)
    if status < 205:
        ti = k.TokenInfo.from_json_decoded(json.loads(x))
        post.token = ti.value
        return ti.value
    else:
        msg = ('Couldn\'t get a user token for user="{}", password="{}"'
                   .format(username, password))
        raise RuntimeError(msg)
    return ti.value


api_url_azure = 'http://dockerxcomp.westeurope.cloudapp.azure.com:18080/authenticationservice/api/Users/Login'
def set_token_azure(username='admin', password='KoordinatorAdmin'):
    body_param = k.CredentialsInfo(username, password)

    data = json.dumps(body_param, cls=k.KJsonEncoder)
    status, x = post.httpRequest(api_url_azure, 'POST', data)
    # user_pass_dict = {'user': username,
    #         'passwd': password,
    #        'api_type': 'json'}
    # sess = requests.Session()
    # sess.headers.update({'User-Agent' : 'I am testing Alexa:sentdex'})
    # resp = sess.post(api_url, data=user_pass_dict)
    # status = resp.status_code
    # print('status={}, data={}'.format(status, x))
    print(status)
    if status < 205:
        ti = k.TokenInfo.from_json_decoded(json.loads(x))
        post.token = ti.value
        return ti.value
    else:
        msg = ('Couldn\'t get a user token for user="{}", password="{}"'
               .format(username, password))
        raise RuntimeError(msg)
    return ti.value

#-------------------------------------------------------------------------------
# get_worker_id - generate a pid-labelled worker id
#-------------------------------------------------------------------------------

def get_worker_id(prefix):
    """Return a unique worker id, including the current pid."""
    return '{}-worker-{}'.format(prefix, os.getpid())

#-------------------------------------------------------------------------------
# CcException - I want to check the HTTP return code on RunTimeError
#-------------------------------------------------------------------------------

class CcException(Exception):
    def __init__(self, status, *args, **kwargs):
        self.status = status
        Exception.__init__(self, *args, **kwargs)

# -----------------------------------------------------------------------------
# Test one of the endpoints
# -----------------------------------------------------------------------------

def get_service_status():
    """Get a named workspace."""
    url = 'http://localhost:443/monitoringservice/api/ServiceStatus'
    status, data = post.httpRequest(url, 'GET', None)
    # status may be zero if there is non response
    if status != 204:
        msg = 'get_service_status: status: {}'.format(status)
        raise CcException(status, msg)
    return status

#-------------------------------------------------------------------------------
# main
#-------------------------------------------------------------------------------

if __name__ == '__main__':
    print(set_token())
