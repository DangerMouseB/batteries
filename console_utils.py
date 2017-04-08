#************************************************************************************************************************************************
#
# Copyright 2017 David Briant
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#************************************************************************************************************************************************


# python imports
from pprint import pprint
from copy import copy

# 3rd party imports
import numpy as np


__all__ = ['PP', 'PPP', 'DD', 'HH', 'TT', 'CRPP', 'LL']

_list_iter_type = type(iter([]))


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

PP = _PipeablePrint(False)
PPP = _PipeablePrint(True)


class _PipeableDir(object):
    def __rrshift__(self, other):
        # other >> self
        print(dir(other))
        return other

    def __lshift__(self, other):
        # self << other
        print(dir(other))
        return self

DD = _PipeableDir()


class _PipeableHelp(object):
    def __rrshift__(self, other):
        # other >> self
        self._help(other)
        return other

    def __lshift__(self, other):
        # self << other
        self._help(other)
        return self

    def _help(self, obj):
        if hasattr(obj, '_doc'):
            print(obj._doc)
        else:
            help(obj)

HH = _PipeableHelp()


class _PipeableType(object):
    def __rrshift__(self, other):
        # other >> self
        print(type(other))
        return other

    def __lshift__(self, other):
        # self << other
        print(type(other))
        return self

TT = _PipeableType()


class _PipeableLen(object):

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
        if isinstance(other, np.ndarray):
            print(other.shape)
        else:
            print(len(other))

LL = _PipeableLen()


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
