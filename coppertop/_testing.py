# *******************************************************************************
#
#    Copyright (c) 2011-2020 David Briant
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


import sys, traceback, contextlib
# from io import StringIO



@contextlib.contextmanager
def HookStdOutErrToLines():
    oldout, olderr = sys.stdout, sys.stderr
    try:
        sys.stdout = StreamToLines()
        sys.stderr = StreamToLines()
        yield [sys.stdout.lines, sys.stderr.lines]
    finally:
        sys.stdout, sys.stderr = oldout, olderr


class StreamToLines(object):
    def __init__(self):
        self.lines = []
        self.textBuffer = ""
    def write(self, text=""):
        if len(text) > 0:
            splits = text.split("\n")
            for split in splits[:-1]:
                self.textBuffer += split
                self.lines.append(self.textBuffer)
                self.textBuffer = ""
            self.textBuffer += splits[-1:][0]



class AssertRaises(object):

    def __init__(self, expectedExceptionType):
        self.expectedExceptionType = expectedExceptionType
        self.exceptionType = None
        self.exceptionValue = None
        self.tb = None

    def __enter__(self):
        return self

    def __exit__(self, exceptionType, exceptionValue, tb):
        self.exceptionType = exceptionType
        self.exceptionValue = exceptionValue
        self.tb = tb
        if exceptionType is None: raise AssertionError("No exception raised, %s expected." % self.expectedExceptionType)        # no error was raised
        if issubclass(exceptionType, self.expectedExceptionType):
            return True               # the correct error was raised
        # traceback.print_tb(tb)    Don't think this makes much sense
        raise AssertionError("%s raised. %s expected." % (exceptionType, self.expectedExceptionType) )

