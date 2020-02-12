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
from ..ranges import RMap


@Pipeable
def Sorted(iterable, key=None, reverse=False):
    return sorted(iterable, key, reverse)

@Pipeable
def Len(lenable):
    return len(lenable)

@Pipeable
def WrapInList(x):
    l = []
    l.append(x)
    return l

@Pipeable
def First(x):
    raise NotImplementedError()

@Pipeable
def Last(x):
    raise NotImplementedError()

@Pipeable
def Take(x):
    raise NotImplementedError()

@Pipeable
def Cut(x):
    raise NotImplementedError()

@Pipeable
def ReplaceWith(haystack, needle, replacement):
    return haystack >> RMap >> (lambda e: replacement if e == needle else e)


