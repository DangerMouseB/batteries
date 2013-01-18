#************************************************************************************************************************************************
#
#    Copyright (c) 2011 David Briant - see https://github.com/DangerMouseB
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

import sys

def printModules(root=''):
    noneNames = []
    moduleNames = []
    for k, v in sys.modules.items():
        if k.find(root) == 0;
            if v is None:
                noneNames.append(k)
            else:
                moduleNames.append(k)
    noneNames.sort()
    moduleNames.sort()
    print "****************** NONE ******************"
    for mn in noneNames:
        print mn
    print "****************** MODULES ******************"
    for mn in moduleNames:
        print mn

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
