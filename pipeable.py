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
from . import Missing


__all__ = ['Pipeable', 'MoreArgsRequiredException', 'EachChained', 'Each']

# if we want to parameterise a function not in a left to right manner then we must specify those arguments as kwargs
# the >> (rshift) operator adds an argument to the list - when enough arguments are present then the actual function
# is executed else a new (more curried) function object is returned
# ignores default variables - instead the client will have to provide reduced interfaces if required

# TODO str -> <CurriedFunction Fred (b unbound) at 0xghste>

def Pipeable(*args, **kwargs):
    if len(args) == 1 and isinstance(args[0], (types.FunctionType, types.MethodType)):
        # called as @Pipeable
        try:
            # P3
            argNames = list(inspect.signature(args[0]).parameters.keys())
        except:
            # P2
            argSpec = inspect.getargspec(args[0])
            argNames = argSpec.args + ([argSpec.varargs] if argSpec.varargs else [])
        return _CurriedFunctionDecorator(args[0], argNames)
    else:
        raise SyntaxError('must not call Pipeable decorator')

class _CurriedFunctionDecorator(object):
    def __init__(self, fn, argNames):
        self._fn = fn
        self._argNames = argNames
    def __call__(self, *args, **kwargs):
        return _CurriedFunction(self._fn, self._argNames)(*args, **kwargs)
    def __rrshift__(self, lhs):
        # lhs >> self
        '''Appends LHS to the list of arguments for the function'''
        return _CurriedFunction(self._fn, self._argNames)(lhs)
    def __rshift__(self, rhs):
        # self >> rhs
        '''Appends RHS to the list of arguments for the function'''
        return _CurriedFunction(self._fn, self._argNames)(rhs)

class _CurriedFunction(object):
    def __init__(self, fn, argNames):
        self._fn = fn
        self._argNames = argNames
        self._accumulatedArgs = []
        self._accumulatedKwargs = {}
    def __call__(self, *args, **kwargs):
        return self._curry(*args, **kwargs)
    def __rrshift__(self, lhs):
        # lhs >> self
        return self._curry(lhs)
    def __rshift__(self, rhs):
        # self >> rhs
        return self._curry(rhs)

    def _curry(self, *args, **kwargs):
        allKwargs = dict(self._accumulatedKwargs)
        allKwargs.update(kwargs)
        allArgs = list(self._accumulatedArgs)
        allArgs.extend(args)
        numArgs = len(allArgs) + len(allKwargs)
        if numArgs < len(self._argNames):
            # return a new instance of myself with extra args or kwargs curried
            answer = _CurriedFunction(self._fn, self._argNames)
            answer._accumulatedKwargs = allKwargs
            answer._accumulatedArgs = allArgs
            return answer
        else:
            try:
                return self._fn(*self._argsAndKwargsAsArgs(allArgs, allKwargs))
            except MoreArgsRequiredException:
                answer = _CurriedFunction(self._fn, self._argNames)
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
        for argName in self._argNames:
            arg = kwargs.pop(argName, Missing)
            if arg is Missing:
                arg = args.pop(0)
            answer.append(arg)
        return answer + args

class MoreArgsRequiredException(Exception):
    pass


@Pipeable
def EachChained(x0, values, fn):
    x = x0
    for v in values:
        x = fn(x, v)
    return x


@Pipeable
def Each(values, fn):
    return [fn(v) for v in values]


