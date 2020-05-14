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


from pprint import pprint
from copy import copy
from ..pipeable import Pipeable


_list_iter_type = type(iter([]))
_numpy = None        # don't import numpy proactively

# Consider the following - print converts to str and embedding in a build-in converts to repr - which means to be
# consistent we have to use print(repr(Fred)) - in the bones ipython kernel we output repr
#
# class Fred():
#     def __str__(self):
#         return 'str Fred'
#     def __repr__(self):
#         return 'repr Fred'
#
# print((Fred(),));
# Fred() >> SS
# print([Fred(),]);
# Fred() >> PP;
#
# (repr Fred,)
# str Fred
# [repr Fred]
# repr Fred

@Pipeable(leftToRight=True, rightToLeft=True)
def _callFReturnX(f, x):
    f(x)
    return x

def _printRepr(x):
    print(repr(x))
PP = _callFReturnX(_printRepr)

def _printStr(x):
    print(str(x))
SS = _callFReturnX(_printStr)

def _printDir(x):
    print(dir(x))
DD = _callFReturnX(_printDir)

def _printHelp(x):
    if hasattr(x, '_doc'):
        print(x._doc)
    else:
        help(x)
HH = _callFReturnX(_printHelp)

def _printType(x):
    print(type(x))
TT = _callFReturnX(_printType)

@Pipeable
def IsNdArray(x):
    global _numpy
    if type(x).__name__ != "ndarray":
        return False
    try:
        import numpy as _numpy
        return isinstance(x, _numpy.ndarray)
    except (ModuleNotFoundError, AttributeError):      # cf None.ndarray if numpy is not installed
        return False

def _printLen(x):
    if isinstance(x, _list_iter_type):
        x = list(copy(x))
    if x >> IsNdArray:
        print(x.shape)
    else:
        print(len(x))

LL = _callFReturnX(_printLen)



class _PipeablePrint(object):
    def __init__(self, isPretty):
        self._isPretty = isPretty

    def __rrshift__(self, other):
        # other >> self
        self._Print(other)
        return other

    def __lshift__(self, other):
        # self << other
        self._Print(other)
        return self

    def _Print(self, other):
        if isinstance(other, _list_iter_type):
            other = list(copy(other))
        if self._isPretty:
            pprint(other)
        else:
            print(other)

PPP = _PipeablePrint(True)


class _PipeablePrintSplitCR(object):

    def __rrshift__(self, other):
        # other >> self
        self._Print(other)
        return other

    def __lshift__(self, other):
        # self << other
        self._Print(other)
        return self

    def _Print(self, other):
        if isinstance(other, _list_iter_type):
            other = list(copy(other))
        for line in other.split('\n'):
            print(line)

CRPP = _PipeablePrintSplitCR()


@Pipeable
def Pipeables(arg):
    return sorted([k for k, v in arg.items() if isinstance(v, (Pipeable,))])
