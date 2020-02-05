#*******************************************************************************
#
#    Copyright (c) 2011-2012 David Briant
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

_all = set(['Missing', 'null'])

import inspect, sys

def _getAll(module):
    names = ['batteries.pipeable', module.__name__]
    members = [(name, o) for (name, o) in inspect.getmembers(module) if (name[0:1] != '_')]
    members = [(name, o) for (name, o) in members if not (inspect.isbuiltin(o) or inspect.ismodule(o))]
    members = [(name, o) for (name, o) in members if (o.__module__ in names)]
    return [name for (name, o) in members]


from .missing import Missing

if not hasattr(sys, '_NULL'):
    class _NULL(object):
        # def __str__(self):
        #     return 'na'
        def __repr__(self):
            # for pretty display in pycharm debugger
            return 'null'
    sys._NULL = _NULL()
nill = sys._NULL

# the following are wrapped in exception handlers to make testing and debugging easier

try:
    from . import _testing
    from ._testing import *
    _all.update(_getAll(_testing))
except:
    pass

try:
    from . import pipeable
    from .pipeable import *
    _all.update(_getAll(pipeable))
except:
    pass

try:
    from . import useful
    from .useful import *
    _all.update(_getAll(useful))
except:
    pass

try:
    from . import ranges
    from .ranges import *
    _all.update(_getAll(ranges))
except:
    pass

try:
    from . import testing
    from .testing import *
    _all.update(_getAll(testing))
except:
    pass

_all =list(_all)
_all.sort()
__all__ = _all
