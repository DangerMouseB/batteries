#************************************************************************************************************************************************
#
# Copyright (c) 2011 David Briant  - All rights reserved
#
#************************************************************************************************************************************************

repositories = {}      # {} of objectName -> (id, object) pairs keyed by repositoryName


def objectName(objectNameMaybeWithTicker):
    return objectNameMaybeWithTicker.strip().split(".")[0]

def objectKey(objectName):
    return objectName.strip().upper().split(".")[0]

def getIDAndObject(repositoryName, objectName):
    return getRepository(repositoryName.strip().upper()).get(objectKey(objectName))

def objectID(repositoryName, objectName):
    t = getIDAndObject(repositoryName, objectName)
    if t is None:
        return 0
    else:
        return t[0]

def object(repositoryName, objectName):
    t = getIDAndObject(repositoryName, objectName)
    if t is None:
        return None
    else:
        return t[1]

def setObject(repositoryName, objectName, object):
    repository = getRepository(repositoryName.strip().upper())
    key = objectKey(objectName)
    t = repository.get(key)
    if t is None:
        newID = 1
    else:
        newID = t[0] + 1
    repository[key] = (newID, object)

def dropObject(repositoryName, objectName):
    t = getRepository(repositoryName.strip().upper()).pop(objectKey(objectName), None)    
    if t is None:
        return None
    else:
        return t[1]
    
def getRepository(repositoryName):
    name = repositoryName.strip().upper()
    repository = repositories.get(name)
    if repository is None: 
        repository = {}
        repositories[name] = repository
    return repository
    
 