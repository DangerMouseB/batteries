#************************************************************************************************************************************************
#
# Copyright 2017-2020 David Briant
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License atA2WQ
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#************************************************************************************************************************************************


"""Pipeable is a decorator that extends a function with the >> and << opertors with the effect of adding pipeline like behaviour (e.g. similar to |> in F#)

x >> f   and   fn >> x   both answer fn(x)
x << f   calls fn(x) and answers x
f << x   calls fn(x) and answers fn

or equivalently
lhs >> rhs   answers f(x)
lhs << rhs   calls f(x) and answers the lhs

See /tests/test_pipeable for a fuller description and code examples
"""

from __future__ import annotations


from typing import Any, Union
import types, inspect, collections, sys
from ._core import Missing



def Pipeable(*args, overrideLHS=False, pipeOnly=False, leftToRight=Missing, rightToLeft=Missing):
    # overrideLHS allows a higher order function PF2 to override the behaviour of another PipeableFunction PF1
    # for PF1 >> PF2 or PF1 << PF2, i.e. execution order changes from PF1(), PF2() to PF2(), PF1()

    leftToRight, rightToLeft = (True, False) if (leftToRight is Missing and rightToLeft is Missing) else (leftToRight, rightToLeft)
    leftToRight = not rightToLeft if leftToRight is Missing else leftToRight
    rightToLeft = not leftToRight if rightToLeft is Missing else rightToLeft

    def _DecorateWithPF(fnOrClass):
        coreBindings = {}
        optionalBindings = {}
        optionalBindingsReprs = []
        hasKwargs = False
        if isinstance(fnOrClass, type):
            parameters = dict(inspect.signature(fnOrClass.__init__).parameters)
            selfName = list(parameters.keys())[0]
            del parameters[selfName]
        else:
            parameters = inspect.signature(fnOrClass).parameters
        for name, parameter in parameters.items():
            if parameter.kind == inspect.Parameter.VAR_POSITIONAL:
                raise TypeError('Function must not include *%s' % name)
            elif parameter.kind == inspect.Parameter.VAR_KEYWORD:
                hasKwargs= True
                optionalBindingsReprs.append('**%s' % name)
            else:
                if parameter.default == inspect.Parameter.empty:
                    coreBindings[name] = Missing
                else:
                    optionalBindings[name] = Missing
                    optionalBindingsReprs.append('%s=%s' % (name, parameter.default))
        doc = fnOrClass.__doc__ if hasattr(fnOrClass, '__doc__') else ''
        fnRepr = '%s(%s)' % (fnOrClass.__name__, ', '.join(list(coreBindings.keys()) + optionalBindingsReprs))
        answer = PipeableFunction(fnOrClass, coreBindings, len(coreBindings), optionalBindings, hasKwargs, overrideLHS, pipeOnly, leftToRight, rightToLeft, doc, fnRepr)
        return answer

    if len(args) == 1 and isinstance(args[0], (types.FunctionType, types.MethodType, type)):
        # of form @Pipeable so args[0] is the function or class being decorated
        return _DecorateWithPF(args[0])
    else:
        # of form as @Pipeable() or @Pipeable(overrideLHS=True) etc
        return _DecorateWithPF


class PipeableFunction(object):
    # PipeableFunction accumulates arguments via () ,<< or >>
    # when it has enough arguments it calls the wrapped function
    __slots__ = [
        '_fnOrClass', '_hasKwargs', '_overrideLHS', '_pipeOnly', '_leftToRight', '_rightToLeft',
        '_doc', '_coreBindings', '_optionalBindings', '_fnRepr', '_numAvailableCoreBindings'
    ]

    def __init__(self, fn, coreBindings, numAvailableCoreBindings, optionalBindings, hasKwargs, overrideLHS, pipeOnly, leftToRight, rightToLeft, doc, fnRepr):
        self._fnOrClass = fn
        self._coreBindings = coreBindings
        self._numAvailableCoreBindings = numAvailableCoreBindings
        self._optionalBindings = optionalBindings
        self._hasKwargs = hasKwargs
        self._overrideLHS = overrideLHS
        self._pipeOnly = pipeOnly
        self._leftToRight = leftToRight
        self._rightToLeft = rightToLeft
        self._doc = doc
        self._fnRepr = fnRepr

    def _copy(self) -> PipeableFunction:
        return PipeableFunction(
            self._fnOrClass,
            dict(self._coreBindings),
            self._numAvailableCoreBindings, 
            dict(self._optionalBindings),
            self._hasKwargs,
            self._overrideLHS,
            self._pipeOnly,
            self._leftToRight,
            self._rightToLeft,
            self._doc,
            self._fnRepr
        )

    def __repr__(self) -> str:
        # for pretty display in pycharm debugger
        return 'Pipeable=>%s' % self._fnRepr

    def __call__(self, *args, **kwargs) -> Any:
        """Appends args and kwargs to the list of arguments for the function and returns the result"""
        if self._pipeOnly:
            raise TypeError('Cannot add arguments to %s using ()' % self._fnOrClass.__name__)
        return self._bindAndCall(*args, **kwargs)

    def __rrshift__(self, lhs: Any) -> Any:
        # lhs >> self
        """Appends LHS to the list of arguments for the function and returns the result"""
        if not self._leftToRight:
            raise TypeError('Cannot add arguments to %s with >>' % self._fnOrClass.__name__)
        if isinstance(lhs, _Arg):
            return self._bindAndCall(lhs.arg)
        elif isinstance(lhs, _Args):
            return self._bindAndCall(*lhs.args)
        elif isinstance(lhs, _Kwargs):
            return self._bindAndCall(**lhs.kwargs)
        else:
            return self._bindAndCall(lhs)

    def __rshift__(self, rhs: Any) -> Any:
        # self >> rhs
        """Appends RHS to the list of arguments for the function and returns the result"""
        if isinstance(rhs, (PipeableFunction,)) and rhs._overrideLHS and rhs._leftToRight:
            return rhs.__rrshift__(self)
        else:
            if not self._leftToRight:
                raise TypeError('Cannot add arguments to %s with >>' % self._fnOrClass.__name__)
            if isinstance(rhs, _Arg):
                return self._bindAndCall(rhs.arg)
            elif isinstance(rhs, _Args):
                return self._bindAndCall(*rhs.args)
            elif isinstance(rhs, _Kwargs):
                return self._bindAndCall(**rhs.kwargs)
            else:
                return self._bindAndCall(rhs)

    def __rlshift__(self, lhs: Any) -> Any:
        # lhs << self
        """Appends LHS to the list of arguments for the function and returns the LHS"""
        if not self._rightToLeft:
            raise TypeError('Cannot add arguments to %s with <<' % self._fnOrClass.__name__)
        if self._numAvailableCoreBindings != 1:
            raise TypeError(
                'Can only call %s with << when there is only one available core binding. Currently there are %s' % (
                self._fnOrClass.__name__, self._numAvailableCoreBindings))
        self._bindAndCall(lhs)
        return lhs

    def __lshift__(self, rhs: Any) -> Any:
        # self << rhs
        """Appends RHS to the list of arguments for the function and returns the LHS (i.e. self)"""
        if isinstance(rhs, (PipeableFunction,)) and rhs._overrideLHS and rhs._rightToLeft:
            return rhs.__rrshift__(self)
        else:
            if not self._rightToLeft:
                raise TypeError('Cannot add arguments to %s with <<' % self._fnOrClass.__name__)
            if self._numAvailableCoreBindings != 1:
                raise TypeError(
                    'Can only call %s with << when there is only one available core binding. Current there are %s' % (
                    self._fnOrClass.__name__, self._numAvailableCoreBindings))
            self._bindAndCall(rhs)
            return self

    def _bindAndCall(self, *args, **kwargs):
        # _bindAndCall is slightly easier to step through in a debugger
        bindResult = self._bind(*args, **kwargs)
        if isinstance(bindResult, tuple):
            return self._fnOrClass(*bindResult[0], **bindResult[1])
        else:
            return bindResult


    def _bind(oldself, *args, **kwargs):
        self = oldself._copy()

        availableCoreBindings = {k: v for (k, v) in self._coreBindings.items() if (isinstance(v, _ELLIPSIS) or v is Missing)}
        availableOptionalBindings = {k: v for (k, v) in self._optionalBindings.items() if(isinstance(v, _ELLIPSIS) or v is Missing)}

        def filterAndSort(bindingItems):
            bindingItems = [(k,v) for (k,v) in bindingItems if isinstance(v, _ELLIPSIS)]
            bindingItems.sort(key=lambda x: x[1].id)
            return bindingItems
        coreBindingsWithEllipsis = filterAndSort(availableCoreBindings.items())
        optionalBindingsWithEllipsis = filterAndSort(availableOptionalBindings.items())

        # process each arg finding it a home
        addedArgEllipsis = False
        addedKwargEllipsis = False
        checkForEllipsis = True
        checkForMissing = True
        while args:
            arg = args[0]
            if arg is ...:
                arg = _ADDING_ELLIPSIS()
                addedArgEllipsis = True
            elif arg is na:
                arg = Missing
            if checkForEllipsis:
                # fill the _ELLIPSIS first
                checkForEllipsis = False
                if coreBindingsWithEllipsis:
                    name, v = coreBindingsWithEllipsis[0]
                    self._coreBindings[name] = arg
                    del availableCoreBindings[name]
                    del coreBindingsWithEllipsis[0]
                    checkForEllipsis = True
                    args = args[1:]
                    arg = _PROCESSED
                if arg is not _PROCESSED:
                    if optionalBindingsWithEllipsis:
                        name, v = optionalBindingsWithEllipsis[0]
                        self._optionalBindings[name] = arg
                        del availableOptionalBindings[name]
                        del optionalBindingsWithEllipsis[0]
                        checkForEllipsis = True
                        args = args[1:]
                        arg = _PROCESSED
                if arg is _PROCESSED:
                    continue
            if checkForMissing:
                # once the _ELLIPSIS have been exhausted fill the Missing
                checkForMissing = False
                for name, v in availableCoreBindings.items():
                    if v is Missing:
                        self._coreBindings[name] = arg
                        del availableCoreBindings[name]
                        checkForMissing = True
                        args = args[1:]
                        arg = _PROCESSED
                        break
                if arg is not _PROCESSED:
                    for name, v in availableOptionalBindings.items():
                        if v is Missing:
                            self._optionalBindings[name] = arg
                            del availableOptionalBindings[name]
                            checkForMissing = True
                            args = args[1:]
                            arg = _PROCESSED
                            break
                if arg is _PROCESSED:
                    continue
            if arg is not _PROCESSED:
                raise TypeError('%s>>Number of args passed in > number of unbound parameters' % self._fnRepr)

        # process each kwarg finding it a home
        for name, arg in kwargs.items():
            if arg is ...:
                arg = _ADDING_ELLIPSIS()
                addedKwargEllipsis = True
            if name in availableCoreBindings:
                coreValue = availableCoreBindings[name]
                if isinstance(coreValue, _ELLIPSIS) or coreValue is Missing:
                    self._coreBindings[name] = arg
                    del availableCoreBindings[name]
                    continue
            if name in availableOptionalBindings:
                optionalValue = availableOptionalBindings[name]
                if isinstance(optionalValue, _ELLIPSIS) or optionalValue is Missing:
                    self._optionalBindings[name] = arg
                    del availableOptionalBindings[name]
                    continue
            if self._hasKwargs:
                self._optionalBindings[name] = arg
                continue
            raise TypeError('%s>>No unbound parameter available for arg named "%s"' % (self._fnRepr, name))


        if addedArgEllipsis:
            if len(availableCoreBindings) > 0:
                raise TypeError('%s>>... - number of args passed in < number of unbound parameters' % self._fnRepr)

        if addedArgEllipsis or addedKwargEllipsis:
            for name, arg in self._coreBindings.items():
                if isinstance(arg, _ADDING_ELLIPSIS):
                    self._coreBindings[name] = _ELLIPSIS(arg.id)
            for name, arg in self._optionalBindings.items():
                if isinstance(arg, _ADDING_ELLIPSIS):
                    self._optionalBindings[name] = _ELLIPSIS(arg.id)

        self._numAvailableCoreBindings = len(availableCoreBindings) 
        if not (addedArgEllipsis or addedKwargEllipsis) and self._numAvailableCoreBindings == 0:
            return (
                list(self._coreBindings.values()),
                {k:v for k,v in self._optionalBindings.items() if v is not Missing}
            )
        else:
            return self



class _Arg(object):
    def __init__(self, arg):
        self.arg = arg

class _Args(object):
    def __init__(self, args):
        self.args = args

class _Kwargs(object):
    def __init__(self, kwargs):
        self.kwargs = kwargs


def arg(arg) -> _Arg:
    return _Arg(arg)

@Pipeable(overrideLHS=True)
def args(args) -> _Args:
    if not hasattr(args, '__iter__'):
        raise TypeError('The argument to args must be iterable')
    return _Args(args)

@Pipeable(overrideLHS=True)
def kwargs(kwargs) -> _Kwargs:
    if not isinstance(kwargs, collections.abc.Mapping):
        raise TypeError('The argument to kwargs must be a mapping')
    return _Kwargs(kwargs)



if not hasattr(sys, '_NA'):
    class _NA(object):
        # def __str__(self):
        #     return 'na'
        def __repr__(self):
            # for pretty display in pycharm debugger
            return 'na'
    sys._NA = _NA()
na = sys._NA


_ellipsisSeed = 0
class _ADDING_ELLIPSIS(object):
    def __init__(self):
        global _ellipsisSeed
        _ellipsisSeed += 1
        self.id = _ellipsisSeed
    # def __str__(self):
    #     return '_ADDING_ELLIPSIS'
    def __repr__(self):
        # for pretty display in pycharm debugger
        return '_ADDING_ELLIPSIS(%s)' % self.id

class _ELLIPSIS(object):
    def __init__(self, id):
        self.id = id
    def __repr__(self):
        # for pretty display in pycharm debugger
        return '_ELLIPSIS(%s)' % self.id

if not hasattr(sys, '_PROCESSED'):
    class _PROCESSED(object):
        # def __str__(self):
        #     return '_PROCESSED'
        def __repr__(self):
            # for pretty display in pycharm debugger
            return '_PROCESSED'
    sys._PROCESSED = _PROCESSED()
_PROCESSED = sys._PROCESSED

