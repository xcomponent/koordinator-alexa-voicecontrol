#!/usr/bin/env python
# post.py - using urllib3 for posting
#-------------------------------------------------------------------------------
# POST'ing data to the Koordinator REST API's has two steps :
#
#   - authentication: payload = (user, pswd), only content-type header. This
#     returns a token that must be passed to subsequent POST requests
#
#   - post: payload is the data, the header must include 'authorization' with
#     the token from the authenticate call
#
# Each caller of the post() function passes the data and the URL
#-------------------------------------------------------------------------------

# This could be a class, to store the token in the state

import json
import urllib3

# Validate certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
http = urllib3.PoolManager()

# Login/password for authentication
token = None

def httpRequest_raw(url, method, data, fields=None, content_type='application/json'):
    # print('url={}\nmethod={}\ndata={}'.format(url, method, data))
    # print('fields={}, content_type={}'.format(fields, content_type))
    # print()

    # Specify mime-types
    headers = {
        'Accept': 'application/json',
    }
    # The token was retrieved with a call to the authentication service
    headers['Authorization'] = '{}'.format(token)
    headers['Content-Type'] = '{}'.format(content_type)

    # Body may be present/absent depending on the operation
    body = None
    if data != None:
        # body=data.encode('utf-8') # breaks a lot of stuff
        body=data # accents don't get through 
    
    # send request
    if body is None:
        r = http.request(
            method,
            url,
            headers=headers,
            fields=fields,
        )
    else:
        r = http.request(
            method,
            url,
            headers=headers,
            fields=fields,
            body=body,
        )
        # return value is an HTTPResponse object, with three attributes: status,
    # data, and header
    if r is None:
        print('post.httpRequest: http.request returned None'.format(r))
        return None, None

    # Each REST API operation lists the possible return statuses, so I can't
    # decide here to handle some of them or no.
    return r.status, r.data

def httpRequest(url, method, data, fields=None, content_type='application/json'):
    status, data = httpRequest_raw(url, method, data, fields, content_type)
    if status is None:
        return None, None
    if status == 401:
        print('401: Not authenticated')
    elif status == 403:
        # This disrupts the unittest's output
        #print('403: Unauthorized')
        pass

    # Each REST API operation lists the possible return statuses, so I can't
    # decide here to handle some of them or no.
    return status, data
