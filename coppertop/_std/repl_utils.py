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


_list_iter_type = type(iter([]))
_numpy = None        # don't import numpy proactively


@Pipeable(leftToRight=True, rightToLeft=True)
def _callFReturnX(f, x):
    f(x)
    return x
PP = _callFReturnX(print)

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