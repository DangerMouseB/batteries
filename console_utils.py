# python imports
from pprint import pprint
from copy import copy

__all__ = ['PP', 'PPP', 'DD', 'HH', 'TT']

_list_iter_type = type(iter([]))


class _PipeablePrint(object):
    def __init__(self, isPretty):
        self._isPretty = isPretty

    def __rrshift__(self, other):
        # other >> self
        self._Print(other)
        return other

    def __lshift__(self, other):
        # self << other
        self._Print(other)
        return self

    def _Print(self, other):
        if isinstance(other, _list_iter_type):
            other = list(copy(other))
        if self._isPretty:
            pprint(other)
        else:
            print(other)


PP = _PipeablePrint(False)
PPP = _PipeablePrint(True)


class _PipeableDir(object):
    def __rrshift__(self, other):
        # other >> self
        print(dir(other))
        return other

    def __lshift__(self, other):
        # self << other
        print(dir(other))
        return self


DD = _PipeableDir()


class _PipeableHelp(object):
    def __rrshift__(self, other):
        # other >> self
        print(help(other))
        return other

    def __lshift__(self, other):
        # self << other
        print(help(other))
        return self


HH = _PipeableHelp()


class _PipeableType(object):
    def __rrshift__(self, other):
        # other >> self
        print(type(other))
        return other

    def __lshift__(self, other):
        # self << other
        print(type(other))
        return self


TT = _PipeableType()