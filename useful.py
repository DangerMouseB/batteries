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



from .pipeable import Pipeable
_EPS = 7.105427357601E-15      # i.e. double precision


@Pipeable
def assertEqual(actual, expected, suppressMsg=False, keepWS=False, tolerance=_EPS):
    if keepWS:
        act = actual
        exp = expected
    else:
        act = actual.replace(" ", "").replace("\n", "") if isinstance(actual, (str,)) else actual
        exp = expected.replace(" ", "").replace("\n", "") if isinstance(expected, (str,)) else expected
    if isinstance(act, (int, float)) and isinstance(exp, (int, float)):
        equal = act >> closeTo(tolerance=tolerance) >> exp
    else:
        equal = act == exp
    if equal:
        return True
    else:
        if suppressMsg:
            raise AssertionError()
        else:
            if isinstance(actual, (str,)):
                actual = '"' + actual + '"'
            if isinstance(expected, (str,)):
                expected = '"' + expected + '"'
            raise AssertionError('expected %s but got %s' % (expected, actual))

@Pipeable
def closeTo(a, b, tolerance=_EPS):
    if abs(a) < tolerance:
        return abs(b) < tolerance
    else:
        return abs(a - b) / abs(a) < tolerance

@Pipeable
def each(xs, f):
    """each(xs, f)  e.g. xs >> each >> f
    Answers [f(x) for x in xs]"""
    return [f(x) for x in xs]

@Pipeable
def chain(seed, xs, f):
    """chain(seed, xs, f)    e.g. xs >> chain(seed) >> f
    Answers resultn where resulti=f(prior, xi) for each x in xs
    prior = resulti-1 or seed initially"""
    prior = seed
    for x in xs:
        prior = f(prior, x)
    return prior

@Pipeable
def eachArgs(listOfArgs, f):
    """eachArgs(f, listOfArgs)
    Answers [f(*args) for args in listOfArgs]"""
    return [f(*args) for args in listOfArgs]




