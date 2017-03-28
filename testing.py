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

EPS = 7.105427357601E-15


class NotTestedError(Exception): pass


def close(a, b, tolerance=EPS):
    if abs(a) < tolerance:
        return abs(b) < tolerance
    else:
        return abs(a - b) / abs(a) < tolerance


class StdoutHooker(object):

    def __init__(self, lines):
        self.lines = lines
        self.textBuffer = ""

    def write(self, text=""):
        if len(text) > 0:
            splits = text.split("\n")
            for split in splits[:-1]:
                self.textBuffer += split
                self.lines.append(self.textBuffer)
                self.textBuffer = ""
            self.textBuffer += splits[-1:][0]
        else:
            raise NotImplemented

    def __enter__(self):
        self.oldStdout = sys.stdout
        sys.stdout = self

    def __exit__(self, type, e, tb):
        sys.stdout = self.oldStdout
        return False


def ErrorTypeRaised(func, *args, **kwargs):
    """Python 2.4 equivalent to AssertRaises"""
    et = None
    try:
        nothing = func(*args, **kwargs)
    except:
        et, ev, tb = sys.exc_info()
    return et


class AssertRaises(object):

    def __init__(self, expectedExceptionType):
        self.expectedExceptionType = expectedExceptionType
        self.exceptionType = None
        self.exceptionValue = None
        self.traceback = None

    def __enter__(self):
        return self

    def __exit__(self, exceptionType, exceptionValue, traceback):
        self.exceptionType = exceptionType
        self.exceptionValue = exceptionValue
        self.traceback = traceback
        if exceptionType is None: raise AssertionError("No exception raised, %s expected." % self.expectedExceptionType)        # no error was raised
        if issubclass(exceptionType, self.expectedExceptionType):  return True               # the right error was raised
        raise AssertionError("%s raised. %s expected." % (exceptionType, self.expectedExceptionType) )

