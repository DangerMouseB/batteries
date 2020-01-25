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



import types, inspect, collections, sys
from .missing import Missing


__all__ = ['Pipeable', 'arg', 'args', 'kwargs', 'na']



def Pipeable(*args, overrideLHS=False, pipeOnly=False, leftToRight=Missing, rightToLeft=Missing):
    # overrideLHS allows a higher order function PF2 to override the behaviour of another PipeableFunction PF1
    # for PF1 >> PF2 or PF1 << PF2, i.e. execution order changes from PF1(), PF2() to PF2(), PF1()

    leftToRight, rightToLeft = (True, False) if (leftToRight is Missing and rightToLeft is Missing) else (leftToRight, rightToLeft)
    leftToRight = not rightToLeft if leftToRight is Missing else leftToRight
    rightToLeft = not leftToRight if rightToLeft is Missing else rightToLeft
    if leftToRight and rightToLeft:
        raise TypeError('Function cannot both pipe leftToRight (i.e. >>) and rightToLeft (i.e. <<)')

    def _DecorateWithPF(fn):
        coreBindings = {}
        optionalBindings = {}
        optionalBindingsReprs = []
        hasKwargs = False
        for name, parameter in inspect.signature(fn).parameters.items():
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
        if rightToLeft and len(coreBindings) != 1:
            raise TypeError('rightToLeft functions must have exactly one core (non-optional) argument')
        doc = fn.__doc__ if hasattr(fn, '__doc__') else ''
        fnRepr = '%s(%s)' % (fn.__name__, ', '.join(list(coreBindings.keys()) + optionalBindingsReprs))
        answer = PipeableFunction(fn, coreBindings, optionalBindings, hasKwargs, overrideLHS, pipeOnly, leftToRight, rightToLeft, doc, fnRepr)
        return answer

    if len(args) == 1 and isinstance(args[0], (types.FunctionType, types.MethodType)):
        # decorated as @Pipeable so args[0] is the function being wrapped
        return _DecorateWithPF(args[0])
    else:
        # decorated as @Pipeable() or @Pipeable(overrideLHS=True) etc
        return _DecorateWithPF


class PipeableFunction(object):
    # PipeableFunction accumulates arguments via () ,<< or >>
    # when it has enough arguments it calls the wrapped function
    __slots__ = [
        '_fn', '_hasKwargs', '_overrideLHS', '_pipeOnly', '_leftToRight', '_rightToLeft',
        '_doc', '_coreBindings', '_optionalBindings', '_fnRepr'
    ]

    def __init__(self, fn, coreBindings, optionalBindings, hasKwargs, overrideLHS, pipeOnly, leftToRight, rightToLeft, doc, fnRepr):
        self._fn = fn
        self._coreBindings = coreBindings
        self._optionalBindings = optionalBindings
        self._hasKwargs = hasKwargs
        self._overrideLHS = overrideLHS
        self._pipeOnly = pipeOnly
        self._leftToRight = leftToRight
        self._rightToLeft = rightToLeft
        self._doc = doc
        self._fnRepr = fnRepr

    def _copy(self):
        return PipeableFunction(
            self._fn,
            dict(self._coreBindings),
            dict(self._optionalBindings),
            self._hasKwargs,
            self._overrideLHS,
            self._pipeOnly,
            self._leftToRight,
            self._rightToLeft,
            self._doc,
            self._fnRepr
        )

    def __repr__(self):
        # for pretty display in pycharm debugger
        return 'Pipeable=>%s' % self._fnRepr

    def __call__(self, *args, **kwargs):
        """Appends args and kwargs to the list of arguments for the function and returns the result"""
        if self._pipeOnly:
            raise TypeError('Cannot add arguments to %s using ()' % self._fn.__name__)
        return self._bind(*args, **kwargs)

    def __rrshift__(self, lhs):
        # lhs >> self
        """Appends LHS to the list of arguments for the function and returns the result"""
        if not self._leftToRight:
            raise TypeError('Cannot add arguments to %s with >>' % self._fn.__name__)
        if isinstance(lhs, _Arg):
            return self._bind(lhs.arg)
        elif isinstance(lhs, _Args):
            return self._bind(*lhs.args)
        elif isinstance(lhs, _Kwargs):
            return self._bind(**lhs.kwargs)
        else:
            return self._bind(lhs)

    def __rshift__(self, rhs):
        # self >> rhs
        """Appends RHS to the list of arguments for the function and returns the result"""
        if isinstance(rhs, (PipeableFunction,)) and rhs._overrideLHS and rhs._leftToRight:
            return rhs.__rrshift__(self)
        else:
            if not self._leftToRight:
                raise TypeError('Cannot add arguments to %s with >>' % self._fn.__name__)
            if isinstance(rhs, _Arg):
                return self._bind(rhs.arg)
            elif isinstance(rhs, _Args):
                return self._bind(*rhs.args)
            elif isinstance(rhs, _Kwargs):
                return self._bind(**rhs.kwargs)
            else:
                return self._bind(rhs)

    def __rlshift__(self, lhs):
        # lhs << self
        """Appends LHS to the list of arguments for the function and returns the LHS"""
        if not self._rightToLeft:
            raise TypeError('Cannot add arguments to %s with <<' % self._fn.__name__)
        self._bind(lhs)
        return lhs

    def __lshift__(self, rhs):
        # self << rhs
        """Appends RHS to the list of arguments for the function and returns the LHS (i.e. self)"""
        if isinstance(rhs, (PipeableFunction,)) and rhs._overrideLHS and rhs._rightToLeft:
            return rhs.__rrshift__(self)
        else:
            if not self._rightToLeft:
                raise TypeError('Cannot add arguments to %s with <<' % self._fn.__name__)
            self._bind(rhs)
            return self

    def _bind(oldself, *args, **kwargs):
        self = oldself._copy()

        availableCoreBindings = {k: v for (k, v) in self._coreBindings.items() if (isinstance(v, ELLIPSIS) or v is Missing)}
        availableOptionalBindings = {k: v for (k, v) in self._optionalBindings.items() if(isinstance(v, ELLIPSIS) or v is Missing)}

        def filterAndSort(bindingItems):
            bindingItems = [(k,v) for (k,v) in bindingItems if isinstance(v, ELLIPSIS)]
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
                arg = ADDING_ELLIPSIS()
                addedArgEllipsis = True
            elif arg is na:
                arg = Missing
            if checkForEllipsis:
                # fill the ELLIPSIS first
                checkForEllipsis = False
                if coreBindingsWithEllipsis:
                    name, v = coreBindingsWithEllipsis[0]
                    self._coreBindings[name] = arg
                    del availableCoreBindings[name]
                    del coreBindingsWithEllipsis[0]
                    checkForEllipsis = True
                    args = args[1:]
                    arg = PROCESSED
                if arg is not PROCESSED:
                    if optionalBindingsWithEllipsis:
                        name, v = optionalBindingsWithEllipsis[0]
                        self._optionalBindings[name] = arg
                        del availableOptionalBindings[name]
                        del optionalBindingsWithEllipsis[0]
                        checkForEllipsis = True
                        args = args[1:]
                        arg = PROCESSED
                if arg is PROCESSED:
                    continue
            if checkForMissing:
                # once the ELLIPSIS have been exhausted fill the Missing
                checkForMissing = False
                for name, v in availableCoreBindings.items():
                    if v is Missing:
                        self._coreBindings[name] = arg
                        del availableCoreBindings[name]
                        checkForMissing = True
                        args = args[1:]
                        arg = PROCESSED
                        break
                if arg is not PROCESSED:
                    for name, v in availableOptionalBindings.items():
                        if v is Missing:
                            self._optionalBindings[name] = arg
                            del availableOptionalBindings[name]
                            checkForMissing = True
                            args = args[1:]
                            arg = PROCESSED
                            break
                if arg is PROCESSED:
                    continue
            if arg is not PROCESSED:
                raise TypeError('Number of args passed in > number of unbound parameters')

        # process each kwarg finding it a home
        for name, arg in kwargs.items():
            if arg is ...:
                arg = ADDING_ELLIPSIS()
                addedKwargEllipsis = True
            if name in availableCoreBindings:
                coreValue = availableCoreBindings[name]
                if isinstance(coreValue, ELLIPSIS) or coreValue is Missing:
                    self._coreBindings[name] = arg
                    del availableCoreBindings[name]
                    continue
            if name in availableOptionalBindings:
                optionalValue = availableOptionalBindings[name]
                if isinstance(optionalValue, ELLIPSIS) or optionalValue is Missing:
                    self._optionalBindings[name] = arg
                    del availableOptionalBindings[name]
                    continue
            if self._hasKwargs:
                self._optionalBindings[name] = arg
                continue
            raise TypeError('No unbound parameter available for arg named "%s"' % name)


        if addedArgEllipsis:
            if len(availableCoreBindings) > 0:
                raise TypeError('... - number of args passed in < number of unbound parameters')

        if addedArgEllipsis or addedKwargEllipsis:
            for name, arg in self._coreBindings.items():
                if isinstance(arg, ADDING_ELLIPSIS):
                    self._coreBindings[name] = ELLIPSIS(arg.id)
            for name, arg in self._optionalBindings.items():
                if isinstance(arg, ADDING_ELLIPSIS):
                    self._optionalBindings[name] = ELLIPSIS(arg.id)

        if not (addedArgEllipsis or addedKwargEllipsis) and len(availableCoreBindings) == 0:
            return self._fn(
                *list(self._coreBindings.values()),
                **{k:v for k,v in self._optionalBindings.items() if v is not Missing})
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


def arg(arg):
    return _Arg(arg)

@Pipeable(overrideLHS=True)
def args(args):
    if not hasattr(args, '__iter__'):
        raise TypeError('The argument to args must be iterable')
    return _Args(args)

@Pipeable(overrideLHS=True)
def kwargs(kwargs):
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
class ADDING_ELLIPSIS(object):
    def __init__(self):
        global _ellipsisSeed
        _ellipsisSeed += 1
        self.id = _ellipsisSeed
    # def __str__(self):
    #     return 'ADDING_ELLIPSIS'
    def __repr__(self):
        # for pretty display in pycharm debugger
        return 'ADDING_ELLIPSIS(%s)' % self.id

class ELLIPSIS(object):
    def __init__(self, id):
        self.id = id
    def __repr__(self):
        # for pretty display in pycharm debugger
        return 'ELLIPSIS(%s)' % self.id

if not hasattr(sys, '_PROCESSED'):
    class _PROCESSED(object):
        # def __str__(self):
        #     return 'PROCESSED'
        def __repr__(self):
            # for pretty display in pycharm debugger
            return 'PROCESSED'
    sys._PROCESSED = _PROCESSED()
PROCESSED = sys._PROCESSED

