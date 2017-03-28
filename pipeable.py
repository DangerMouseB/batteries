import types, inspect
_list_iter_type = type(iter([]))

# local imports
from . import Missing


__all__ = ['Pipeable', 'MoreArgsRequiredException']

# if we want to parameterise a function not in a left to right manner then we must specify those arguments as kwargs
# the >> (rshift) operator adds an argument to the list - when enough arguments are present then the actual function
# is executed else a new (more curried) function object is returned
# ignores default variables - instead the client will have to provide reduced interfaces if required

# TODO str -> <CurriedFunction Fred (b unbound) at 0xghste>

def Pipeable(*args, **kwargs):
    if len(args) == 1 and isinstance(args[0], (types.FunctionType, types.MethodType)):
        # called as @Pipeable
        # argNames = inspect.getargspec(args[0]).args
        argNames = list(inspect.signature(args[0]).parameters.keys())
        return _CurriedFunctionDecorator(args[0], argNames)
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


# TODO assert [1,2,3] >> ApplyEach >> Add(1) == [2,3,4]

