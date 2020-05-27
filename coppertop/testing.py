# *******************************************************************************
#
#    Copyright (c) 2019-2020 David Briant
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


from ._testing import HookStdOutErrToLines, AssertRaises
from .pipeable import Pipeable


_EPS = 7.105427357601E-15      # i.e. double precision


@Pipeable
def AssertEqual(actual, expected, suppressMsg=False, keepWS=False, returnResult=False, tolerance=_EPS):
    if keepWS:
        act = actual
        exp = expected
    else:
        act = actual.replace(" ", "").replace("\n", "") if isinstance(actual, (str,)) else actual
        exp = expected.replace(" ", "").replace("\n", "") if isinstance(expected, (str,)) else expected
    if isinstance(act, (int, float)) and isinstance(exp, (int, float)):
        equal = act >> CloseTo(tolerance=tolerance) >> exp
    else:
        equal = act == exp
    if returnResult:
        return equal
    else:
        if not equal:
            if suppressMsg:
                raise AssertionError()
            else:
                if isinstance(actual, (str,)):
                    actual = '"' + actual + '"'
                if isinstance(expected, (str,)):
                    expected = '"' + expected + '"'
                raise AssertionError('expected %s but got %s' % (expected, actual))
        else:
            return None


@Pipeable
def CloseTo(a, b, tolerance=_EPS):
    if abs(a) < tolerance:
        return abs(b) < tolerance
    else:
        return abs(a - b) / abs(a) < tolerance

