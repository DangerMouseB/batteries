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

__all__ = ['PP', 'PPP', 'DD', 'HH', 'TT']

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
        print(help(other))
        return other

    def __lshift__(self, other):
        # self << other
        print(help(other))
        return self


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