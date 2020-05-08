# *******************************************************************************
#
#    Copyright (c) 2020 David Briant
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
# *******************************************************************************


_all = set()

import inspect

def _getPublicMembersOnly(module):
    names = ['coppertop.pipeable', module.__name__]
    members = [(name, o) for (name, o) in inspect.getmembers(module) if (name[0:1] != '_')]
    members = [(name, o) for (name, o) in members if not (inspect.isbuiltin(o) or inspect.ismodule(o))]
    members = [(name, o) for (name, o) in members if (o.__module__ in names)]
    return [name for (name, o) in members]


# the following are wrapped in exception handlers to make testing and debugging of coppertop easier

try:
    from . import _enums
    from ._enums import *
    _all.update(_getPublicMembersOnly(_enums))
except:
    pass

try:
    from . import _core
    from ._core import *
    _all.update(_getPublicMembersOnly(_core))
except:
    pass


_all =list(_all)
_all.sort()
__all__ = _all
