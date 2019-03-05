#************************************************************************************************************************************************
#
# Copyright 2017 David Briant
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
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


# python imports
import types, inspect


# local imports
from .missing import Missing


__all__ = ['Pipeable', 'MoreArgsRequiredException', 'Chain', 'Apply', 'Each', 'EachAll', 'Pipeables']

# if we want to parameterise a function not in a left to right manner then we must specify those arguments as kwargs
# the >> (rshift) operator adds an argument to the list - when enough arguments are present then the actual function
# is executed else a new (more curried) function object is returned
# ignores default variables - instead the client will have to provide reduced interfaces if required

# TODO str -> <CurriedFunction Fred (b unbound) at 0xghste>

def Pipeable(*args, **kwargs):
    minNumArgs = kwargs.get('minNumArgs', None)
    consumesLHS = kwargs.get('consumesLHS', False)
    def WrapFn(fn):
        try:
            # P3
            argNames = list(inspect.signature(fn).parameters.keys())
        except:
            # P2
            argSpec = inspect.getargspec(fn)
            argNames = argSpec.args + ([argSpec.varargs] if argSpec.varargs else [])
        return _CurriedFunctionDecorator(fn, argNames, len(argNames) if minNumArgs is None else minNumArgs, consumesLHS)
    if len(args) == 1 and isinstance(args[0], (types.FunctionType, types.MethodType)):
        # decorated as @Pipeable so args[0] is the function being wrapped
        return WrapFn(args[0])
    else:
        # decorated as @Pipeable() or @Pipeable(minNumArgs=2) etc
        return WrapFn

class _CurriedFunctionDecorator(object):
    def __init__(self, fn, argNames, minNumArgs, consumesLHS):
        self._fn = fn
        self._minNumArgs = minNumArgs
        self._consumesLHS = consumesLHS
        if hasattr(fn, '__doc__'):
            self._doc = fn.__doc__
        self._argNames = argNames
    def __call__(self, *args, **kwargs):
        return _CurriedFunction(self._fn, self._argNames, self._minNumArgs, self._consumesLHS)(*args, **kwargs)
    def __rrshift__(self, lhs):
        # lhs >> self
        '''Appends LHS to the list of arguments for the function'''
        return _CurriedFunction(self._fn, self._argNames, self._minNumArgs, self._consumesLHS)(lhs)
    def __rshift__(self, rhs):
        # self >> rhs
        '''Appends RHS to the list of arguments for the function'''
        if isinstance(rhs, (_CurriedFunction, _CurriedFunctionDecorator)) and rhs._consumesLHS:
            curriedMe = _CurriedFunction(self._fn, self._argNames, self._minNumArgs, self._consumesLHS)
            return rhs.__rrshift__(curriedMe)
        else:
            return _CurriedFunction(self._fn, self._argNames, self._minNumArgs, self._consumesLHS)(rhs)
    def __rlshift__(self, lhs):
        # lhs << self
        '''Appends LHS to the list of arguments for the function'''
        _CurriedFunction(self._fn, self._argNames, self._minNumArgs, self._consumesLHS)(lhs)
        return lhs
    def __lshift__(self, rhs):
        # self << rhs
        '''Appends RHS to the list of arguments for the function'''
        _CurriedFunction(self._fn, self._argNames, self._minNumArgs, self._consumesLHS)(rhs)
        return self

class _CurriedFunction(object):
    def __init__(self, fn, argNames, minNumArgs, consumesLHS):
        self._fn = fn
        self._minNumArgs = minNumArgs
        self._consumesLHS = consumesLHS
        if hasattr(fn, '__doc__'):
            self._doc = fn.__doc__
        self._argNames = argNames
        self._accumulatedArgs = []
        self._accumulatedKwargs = {}
    def __call__(self, *args, **kwargs):
        return self._curry(*args, **kwargs)
    def __rrshift__(self, lhs):
        # lhs >> self
        return self._curry(*[lhs])
    def __rshift__(self, rhs):
        # self >> rhs
        if isinstance(rhs, (_CurriedFunction, _CurriedFunctionDecorator)) and rhs._consumesLHS:
            return rhs.__rrshift__(self)
        else:
            return self._curry(*[rhs])

    def _curry(self, *args, **kwargs):
        allKwargs = dict(self._accumulatedKwargs)
        allKwargs.update(kwargs)
        allArgs = list(self._accumulatedArgs)
        allArgs.extend(args)
        numArgs = len(allArgs) + len(allKwargs)
        if numArgs < self._minNumArgs:
            # return a new instance of myself with extra args or kwargs curried
            answer = _CurriedFunction(self._fn, self._argNames, self._minNumArgs, self._consumesLHS)
            answer._accumulatedKwargs = allKwargs
            answer._accumulatedArgs = allArgs
            return answer
        else:
            try:
                return self._fn(*self._argsAndKwargsAsArgs(allArgs, allKwargs))
            except MoreArgsRequiredException:
                answer = _CurriedFunction(self._fn, self._argNames, self._minNumArgs, self._consumesLHS)
                answer._accumulatedKwargs = allKwargs
                answer._accumulatedArgs = allArgs
                return answer
            except TypeError:
                # TypeError: Joe() missing 1 required positional argument: 'a'
                # TypeError: Joe() takes 1 positional argument but 2 were given
                raise

    def _argsAndKwargsAsArgs(self, args, kwargs):
        args = list(args)
        answer = []
        for argName in self._argNames[0:self._minNumArgs]:
            arg = kwargs.pop(argName, Missing)
            if arg is Missing:
                arg = args.pop(0)
            answer.append(arg)
        return answer + args

class MoreArgsRequiredException(Exception):
    pass


@Pipeable
def Chain(x0, args, f):
    """Chain(x0, args, f)
    Answers xn where xi=f(xi-1, arg) for each arg in args"""
    xn = x0
    for arg in args:
        xn = f(xn, arg)
    return xn


@Pipeable
def Apply(xs, f):
    """Apply(xs, f)
    Answers [f(x) for x in xs]"""
    return [f(x) for x in xs]


@Pipeable(consumesLHS=True)
def Each(f, listOfArg):
    # much the same as Apply but conveys a subtly different relationship between the function and the list (more q llike)
    """Each(f, listOfArg)
    Answers [f(arg) for arg in listOfArg]"""
    return [f(arg) for arg in listOfArg]


@Pipeable(consumesLHS=True)
def EachAll(f, listOfArgs):
    """EachAll(f, listOfArgs)
    Answers [f(*arg) for arg in listOfArgs]"""
    return [f(*args) for args in listOfArgs]


@Pipeable
def Pipeables(arg):
    return sorted([k for k, v in arg.items() if isinstance(v, (_CurriedFunction, _CurriedFunctionDecorator))])



