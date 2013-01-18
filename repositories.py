#************************************************************************************************************************************************
#
#    Copyright (c) 2011-2012 David Briant - see https://github.com/DangerMouseB
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
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
    
 