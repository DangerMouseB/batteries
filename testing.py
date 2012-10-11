#************************************************************************************************************************************************
#
# Copyright (c) 2011 David Briant  - All rights reserved
#
#************************************************************************************************************************************************

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

