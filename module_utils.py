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


import sys

def printModules(root=''):
    noneNames = []
    moduleNames = []
    for k, v in sys.modules.items():
        if k.find(root) == 0:
            if v is None:
                noneNames.append(k)
            else:
                moduleNames.append(k)
    noneNames.sort()
    moduleNames.sort()
    print("****************** NONE ******************")
    for mn in noneNames:
        print(mn)
    print("****************** MODULES ******************")
    for mn in moduleNames:
        print(mn)

def unloadIf(module_name, condition=True, leaveRelativeImportsOptimisation=False):
    # for description of relative imports optimisation in earlier versions of python see:
    # http://www.python.org/dev/peps/pep-0328/#relative-imports-and-indirection-entries-in-sys-modules

    if condition:
        l = len(module_name)
        for name in sys.modules.keys():
            if name[:l] == module_name:
                if leaveRelativeImportsOptimisation:
                    if sys.modules[name] is not None:
                        del sys.modules[name]
                else:
                    del sys.modules[name]
