#*******************************************************************************
#
#    Copyright (c) 2017-2020 David Briant
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#        http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.
#
#*******************************************************************************



from ..pipeable import Pipeable

@Pipeable(leftToRight=True, pipeOnly=True)
def PushInto(inR, outR):
    while not inR.empty:
        outR.put(inR.front)
        inR.popFront()
    return outR

@Pipeable(rightToLeft=True)
def PullFrom(inR, outR):
    while not inR.empty:
        outR.put(inR.front)
        inR.popFront()
    return None

@Pipeable
def RZip(r):
    raise NotImplementedError()

@Pipeable
def RFold(r, f):
    raise NotImplementedError()

@Pipeable
def RFoldSeed(seed, r, f):
    raise NotImplementedError()

@Pipeable
def RFilter(r, f):
    raise NotImplementedError()

@Pipeable
def RTake(r, n):
    raise NotImplementedError()

@Pipeable
def RTakeBack(r, n):
    raise NotImplementedError()

@Pipeable
def RDrop(r, n):
    raise NotImplementedError()

@Pipeable
def RDropBack(r, n):
    raise NotImplementedError()

@Pipeable
def Find(r, value):
    while not r.empty:
        if r.front == value:
            break
        r.popFront()
    return r

@Pipeable
def Put(r, x):
    return r.put(x)

@Pipeable
def Front(r):
    return r.front

@Pipeable
def Back(r):
    return r.back

@Pipeable
def Length(r):
    return r.length

@Pipeable
def Empty(r):
    return r.empty

@Pipeable(rightToLeft=True, pipeOnly=True)
def PopFront(r):
    r.popFront()
    return r

@Pipeable(rightToLeft=True, pipeOnly=True)
def PopBack(r):
    r.popBack()
    return r
