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
from .missing import Missing
import datetime

_np = None        # don't import numpy proactively

_list_iter_type = type(iter([]))


# Composition - could be made more efficient

@Pipeable(overrideLHS=True)
def Compose(f1, f2):
    @Pipeable
    def _Composed(x):
        return x >> f1 >> f2
    return _Composed

@Pipeable(overrideLHS=True)
def ComposeAll(f1, f2):
    raise NotImplementedError


# array iteration (rather than range iteration)

@Pipeable
def Each(xs, f):
    """each(xs, f)  e.g. xs >> Each >> f
    Answers [f(x) for x in xs]"""
    return [f(x) for x in xs]

@Pipeable
def EachIf(xs, f, ifF):
    """each(xs, f)  e.g. xs >> EachIf >> f >> ifF
    Answers [f(x) for x in xs]"""
    return [f(x) for x in xs if ifF(x)]

@Pipeable
def Chain(seed, xs, f):
    """chain(seed, xs, f)    e.g. xs >> Chain(seed) >> f
    Answers resultn where resulti=f(prior, xi) for each x in xs
    prior = resulti-1 or seed initially"""
    prior = seed
    for x in xs:
        prior = f(prior, x)
    return prior

@Pipeable
def EachArgs(listOfArgs, f):
    """eachArgs(f, listOfArgs)
    Answers [f(*args) for args in listOfArgs]"""
    return [f(*args) for args in listOfArgs]


# array utils

@Pipeable
def Sorted(iterable, key=None, reverse=False):
    return sorted(iterable, key, reverse)

@Pipeable
def Len(lenable):
    return len(lenable)

@Pipeable
def WrapInList(x):
    l = []
    l.append(x)
    return l


@Pipeable
def First(x):
    raise NotImplementedError()

@Pipeable
def Last(x):
    raise NotImplementedError()

@Pipeable
def Take(x):
    raise NotImplementedError()

@Pipeable
def Cut(x):
    raise NotImplementedError()


# conversions

@Pipeable
def ToStr(x):
    return str(x)

@Pipeable
def ToInt(a):
    return int(a)


# other

@Pipeable
def Not(x):
    return not x


# string utills

@Pipeable
def Strip(s,  chars=None):
    return s.strip(chars)

@Pipeable
def LJust(w, s, pad=" "):
    return s.ljust(w, pad)

@Pipeable
def RJust(w, s, pad=" "):
    return s.rjust(w, pad)

@Pipeable
def CJust(w, s, pad=" "):
    return s.center(w, pad)

@Pipeable
def Join(s, iter):
    return s.join(iter)

@Pipeable
def Format(format, thing):
    return format.format(thing)


# datetime.date utilities

@Pipeable
def ToDate(x, strFormat=Missing):
    if strFormat is Missing:
        # assume kdb format
        # TODO implement other conversions
        return datetime.date(*x.split(".") >> Each >> ToInt)
    else:
        raise NotImplementedError()

@Pipeable
def Weekday(x):
    return x.weekday()

@Pipeable
def Year(x):
    return x.year

@Pipeable
def Month(x):
    return x.month

@Pipeable
def Day(x):
    return x.day

@Pipeable
def WeekdayName(x, locale=Missing):
    # TODO implement for other locales
    return ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][x]

@Pipeable
def WeekdayLongName(x, locale=Missing):
    # TODO implement for other locales
    return ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][x]

@Pipeable
def MonthName(month, locale=Missing):
    # TODO implement for other locales
    return ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][month - 1]

@Pipeable
def MonthLongName(month, locale=Missing):
    # TODO implement for other locales
    return ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][month - 1]


# REPL utilities

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
    global _np
    if type(x).__name__ != "ndarray":
        return False
    try:
        import numpy as _np
        return isinstance(x, _np.ndarray)
    except AttributeError:      # cf None.ndarray if numpy is not installed
        return False

def _printLen(x):
    if isinstance(x, _list_iter_type):
        x = list(copy(x))
    if x >> IsNdArray:
        print(x.shape)
    else:
        print(len(x))

LL = _callFReturnX(_printLen)



@Pipeable
def GetAttr(x, name):
    return getattr(x, name)
