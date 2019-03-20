#!/usr/bin/env python
# k.py - implement Koordinator objects (workflow, tasks, catalog)

"""This module defines python classes that implement types defined in Command
Center's (a.k.a.Koordinator's) swagger files. It could probably be entirely
generated from the swagger file (which I believe is what Swagger Codegen does)
"""

# Standard imports
import sys
import json
import uuid
from enum import Enum
from alexaskill.scripts_koor import enums
from alexaskill.scripts_koor import k

#-------------------------------------------------------------------------------
# FIXME: One-Line Constructors: avoid a lot of boilerplate assignments when
# initializing a class.
#
# class A(object):
#     def __init__(self, a, b, c, d, e, f):
#         self.__dict__.update({k: v for k, v in locals().items() if k != 'self'})
#-------------------------------------------------------------------------------

# I want to recognize if a property was not set. Is it the same as testing the
# default value ?

# If a keyword arg comes right after a positional arg, is the name mandatory ?

# invariants: strings or integers ? arrays or dictionaries ?
# inputs/outputs: json-serializable or not ? It depends.
# Required: check each object

#-------------------------------------------------------------------------------
# KJson: specialize the JSON encoders/decoders
#-------------------------------------------------------------------------------

# encode: from K object to JSON: json.dump
# decode: from JSON to K object: json.load

# JSON serializes a number of basic objects, array, dict's, etc, but it won't
# serialize just any random object such as the CatalogTaskDefinition. What it
# can serialize is an array of dict's. So Koordinator objects require
# specialized JSON encoders and decoders.

class KJsonEncoder(json.JSONEncoder):
    """Return a json-encodable representation of the Koordinator objects.

    This is an new object, built entirely out of dictionaries and lists
    of elementary types. Usage: json.dumps(k_obj, cls=KJsonEncoder). The
    'dumps' function will call this 'default' method, which in turn
    calls an appropriate 'to_json_encodable' function.
"""
    def default(self, k_obj):
        if (isinstance(k_obj, TaskStatusEvent) or
                isinstance(k_obj, CatalogParameterType) or
                isinstance(k_obj, CatalogTaskDefinition) or
                isinstance(k_obj, TaskInstance) or
                isinstance(k_obj, CredentialsInfo) or
                isinstance(k_obj, CatalogUpdate) or
                isinstance(k_obj, WorkflowDefinition) or
                isinstance(k_obj, TaskUtilization) or
                isinstance(k_obj, WorkflowInstance) or
                isinstance(k_obj, UserCreateRequest) or
                isinstance(k_obj, UserUpdateRequest) or
                isinstance(k_obj, User) or
                isinstance(k_obj, StartWorkflow) or
                isinstance(k_obj, Workspace) or
                isinstance(k_obj, WorkspaceCreateRequest) or
                isinstance(k_obj, Right) or
                isinstance(k_obj, ProfileCreateRequest) or
                isinstance(k_obj, ProfileUpdateRequest) or
                isinstance(k_obj, Profile)
            ):
            return k_obj.to_json_encodable()
        else:
            return super(KJsonEncoder, self).default(self, k_obj)

#-------------------------------------------------------------------------------
# TaskStatusEvent: task notifications
#-------------------------------------------------------------------------------

class TaskStatusEvent:
    """Notifications from a running task.

    Required: taskInstanceId, status.
    This class doesn't require an id, because we create and send the
    TaskStatusEvent, but we don't receive it. It does not have a
    lifecycle that spans more than one request.
""" 
    def __init__(self, taskInstanceId, status, errorLevel='None',
                 progressPercentage=None, message='', invariants=None,
                     outputValues=None):
        self.taskInstanceId = taskInstanceId
        self.status = status  # enum now
        self.errorLevel = errorLevel  # enum now
        self.progressPercentage = progressPercentage
        self.message = message

        # invariants is a dictionary of integer-valued properties
        self.invariants = {}
        if invariants is not None:
            self.invariants = invariants

        # outputValues is dictionary of string-valued properties
        self.outputValues = {}
        if outputValues is not None:
            self.outputValues = outputValues

    def __str__(self):
        s = 'TaskStatusEvent\n'
        s += '  taskInstanceId: {}\n'.format(self.taskInstanceId)
        s += '  status: {}\n'.format(self.status)  # auto-converted to str
        s += '  errorLevel: {}\n'.format(self.errorLevel)
        s += '  progressPercentage: "{}"\n'.format(self.progressPercentage)
        s += '  message: "{}"\n'.format(self.message)
        if self.invariants != {}:
            s += '  invariants: { '
            s += ', '.join(['{}: {}'.format(k, v)
                            for k, v in self.invariants.items()])
            s += ' }\n'
        if self.outputValues != {}:
            s += '  outputValues: { '
            s += ', '.join(['{}: {}'.format(k, v)
                            for k, v in self.outputValues.items()])
            s += ' }\n'
        return s
         
    def to_json_encodable(self):
        """Create a json-encodable object representing a TaskStatusEvent.

        The returned object will be fed to the json encoder, to be
        json.dump'ed.  We use the object's __dict__ to ensure that optional
        members that did not receive a value are not included.
"""
        # Start building the resulting object with just the simple types
        d = {}
        # self.__dict__ is the dictionary of attributes of object 'self'
        for k, v in self.__dict__.items():
            # FIXME isn't 'val' the same thing as 'v' ???
            val = getattr(self, k)
            if val is None or val == '' or val == [] or val == {}:
                continue
            elif isinstance(val, Enum):
                d[k] = str(val)
            else:
                # k has a value. Assuming it's a simple value (i.e. it is
                # itself json-encodable), then we are ok. If val is an array or
                # a dictionary, we need to check their elements.
                d[k] = val
        return d

    # No need to decode, this object is only sent, never received. FIXME: is
    # this still true with Monitoring ?

#-------------------------------------------------------------------------------
# CatalogParameterType: an input or output parameter to a Koordinator task
#-------------------------------------------------------------------------------

class CatalogParameterType:
    """Input or output parameter to/from a CatalogTaskDefinition.
    
    Required: name
"""
    # FIXME: optional booleans (like allow_multiple_values), should I set None
    # as the default value ?
    def __init__(self, name, baseType='', allowMultipleValues=False,
                 defaultValue=None, description='', shortDescription='',
                     customRegex='', graphicalControl='', allowedValues=None):

        self.name = name
        self.baseType = baseType
        self.allowMultipleValues = allowMultipleValues
        self.defaultValue = defaultValue
        self.description = description
        self.shortDescription = shortDescription
        self.customRegex = customRegex
        self.graphicalControl = graphicalControl

        # allowedValues is an array of strings
        self.allowedValues = []
        if allowedValues is not None:
            self.allowedValues = allowedValues

    def to_json_encodable(self):
        """Create a json-encodable object representing a CatalogParameterType.

        The returned object will be fed to the json encoder, to be
        json.dump'ed.  We use the object's __dict__ to ensure that optional
        members that did not receive a value are not included.
"""
        # Start building the resulting object with just the simple types
        d = {}
        for k, v in self.__dict__.items():
            val = getattr(self, k)
            # FIXME is this test correct ?
            if val is None or val == '' or val == [] or val == {}:
                continue
            else:
                d[k] = val
        return d

    @classmethod
    def from_json_decoded(cls, obj):
        """Return a CatalogParameterType object from a json-decoded object."""

        # No special de-serialization is needed 
        return cls(**obj)

    def __str__(self):
        s = 'CatalogParameterType:\n'
        s += '  name: {}\n'.format(self.name)
        if self.baseType:
            # FIXME is this test correct ? what's the difference between en empty
            # string and the absence of the property ?
            s += '  baseType: {}'.format(self.baseType)
        return s

#-------------------------------------------------------------------------------
# CatalogTaskDefinition: a Koordinator individual task definition
#-------------------------------------------------------------------------------

# Classes like this one have been designed from the description of their json
# encoding. So they have a few quirks directly related to this 'history'. Maybe
# I should leave them as they are and design another class, independent of any
# kind of encoding ? How would I design a task definition class, if I had no
# json to deal with ? If client and server exchanged python objects ?

class CatalogTaskDefinition:
    """Initialize a task definition.
    
    Required: schemaVersion (FIXME)
"""
    # FIXME suivant les moments, je veux l'id ou non. Suivant que je le crée,
    # que je le reçois dans le Task Catalog, ou dans TaskInstance, c'est pas
    # pareil.
    def __init__(self, name, schemaVersion, namespace=None, displayName='',
                 description='', shortDescription='', timeOutInMillis=0,
                 versionNumber=None, inputs=None, outputs=None,
                     invariants=None, **kwargs):
        self.name = name
        self.schemaVersion = schemaVersion
        self.namespace = namespace
        self.displayName = displayName
        self.description = description
        self.shortDescription = shortDescription
        self.timeOutInMillis = timeOutInMillis
        self.versionNumber = versionNumber

        # inputs is an array of CatalogParameterType objects
        self.inputs = []
        if inputs is not None:
            self.inputs = inputs

        # outputs is an array of CatalogParameterType objects
        self.outputs = []
        if outputs is not None:
            self.outputs = outputs

        # invariants is an array of strings
        self.invariants = []
        if invariants is not None:
            self.invariants = invariants

    def __str__(self):
        s = 'CatalogTaskDefinition:\n'
        s += json.dumps(self, cls=k.KJsonEncoder, indent=4)
        return s
    
    def to_json_encodable(self):
        """Return a json-serializable object representing a CatalogTaskDefinition.
        The returned object will be fed to the json encoder.
"""
        # Start building the resulting object with just the simple types
        d = {}
        for k, v in self.__dict__.items():
            if k in ['inputs', 'outputs']:
                # These attributes have non-json-serializable values
                continue
            val = getattr(self, k)
            if val is None or val == '' or val == [] or val == {}:
                continue
            else:
                d[k] = val

        # Json-encode the python objects inside collections, and add them if
        # they're not empty.
        if self.inputs:
            d['inputs'] = [p.to_json_encodable() for p in self.inputs]
        if self.outputs:
            d['outputs'] = [p.to_json_encodable() for p in self.outputs]

        return d

    @classmethod
    def from_json_decoded(cls, obj):
        """Return a CatalogTaskDefinition object from a json-decoded object.
"""
        d = {}
        # Members can be optional. We iterate on the members actually present
        # in the incoming json, ignoring absent ones.
        for k, v in obj.items():
            if k in ['inputs', 'outputs']:
                continue
            d[k] = v

        # Properties with non-json-serializable values
        if 'inputs' in obj:
            d['inputs'] = [CatalogParameterType.from_json_decoded(i)
                               for i in obj['inputs']]
        if 'outputs' in obj:
            d['outputs'] = [CatalogParameterType.from_json_decoded(i)
                                for i in obj['outputs']]

        return cls(**d)

    def to_csv(self, f):
        # FIXME: properties don't always exist
        f.write('{};{};{};{};{};{};{};{};{}\n'.format(
            self.namespace, self.name, self.versionNumber, self.userName,
            self.schemaVersion, self.id, len(self.inputs), len(self.outputs),
            len(self.invariants)))

#-------------------------------------------------------------------------------
# TaskInstance: a running instance of a task
#-------------------------------------------------------------------------------

class TaskInstance:
    """A TaskInstance is received from the peek or poll api calls.

    Required: <nothing>
    
    Worker programs instantiate TaskInstance's from the return value of
    the Poll request. They never create them form scratch.
"""
    # Initialize a task instance
    def __init__(self, id='', workflowInstanceId='',
                 workflowDefinitionWorkspaceName='',
                 catalogTaskDefinitionNamespace='',
                 catalogTaskDefinitionName='',
                 catalogTaskDefinitionVersion='', taskDefinitionId='',
                 workerId='', timeOutInMillis=None, status='', errorLevel='',
                 creationDate='', workflowInstanceResumeCount=None,
                 userName='', invariants=None, inputData=None, outputData=None,
                     **kwargs):
        self.id = id
        self.workflowInstanceId = workflowInstanceId
        self.workflowDefinitionWorkspaceName = workflowDefinitionWorkspaceName
        self.catalogTaskDefinitionNamespace = catalogTaskDefinitionNamespace
        self.catalogTaskDefinitionName = catalogTaskDefinitionName
        self.catalogTaskDefinitionVersion = catalogTaskDefinitionVersion

        # The TaskDefinition in the Workflow endpoint (which I want to rename
        # TaskUtilization) has no Id property. So the Id below can only be for
        # catalog's TaskDefinition object.
        self.taskDefinitionId = taskDefinitionId

        self.timeOutInMillis = timeOutInMillis
        self.workerId = workerId
        self.status = status
        self.errorLevel = errorLevel
        self.creationDate = creationDate
        self.workflowInstanceResumeCount = workflowInstanceResumeCount
        self.userName = userName

        # invariants is a dictionary of integer-valued properties
        self.invariants = {}
        if invariants is not None:
            self.invariants = invariants

        # FIXME what goes inside inputData and outputData ?
        # inputData is a dictionary of string-valued properties
        self.inputData = {}
        if inputData is not None:
            self.inputData = inputData

        # outputData is dictionary of string-valued properties
        self.outputData = {}
        if outputData is not None:
            self.outputData = outputData

        # Below: this is actually part of the worker implementation, it
        # shouldn't be here at all.

    def __str__(self):
        return json.dumps(self, cls=KJsonEncoder, indent=4)

    #---------------------------------------------------------------------------

    # FIXME: what this means is that the TaskInstance object is
    # json-serializable. So why don't I get rid of the to_json_encodable()
    # method ? Because I don't want to include properties that were not
    # assigned values.
    
    def to_json_encodable(self):
        """Return a json-encodable object representing a TaskInstance.
        The returned object will be fed to the json encoder.
"""
        # Start building the resulting object with just the simple types
        d = {}
        for k, v in self.__dict__.items():
            val = getattr(self, k)
            if val is None or val == '' or val == [] or val == {}:
                continue
            else:
                d[k] = val
        return d

#-------------------------------------------------------------------------------
# CredentialsInfo: user and password
#-------------------------------------------------------------------------------

class CredentialsInfo:
    def __init__(self, username, password):
        self.username = username
        self.password = password
 
    def to_json_encodable(self):
        """Create a json-encodable object representing a CatalogParameterType.

        The returned object will be fed to the json encoder, to be
        json.dump'ed.  We use the object's __dict__ to ensure that optional
        members that did not receive a value are not included.
"""
        # Start building the resulting object with just the simple types
        d = {}
        for k, v in self.__dict__.items():
            val = getattr(self, k)
            # FIXME is this test correct ?
            if val is None or val == '' or val == [] or val == {}:
                continue
            else:
                d[k] = val
        return d
   
#-------------------------------------------------------------------------------
# TokenInfo: return by the authentication request
#-------------------------------------------------------------------------------

class TokenInfo:
    def __init__(self, value):
        self.value = value

    @classmethod
    def from_json_decoded(cls, obj):
        """Return a TokenInfo object from a json-decoded object.
"""
        return cls(**obj)
    
    def __str__(self):
        return 'TokenInfo:\n  value: "{}"'.format(self.value)

#-------------------------------------------------------------------------------
# CatalogUpdate: a Koordinator task catalog
#-------------------------------------------------------------------------------

class CatalogUpdate:

    def __init__(self, catalogTaskDefinitions, namespace='',
                 removePreviousTasks=False):
        """Primary constructor.
        Required: catalogTaskDefinitions
"""
        self.catalogTaskDefinitions = catalogTaskDefinitions
        self.namespace = namespace
        self.removePreviousTasks = removePreviousTasks

    #---------------------------------------------------------------------------

    def to_json_encodable(self):
        """Return a json-serializable object representing a CatalogUpdate.
        The returned object will be fed to the json encoder.
"""
        # Start building the resulting object with just the simple types
        d = {}
        for k, v in self.__dict__.items():
            if k == 'catalogTaskDefinitions':
                # These attributes have non-json-serializable values
                continue
            val = getattr(self, k)
            if val is None or val == '' or val == [] or val == {}:
                continue
            else:
                d[k] = val

        # Json-encode the python objects inside collections
        d['catalogTaskDefinitions'] = [t.to_json_encodable()
                                    for t in self.catalogTaskDefinitions]
        return d

    #---------------------------------------------------------------------------
    
    @classmethod
    def from_json_decoded(cls, obj):
        """Return a CatalogTaskDefinition object from a json-decoded object.
"""
        d = {}
        # We iterate on the members actually present, ignoring absent ones.
        for k, v in obj.items():
            if k in ['taskDefinitions']:
                continue
            d[k] = v

        # Properties with non-json-serializable values
        d['taskDefinitions'] = [CatalogTaskDefinition.from_json_decoded(t)
                               for t in obj['taskDefinitions']]
        return cls(**d)

    def __str__(self):
        """Return a json representation of the CatalogUpdate"""
        return json.dumps(self, cls=k.KJsonEncoder, indent=4)
        
    def to_csv(self, filepath):
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write('namespace;name;versionNumber;userName;schemaVersion;id'
                    + ';nbrInputs;nbrOutputs;nbrInvariants\n')
            for t in self.tasks:
                t.to_csv(f)
    
#-------------------------------------------------------------------------------
# WorkflowDefinition: defining a scenario in Koordinator 
#-------------------------------------------------------------------------------

class WorkflowDefinition:
    """Initialize a ScenarioDefinion object.

    Required: id, name, type, workspaceName, schemaVersion
"""
    def __init__(self, id, name, type, schemaVersion, workspaceName,
                 tasks=None, versionNumber=0, versionDescription='', live=False,
                 timeoutInMillis=0, description=None, inputData=None, **kwargs):
        self.id = id
        self.name = name
        self.type = type
        self.schemaVersion = schemaVersion
        self.workspaceName = workspaceName
        self.versionNumber = versionNumber
        self.versionDescription = versionDescription
        self.live = live
        self.timeoutInMillis = timeoutInMillis
        self.timeoutInMillis = timeoutInMillis
        self.description = description

        # tasks is an array of TaskUtilization
        self.tasks = []
        if tasks is not None:
            self.tasks = tasks

        # inputData is a dictionary of object properties
        self.inputData = {}
        if inputData is not None:
            self.inputData = inputData

    def __str__(self):
        return json.dumps(self, cls=k.KJsonEncoder, indent=4)

    def print_out(self):
        s = 'WorkflowDefinition:\n'
        s += '  name: {}\n'.format(self.name)
        s += '  nbr_inputs: {}\n  nbr_tasks: {}'.format(
            len(self.inputData), len(self.tasks))
        return s

    #---------------------------------------------------------------------------

    def to_json_encodable(self):
        """Return a json-serializable object representing a WorkflowDefinition.

        The returned object will be fed to the json encoder. We take
        great care to remove class members that have not been
        initialized, to avoid cluttering the json with useless default
        values.
"""
        # Start building the resulting object with just the simple types
        d = {}
        for k, v in self.__dict__.items():
            if k == 'tasks':
                # These attributes have non-json-serializable values.
                continue
            val = getattr(self, k)
            if val is None or val == '' or val == [] or val == {}:
                continue
            else:
                d[k] = val

        # Json-encode the python objects inside collections, and add them if
        # they're not empty.
        d['tasks'] = [t.to_json_encodable() for t in self.tasks]

        return d

    #---------------------------------------------------------------------------

    @classmethod
    def from_json_decoded(cls, obj):
        """Return a WorkflowDefinition object from a json-decoded object.
"""
        d = {}
        # We iterate on the members actually present, ignoring absent ones.
        for k, v in obj.items():
            if k == 'tasks':
                continue
            d[k] = v
        
        # Properties with non-json-serializable values
        d['tasks'] = [TaskUtilization.from_json_decoded(i) for i in obj['tasks']]
        
        return cls(**d)
    
#-------------------------------------------------------------------------------
# TaskUtilization: using (referencing) a task definition from the task catalog
#-------------------------------------------------------------------------------

class TaskUtilization:
    """Initialize a TaskUtilization object.

    Required: type

    This type does not have an Id. In swagger it is still named
    TaskDefinition, here we call it TaskUtilization to avoid confusing
    it.
"""
    def __init__(self, type, catalogTaskDefinitionNamespace='',
                 catalogTaskDefinitionName='', catalogTaskDefinitionVersion=0,
                     description='', longDescription='', timeOutInMillis=0,
                     maxRetriesOnError=None, inputData=None, subTasks=None,
                     joinIdList=None, dependsOn=None, **kwargs):

        self.type = type
        self.catalogTaskDefinitionNamespace = catalogTaskDefinitionNamespace
        self.catalogTaskDefinitionName = catalogTaskDefinitionName
        self.catalogTaskDefinitionVersion = catalogTaskDefinitionVersion
        self.description = description
        self.longDescription = longDescription
        self.maxRetriesOnError = maxRetriesOnError
        self.timeOutInMillis = timeOutInMillis

        # inputData is a dictionary of object properties
        # FIXME how is this handled by the json de-serializer ?
        self.inputData = {}
        if inputData is not None:
            self.inputData = inputData
        
        # subTasks is an array of TaskUtilization
        self.subTasks = []
        if subTasks is not None:
            self.subTasks = subTasks
        
        # joinIdList is an array of strings
        self.joinIdList = []
        if joinIdList is not None:
            self.joinIdList = joinIdList
        
        # dependsOn is an array of strings
        self.dependsOn = []
        if dependsOn is not None:
            self.dependsOn = dependsOn

    def __str__(self):
        return json.dumps(self, cls=k.KJsonEncoder, indent=4)

    #---------------------------------------------------------------------------

    def to_json_encodable(self):
        """Return a json-serializable object representing a TaskUtilization.

        The returned object will be fed to the json encoder. We take
        great care to remove class members that have not been
        initialized, to avoid cluttering the json with useless default
        values.
"""
        # Start building the resulting object with just the simple types
        d = {}
        for k, v in self.__dict__.items():
            if k == 'subTasks':
                # These attributes have non-json-serializable values
                continue
            val = getattr(self, k)
            if val is None or val == '' or val == [] or val == {}:
                continue
            else:
                d[k] = val

        # Json-encode the python objects inside collections, and add them if
        # they're not empty. 
        if self.subTasks:
            d['subTasks'] = [t.to_json_encodable() for t in self.subTasks]

        return d

    #---------------------------------------------------------------------------
    
    @classmethod
    def from_json_decoded(cls, obj):
        """Return a TaskUtilization object from a json-decoded object.
"""
        d = {}
        # We iterate on the members actually present, ignoring absent ones.
        for k, v in obj.items():
            if k == 'subTasks':
                continue
            d[k] = v

        # Properties with non-json-serializable values
        if 'subTasks' in obj:
            d['subTasks'] = [TaskUtilization.from_json_decoded(t)
                                 for t in obj['subTasks']]

        return cls(**d)

    #--------------------------------------------------------------------------

    # "easier to ask for forgiveness than permission" (EAFP)

    @classmethod
    def from_catalog_task(cls, tk_def, inputData=None):
        """Return a TaskUtilization object from a CatalogTaskDefinition"""
        d= {}
        d['type'] = 'Worker'
        if hasattr(tk_def, 'namespace'):
            d['catalogTaskDefinitionNamespace'] = tk_def.namespace
        if hasattr(tk_def, 'name'):
            d['catalogTaskDefinitionName'] = tk_def.name
        if hasattr(tk_def, 'versionNumber'):
            d['catalogTaskDefinitionVersion'] = tk_def.versionNumber
        if hasattr(tk_def, 'shortDescription'):
            d['description'] = tk_def.shortDescription
        if hasattr(tk_def, 'description'):
            d['longDescription'] = tk_def.description
        if hasattr(tk_def, 'timeOutInMillis'):
            d['timeOutInMillis'] = tk_def.timeOutInMillis

        # A dictionary of strings
        d['inputData'] = inputData

        # print('tu.versionNumber={}'.format(d['catalogTaskDefinitionVersion']))
        
        d['id'] = 'joao-id-tu'
        # d['databaseId'] = -1

        return cls(**d)
    
#------------------------------------------------------------------------------
# WorkflowInstance: 
#------------------------------------------------------------------------------

class WorkflowInstance:
    """Initialize a WorkflowInstance object.

"""
    def __init__(self, workflowDefinition, id, name=None, userName=None,
                 resumeCount=None, inputData=None, tasksInputData=None,
                 tasksPreviousOutputData=None,terminationStatus=None,
                 timeoutInMillis=None, startDate=None, endDate=None,
                 status=None, doneTasks=None, runningTasks=None,
                 errorTasks=None, invariants=None,
                 taskDefinitionRetryCount=None, workspaceName=None, **kwargs):
        self.workflowDefinition = workflowDefinition
        self.id = id
        self.name = name
        self.userName = userName
        self.resumeCount = resumeCount
        self.terminationStatus = terminationStatus
        self.timeoutInMillis = timeoutInMillis
        self.startDate = startDate
        self.endDate = endDate
        self.status = status
        self.workspaceName = workspaceName

        # inputData, tasksInputData, doneTasks, runningTasks, errorTasks,
        # invariants, taskDefinitionRetryCount, 

        # inputData is a dictionary of object properties. In practice (as of
        # Oct.10, 2018) it's a "flat" dictionary, all values are strings.
        self.inputData = {}
        if inputData is not None:
            self.inputData = inputData

        # tasksInputData is a dictionary of object properties. In practice (as
        # of Oct.10, 2018) it's a "flat" dictionary, all values are strings.
        # Actually, the strings represent integers, but that's not the point
        # here, the point is that the json de-serializer can handle it.
        self.tasksInputData = {}
        if tasksInputData is not None:
            self.tasksInputData = tasksInputData

        # tasksPreviousOutputData has the same (strange) definition as the
        # previous tasksInputData object.
        self.tasksPreviousOutputData = {}
        if tasksPreviousOutputData is not None:
            self.tasksPreviousOutputData = tasksPreviousOutputData
        
        # doneTasks is an array of TaskUtilization
        self.doneTasks = []
        if doneTasks is not None:
            self.doneTasks = doneTasks
        
        # runningTasks is an array of TaskUtilization
        self.runningTasks = []
        if runningTasks is not None:
            self.runningTasks = runningTasks
        
        # errorTasks is an array of TaskUtilization
        self.errorTasks = []
        if errorTasks is not None:
            self.errorTasks = errorTasks

        # invariants is a dictionary of integer properties
        self.invariants = {}
        if invariants is not None:
            self.invariants = invariants

        # taskDefinitionRetryCount is a dictionary of integer properties
        self.taskDefinitionRetryCount = {}
        if taskDefinitionRetryCount is not None:
            self.taskDefinitionRetryCount = taskDefinitionRetryCount

    #---------------------------------------------------------------------------
    
    @classmethod
    def from_json_decoded(cls, obj):
        """Return a WorkflowInstance object from a json-decoded object.
"""
        d = {}
        # We iterate on the members actually present, ignoring absent ones.
        for k, v in obj.items():
            if k in ('workflowDefinition', 'doneTasks', 'runningTasks',
                         'errorTasks'):
                continue
            d[k] = v

        # Properties with non-json-serializable values
        if 'workflowDefinition' in obj:
            d['workflowDefinition'] = WorkflowDefinition.from_json_decoded(
                obj['workflowDefinition'])
        if 'doneTasks' in obj:
            d['doneTasks'] = [TaskUtilization.from_json_decoded(t)
                                 for t in obj['doneTasks']]
        if 'runningTasks' in obj:
            d['runningTasks'] = [TaskUtilization.from_json_decoded(t)
                                 for t in obj['runningTasks']]
        if 'errorTasks' in obj:
            d['errorTasks'] = [TaskUtilization.from_json_decoded(t)
                                 for t in obj['errorTasks']]

        return cls(**d)

# -----------------------------------------------------------------------------
# ParameterValue
# -----------------------------------------------------------------------------

class ParameterValue:
    """A ParameterValue represents an input or output to a task.
"""
    def __init__(self, stringValue='', arrayStringValue=None):
        self.stringValue = stringValue

        # arrayStringValue is an array of CatalogParameterType objects
        self.arrayStringValue = []
        if arrayStringValue is not None:
            self.arrayStringValue = arrayStringValue        

#-------------------------------------------------------------------------------
# User
#-------------------------------------------------------------------------------

class User:
    """A User represents someone with login rights.

    At the json level, every field is optional (which doesn't sound right).
"""
    def __init__(self, name=None, password=None, roles=None, workspaces=None,
                 profileNames=None):
        self.name = name
        self.password = password

        # roles is an array of strings: Admin, Write, Read
        self.roles = []
        if roles is not None:
            self.roles = roles

        # FIXME is a workspace mandatory ? or can we default to... the
        # DefaultWorkspace ?

        # workspaces is an array of strings
        self.workspaces = []
        if workspaces is not None:
            self.workspaces = workspaces

        # profileNames is an array of strings
        self.profileNames = []
        if profileNames is not None:
            self.profileNames = profileNames

    def to_json_encodable(self):
        """Create a json-encodable object representing a User.

        The returned object will be fed to the json encoder, to be
        json.dump'ed.  We use the object's __dict__ to ensure that optional
        members that did not receive a value are not included.
"""
        # Start building the resulting object with just the simple types
        d = {}
        for k, v in self.__dict__.items():
            val = getattr(self, k)
            # Do not include properties where the value is an empty list
            if val is None or val == '' or val == [] or val == {}:
                continue
            else:
                d[k] = val
        return d

    @classmethod
    def from_json_decoded(cls, obj):
        """Return a User object from a json-decoded object.
"""
        # Basically, this means I don't need a special json de-serializer
        return cls(**obj)

    def __str__(self):
        s = 'User:\n'
        s += '    name={}\n'.format(self.name)
        s += '    password={}\n'.format(self.password)
        s += '    profileNames=['
        s += ', '.join(self.profileNames)
        s += ']\n'
        return s

#-------------------------------------------------------------------------------
# UserCreateRequest 
#-------------------------------------------------------------------------------

class UserCreateRequest:
    """A UserCreateRequest is used to create a new User."""
    def __init__(self, name, password, profileNames):
        self.name = name
        self.password = password
        self.profileNames = profileNames  # array of strings

    def to_json_encodable(self):
        """Create a json-encodable object representing a UserCreateRequest.

        The returned object will be fed to the json encoder, to be
        json.dump'ed.  We use the object's __dict__ to ensure that optional
        members that did not receive a value are not included.
"""
        # Start building the resulting object with just the simple types
        d = {}
        for k, v in self.__dict__.items():
            val = getattr(self, k)
            if val is None or val == '' or val == [] or val == {}:
                continue
            else:
                d[k] = val
        return d

#-------------------------------------------------------------------------------
# UserUpdateRequest 
#-------------------------------------------------------------------------------

class UserUpdateRequest:
    """A UserUpdateRequest indicates changes to a User.

    At the json level, every field is optional (which doesn't sound right).
"""
    def __init__(self, newPassword=None, newProfileNames=None):
        self.newPassword = newPassword

        # newProfileNames is an array of strings
        self.newProfileNames = []
        if newProfileNames is not None:
            self.newProfileNames = newProfileNames

    def to_json_encodable(self):
        """Create a json-encodable object representing a UserUpdateRequest.

        The returned object will be fed to the json encoder, to be
        json.dump'ed.  We use the object's __dict__ to ensure that optional
        members that did not receive a value are not included.
"""
        # Start building the resulting object with just the simple types
        d = {}
        for k, v in self.__dict__.items():
            val = getattr(self, k)
            if val is None or val == '' or val == [] or val == {}:
                continue
            else:
                d[k] = val
        return d

    @classmethod
    def from_json_decoded(cls, obj):
        """Return a User object from a json-decoded object.
"""
        # Basically, this means I don't need a special json de-serializer
        return cls(**obj)

#-------------------------------------------------------------------------------
# UploadedFileDescriptor 
#-------------------------------------------------------------------------------

class UploadedFileDescriptor:
    """An UploadedFileDescriptor identifies a file to be uploaded."""
    def __init__(self, fileId, localPath):
        self.fileId = fileId
        self.localPath = localPath

    # this type is only used as a response, so no to_json_encodable() is needed
    @classmethod
    def from_json_decoded(cls, obj):
        """Return a User object from a json-decoded object.
"""
        # Basically, this means I don't need a special json de-serializer
        return cls(**obj)

    def __str__(self):
        return 'fileId: {}\nlocalPath: {}'.format(self.fileId, self.localPath)

#-------------------------------------------------------------------------------
# StartWorkflow 
#-------------------------------------------------------------------------------

class StartWorkflow:
    """A StartWorkflow object holds the parameters for a scenario launch."""
    def __init__(self, workflowDefinitionId, workflowDefinitionVersionNumber,
                 inputParameters=None, **kwargs):
        self.workflowDefinitionId = workflowDefinitionId
        self.workflowDefinitionVersionNumber = workflowDefinitionVersionNumber

        # inputParameters is a dictionary of ParameterValue values
        self.inputParameters = {}
        if inputParameters is not None:
            self.inputParameters = inputParameters

    # -------------------------------------------------------------------------
    
    def to_json_encodable(self):
        """Create a json-encodable object representing a UserUpdateRequest."""

        # Start building the resulting object with just the simple types
        d = {}
        for k, v in self.__dict__.items():
            val = getattr(self, k)
            if val is None or val == '' or val == [] or val == {}:
                continue
            else:
                d[k] = val

        return d

    # -------------------------------------------------------------------------

    @classmethod
    def from_json_decoded(cls, obj):
        """Return a User object from a json-decoded object.
"""
        # Basically, this means I don't need a special json de-serializer
        return cls(**obj)

    # -------------------------------------------------------------------------

    def __str__(self):
        return ('wkf_id={}, version={}, inputs={}'
                    .format(self.workflowDefinitionId,
                            self.workflowDefinitionVersionNumber,
                            self.inputParameters))

#-------------------------------------------------------------------------------
# Workspace - used in POST /api/Workspace
#-------------------------------------------------------------------------------

class Workspace:
    """A Workspace holds a number of scenarios."""
    def __init__(self, name=None, workflowDefinitionsLimit=None, license=None):
        self.name = name
        self.workflowDefinitionsLimit = workflowDefinitionsLimit
        self.license = license

    def to_json_encodable(self):
        """Create a json-encodable object representing this object."""
        
        # Start building the resulting object with just the simple types
        d = {}
        for k, v in self.__dict__.items():
            val = getattr(self, k)
            if val is None or val == '' or val == [] or val == {}:
                continue
            else:
                d[k] = val
        return d

    @classmethod
    def from_json_decoded(cls, obj):
        """Return a User object from a json-decoded object.
"""
        # Basically, this means I don't need a special json de-serializer
        return cls(**obj)

#-------------------------------------------------------------------------------
# WorkspaceCreateRequest - used in POST /api/Workspace
#-------------------------------------------------------------------------------

class WorkspaceCreateRequest:
    """A WorkspaceCreateRequest is used to create one single right."""
    def __init__(self, workspaceName, license):
        self.workspaceName = workspaceName
        self.license = license

    def to_json_encodable(self):
        """Create a json-encodable object representing this object.

        The returned object will be fed to the json encoder, to be
        json.dump'ed.  We use the object's __dict__ to ensure that optional
        members that did not receive a value are not included.
"""
        # Start building the resulting object with just the simple types
        d = {}
        for k, v in self.__dict__.items():
            val = getattr(self, k)
            if val is None or val == '' or val == [] or val == {}:
                continue
            else:
                d[k] = val
        return d

    # No need to decode, this object is only sent, never received. 

#-------------------------------------------------------------------------------
# Right 
#-------------------------------------------------------------------------------

class Right:
    """A Right defines one single right (by its name)."""
    def __init__(self, name=None):
        self.name = name
   
    def to_json_encodable(self):
        """Create a json-encodable object representing this object.

        The returned object will be fed to the json encoder, to be
        json.dump'ed.  We use the object's __dict__ to ensure that optional
        members that did not receive a value are not included.
"""
        # Start building the resulting object with just the simple types
        d = {}
        for k, v in self.__dict__.items():
            val = getattr(self, k)
            if val is None or val == '' or val == [] or val == {}:
                continue
            else:
                d[k] = val
        return d

    @classmethod
    def from_json_decoded(cls, obj):
        """Return a User object from a json-decoded object.
"""
        # Basically, this means I don't need a special json de-serializer
        return cls(**obj)

#-------------------------------------------------------------------------------
# ProfileCreateRequest - used in POST /api/Profile
#-------------------------------------------------------------------------------

class ProfileCreateRequest:
    """A ProfileCreateRequest is used to create one single right."""
    def __init__(self, profileName, profileRights, profileWorkspaces):
        self.profileName = profileName
        self.profileRights = profileRights  # array of strings
        self.profileWorkspaces = profileWorkspaces  # array of strings

    def to_json_encodable(self):
        """Create a json-encodable object representing this object.

        The returned object will be fed to the json encoder, to be
        json.dump'ed.  We use the object's __dict__ to ensure that optional
        members that did not receive a value are not included.
"""
        # Start building the resulting object with just the simple types
        d = {}
        for k, v in self.__dict__.items():
            val = getattr(self, k)
#            if val is None or val == '' or val == [] or val == {}:
            if val is None or val == '' or val == {}:
                continue
            else:
                d[k] = val
        # ugly hack: the above code was written specifically to avoid including
        # empty properties (optional properties that have not been set). But to
        # create a profile without rights, I need the empty list.
        
        return d

    # No need to decode, this object is only sent, never received. 

#-------------------------------------------------------------------------------
# ProfileUpdateRequest - used in POST /api/Profile
#-------------------------------------------------------------------------------

class ProfileUpdateRequest:
    """A ProfileUpdateRequest is used to update rights in a profile."""
    def __init__(self, workspaces=None, rights=None):
        self.workspaces = workspaces  # array of strings
        self.rights = rights  # array of strings

        # workspaces is an array of strings
        self.workspaces = []
        if workspaces is not None:
            self.workspaces = workspaces

        # rights is an array of strings
        self.rights = []
        if rights is not None:
            self.rights = rights

    def to_json_encodable(self):
        """Create a json-encodable object representing this object.

        The returned object will be fed to the json encoder, to be
        json.dump'ed.  We use the object's __dict__ to ensure that optional
        members that did not receive a value are not included.
"""
        # Start building the resulting object with just the simple types
        d = {}
        for k, v in self.__dict__.items():
            val = getattr(self, k)
            if val is None or val == '' or val == [] or val == {}:
                continue
            else:
                d[k] = val
        return d

    # No need to decode, this object is only sent, never received. 

# -----------------------------------------------------------------------------
# Profile 
# -----------------------------------------------------------------------------

class Profile:
    """A Profile defines a set of rights.

    At the json level, every field is optional (which doesn't sound right).
"""
    def __init__(self, name=None, rightIds=None, workspaceIds=None):
        self.name = name

        # rightIds is an array of strings
        self.rightIds = []
        if rightIds is not None:
            self.rightIds = rightIds

        # workspaceIds is an array of strings
        self.workspaceIds = []
        if workspaceIds is not None:
            self.workspaceIds = workspaceIds
   
    def to_json_encodable(self):
        """Create a json-encodable object representing this object.

        The returned object will be fed to the json encoder, to be
        json.dump'ed.  We use the object's __dict__ to ensure that optional
        members that did not receive a value are not included.
"""
        # Start building the resulting object with just the simple types
        d = {}
        for k, v in self.__dict__.items():
            val = getattr(self, k)
            if val is None or val == '' or val == [] or val == {}:
                continue
            else:
                d[k] = val
        return d

    @classmethod
    def from_json_decoded(cls, obj):
        """Return a User object from a json-decoded object.
"""
        # Basically, this means I don't need a special json de-serializer
        return cls(**obj)

# -----------------------------------------------------------------------------
# CancellationStatus 
# -----------------------------------------------------------------------------

class CancellationStatus:
    """A CancellationStatus """
    def __init__(self, isCancelled):
        self.isCancelled = isCancelled

# -----------------------------------------------------------------------------
# TaskStatusMessage
# -----------------------------------------------------------------------------

class TaskStatusMessage:
    """A TaskStatusMessage object """
    def __init__(self, message=None, timeStamp=None, progressPercentage=None):
        self.message = message
        self.timeStamp = timeStamp
        self.progressPercentage = progressPercentage

    @classmethod
    def from_json_decoded(cls, obj):
        """Return a User object from a json-decoded object.
"""
        # Basically, this means I don't need a special json de-serializer
        return cls(**obj)

# -----------------------------------------------------------------------------
# TaskMonitoringEvent
# -----------------------------------------------------------------------------

class TaskMonitoringEvent:
    """A TaskMonitoringEvent object """
    def __init__(self, id=None, taskInstanceId=None, taskDescription=None,
                 workflowInstanceId=None, workflowDefinitionName=None,
                 workflowDefinitionId=None,
                 workflowDefinitionVersionNumber=None,
                 workflowInstanceResumeCount=None, inputData=None,
                 previousOutputData=None, outputData=None,
                 invariants=None, taskDefinitionId=None, status=None,
                 errorLevel=None, messages=None, timeStamp=None,
                 catalogTaskDefinitionNamespace=None,
                 catalogTaskDefinitionName=None,
                 catalogTaskDefinitionVersion=None, userName=None,
                 workerId=None, startTime=None, endTime=None,
                     creationDate=None, workspaceName=None):
        self.id = id
        self.taskInstanceId = taskInstanceId
        self.taskDescription = taskDescription
        self.workflowInstanceId = workflowInstanceId
        self.workflowDefinitionName = workflowDefinitionName
        self.workflowDefinitionId = workflowDefinitionId
        self.workflowDefinitionVersionNumber = workflowDefinitionVersionNumber
        self.workflowInstanceResumeCount = workflowInstanceResumeCount
        self.taskDefinitionId = taskDefinitionId
        self.status = status
        self.errorLevel = errorLevel
        self.timeStamp = timeStamp
        self.catalogTaskDefinitionNamespace = catalogTaskDefinitionNamespace
        self.catalogTaskDefinitionName = catalogTaskDefinitionName
        self.catalogTaskDefinitionVersion = catalogTaskDefinitionVersion
        self.userName = userName
        self.workerId = workerId
        self.startTime = startTime
        self.endTime = endTime
        self.creationDate = creationDate
        self.workspaceName = workspaceName

        # inputData is an array of objects
        self.inputData = []
        if inputData is not None:
            self.inputData = inputData

        # previousOutputData is an array of objects
        self.previousOutputData = []
        if previousOutputData is not None:
            self.previousOutputData = previousOutputData

        # outputData is an array of objects
        self.outputData = []
        if outputData is not None:
            self.outputData = outputData

        # invariants is a dictionary of integer properties
        self.invariants = {}
        if invariants is not None:
            self.invariants = invariants

        # messages is an array of TaskStatusMessage objects
        self.messages = []
        if messages is not None:
            self.messages = messages

    #--------------------------------------------------------------------------

    @classmethod
    def from_json_decoded(cls, obj):
        """Return a TaskMonitoringEvent object from a json-decoded object.
"""
        d = {}
        # We iterate on the members actually present, ignoring absent ones.
        for k, v in obj.items():
            if k in ['messages']:
                continue
            d[k] = v

        # Properties with non-json-serializable values
        if 'messages' in obj:
            d['messages'] = [TaskStatusMessage.from_json_decoded(x)
                                 for x in obj['messages']]
        return cls(**d)

# -----------------------------------------------------------------------------
# WorkflowInstanceMonitoringEvent
# -----------------------------------------------------------------------------

class WorkflowInstanceMonitoringEvent:
    """A WorkflowInstanceMonitoringEvent object """
    def __init__(self, id=None, workflowInstance=None):
        self.id = id
        # FIXME is this new ? a member is an instance of another object
        self.workflowInstance = workflowInstance

    @classmethod
    def from_json_decoded(cls, obj):
        """Return a WorkflowInstanceMonitoringEvent object from a
        json-decoded object."""
        
        d = {}
        # We iterate on the members actually present, ignoring absent ones.
        for k, v in obj.items():
            if k in ['workflowInstance']:
                continue
            d[k] = v

        # Properties with non-json-serializable values
        if 'workflowInstance' in obj:
            d['workflowInstance'] = WorkflowInstance.from_json_decoded(obj['workflowInstance'])

        return cls(**d)

# -----------------------------------------------------------------------------
# EventsDeleted
# -----------------------------------------------------------------------------

class EventsDeleted:
    """A EventsDeleted object """
    def __init__(self, taskEventsDeleted=None,
                 workflowInstanceMonitoringEventsDeleted=None):

        # taskEventsDeleted is an array of TaskMonitoringEvent objects
        self.taskEventsDeleted = []
        if taskEventsDeleted is not None:
            self.taskEventsDeleted = taskEventsDeleted

        # workflowInstanceMonitoringEventsDeleted is an array of
        # WorkflowInstanceMonitoringEvent objects
        self.workflowInstanceMonitoringEventsDeleted = []
        if workflowInstanceMonitoringEventsDeleted is not None:
            # Can't split this line
            self.workflowInstanceMonitoringEventsDeleted = workflowInstanceMonitoringEventsDeleted

    #--------------------------------------------------------------------------

    @classmethod
    def from_json_decoded(cls, obj):
        """Return a TaskMonitoringEvent object from a json-decoded object.
"""
        d = {}
        # We iterate on the members actually present, ignoring absent ones.
        for k, v in obj.items():
            if k in [
                'taskEventsDeleted',
                'workflowInstanceMonitoringEventsDeleted']:
                continue
            d[k] = v

        # Properties with non-json-serializable values
        
        if 'taskEventsDeleted' in obj:
            d['taskEventsDeleted'] = [TaskMonitoringEvent.from_json_decoded(x)
                                          for x in obj['taskEventsDeleted']]
            
        if 'workflowInstanceMonitoringEventsDeleted' in obj:
            d['workflowInstanceMonitoringEventsDeleted'] = [TaskMonitoringEvent.from_json_decoded(x)
                    for x in obj['workflowInstanceMonitoringEventsDeleted']]
        return cls(**d)

#------------------------------------------------------------------------------
# main
#------------------------------------------------------------------------------

if __name__ == '__main__':
    print("Module 'k' implements all the Koordinator objects,\n" +
          'it is not meant to be executed directly.')
    
