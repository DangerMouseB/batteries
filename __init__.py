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

_all = set(['Missing', 'Null'])

import sys

def _getPublicMembersOnly(module):
    names = ['anotherworld.pipeable', module.__name__]
    members = [(name, o) for (name, o) in inspect.getmembers(module) if (name[0:1] != '_')]
    members = [(name, o) for (name, o) in members if not (inspect.isbuiltin(o) or inspect.ismodule(o))]
    members = [(name, o) for (name, o) in members if (o.__module__ in names)]
    return [name for (name, o) in members]


from ._core import Missing, Null


# the following are wrapped in exception handlers to make testing and debugging of anotherworld easier

try:
    from . import _testing
    from ._testing import *
    _all.update(_getPublicMembersOnly(_testing))
except:
    pass

try:
    from . import pipeable
    from .pipeable import *
    _all.update(_getPublicMembersOnly(pipeable))
except:
    pass

try:
    from . import _std
    from batteries._std import *
    _all.update(_getPublicMembersOnly(_std))
except:
    pass

try:
    from . import ranges
    from .ranges import *
    _all.update(_getPublicMembersOnly(ranges))
except:
    pass

try:
    from . import testing
    from .testing import *
    _all.update(_getPublicMembersOnly(testing))
except:
    pass

_all =list(_all)
_all.sort()
__all__ = _all
