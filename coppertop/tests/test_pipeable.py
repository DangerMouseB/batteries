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



from ..pipeable import Pipeable, arg, args, kwargs, na
from .._core import Missing
from .._testing import AssertRaises



def overview():
    # NB in python >> has higher precedence than ==, but in some
    # languages the pipe operator |> has low precedence


    # piping can be enabled on a function by
    @Pipeable
    def square(x):
        return x * x

    @Pipeable
    def toTuple(a, b, c, d=4):
        return (a, b, c, d)

    @Pipeable
    def div(x, y):
        return x / y

    @Pipeable
    def add(x, y):
        return x + y

    # arguments may be passed in the usual way
    assert square(9) == 81
    assert square(x=9) == 81

    # or they may be piped in
    assert 9 >> square == 81

    # unusually the pipeable function may consume arguments
    assert square >> 9 == 81

    # this is termed pacman munching (the function
    # is like pacman consuming argument to it's right)
    # and allows something similar to infix notation (although
    # without operator precedence)
    assert 5 >> add >> 5 >> div >> 2 == 5

    # in python () take precedence over >>
    assert 3 >> toTuple(1, 2) == (1, 2, 3, 4)
    assert toTuple(1, 2) >> 3== (1, 2, 3, 4)

    # defaulted arguments cannot be passed in positionally as the Pipeable wrapper calls the
    # wrapped function once it has enough non-defaulted arguments
    assert 3 >> toTuple(1, 2, d="oooOOOOo") == (1, 2, 3, "oooOOOOo")

    # ... can be used to specify where a piped argument is passed in
    assert 1 >> toTuple(..., 2, 3) == (1, 2, 3, 4)
    assert 2 >> toTuple(1, ..., 3) == (1, 2, 3, 4)

    # if multiple ... are used they are filled left to right in the order they occur in the function call rather than the function signature
    assert 1 >> toTuple(..., 2, ...) >> 3 == (1, 2, 3, 4)
    assert 3 >> toTuple(d=4, c=..., b=2, a=...) >> 1 == (1, 2, 3, 4)

    # partially bound pipeable can be used more than once
    add1 = add(..., 1)
    assert 1 >> add1 >> add1 >> add1 == 4

    # an iterable can be tagged as a sequence of arguments using "args"
    assert range(1, 3) >> args >> toTuple(..., ..., 3) == (1, 2, 3, 4)
    assert range(2, 4)  >> args >> toTuple(1) == (1, 2, 3, 4)

    # defaulted arguments maybe overridden using args
    assert range(4) >> args >> toTuple == (0, 1, 2, 3)

    # a dictionary can be tagged as keywords using "kwargs"
    assert dict(a=1, b=2) >> kwargs  >> toTuple(..., ..., 3) == (1, 2, 3, 4)

    # positional args cannot be overridden using "kwargs"
    with AssertRaises(TypeError):
        assert dict(a=1, b=2) >> kwargs >> toTuple(5, 4) >> 3 == (1, 2, 3, 4)

    # a LHS pipable may be consumed by a RHS pipeable allowing higher order functions to be created that can modify a pipeable on their left
    @Pipeable(overrideLHS=True)
    def applyTo(fn, xs):
        return [fn(x) for x in xs]
    assert add1 >> applyTo >> [1,2,3] == [2,3,4]
    def nonPipeableAddOn(x):
        return x + 1
    assert nonPipeableAddOn >> applyTo >> [1,2,3] == [2,3,4]

    @Pipeable
    def at(xs, i):
        return xs[i]

    # numpy arrays implement >> so must be wrapped first using arg(myNumpyArray) but it's not great so we'd have to not numpy.ndarrays
    # from any function that might be piped later
    try:
        import numpy
        assert (1 >> add >> arg(numpy.zeros(5)))[0] == 1
    except ModuleNotFoundError:
        pass

    # a pipeable can be called using () more than once
    assert toTuple(...,2,...,4)(1,3) == (1,2,3,4)

    # right to left pipeing can only be use when there is one argument left to be bound
    @Pipeable(leftToRight=True, rightToLeft=True)
    def fred(a, b):
        return a + b

    with AssertRaises(TypeError):
        fred << 1
    with AssertRaises(TypeError):
        1 << fred

    joe = 1 >> fred
    assert 2 << joe == 2
    assert joe << 2 is joe

    # can also wrap classes - the init method is parsed and when there are enough args an object is constructed
    @Pipeable
    class Fred(object):
        def __init__(self, n):
            self.n = n

    assert getattr(1 >> Fred, 'n') == 1

    @Pipeable
    def KwargsArePossible(a, b=1, **kwargs):
        answer = dict(a=a, b=b)
        answer.update(kwargs)
        return answer

    assert KwargsArePossible(0, c=2, d=3) == dict(a=0, b=1, c=2, d=3)



def test_Pipeable():
    @Pipeable
    def Joe(a, b):
        return a, b

    assert Joe(1) >> 2 == (1, 2)
    assert Joe >> 3 >> 4 == (3, 4)
    assert 5 >> Joe >> 6 == (5, 6)
    assert Joe(7, 8) == (7, 8)
    assert 10 >> Joe(9) == (9, 10)
    assert 11 >> Joe(b=12) == (11, 12)
    assert Joe(b=14) >> 13 == (13, 14)

    @Pipeable
    def Update(a, b):
        return a + b

    assert sequence(1, 3) >> Apply >> Update(b=1) == sequence(2, 4)

    prior = 0
    likelihoods = sequence(1, 3)
    assert likelihoods >> Chain(prior) >> Update == 6


def test_defaultArgs():
    @Pipeable
    def Fred(a, b, c=3):
        return a, b, c
    assert Fred(1,2) == (1,2,3)
    assert 2 >> Fred(1) == (1,2,3)
    assert 1 >> Fred(..., 2) == (1,2,3)
    assert 2 >> Fred(1, ..., c=3) == (1,2,3)
    assert 3 >> Fred(1, 2, c=...) == (1,2,3)
    assert 1 >> Fred(b=2) == (1,2,3)
    assert 2 >> Fred(a=1) == (1,2,3)
    (1,2) >> args >> Fred(...,...) == 1,2,3
    ((1,2), (4,5)) >> ApplyArgs(Fred(...,...))
    ((1,3), (1,4))  >> argsAll (listOfArgs=...) >> Fred(..., 2, c=...)
    (1,2) >> each >> Fred(...,2) == ((1,2,3),(2,2,3))
    Fred(..., 2) >> eachTo(fn=...) >> (1)
    Fred(..., 2) >> eachFrom >> (1,)
    Fred(..., 2) >> eachFrom >> (1,)

    assert 1 >> Fred >> 2 == (1, 2, 3)
    assert Fred(1) >> 2 == (1, 2, 3)
    assert Fred(1, b=2) == (1, 2, 3)
    with AssertRaises(Exception):
        1 >> Fred >> 2 >> 3

    assert 1 >> Fred(c=4) >> 2 == (1, 2, 4)
    assert Fred(1, c=4) >> 2 == (1, 2, 4)
    assert Fred(1, b=2, c=4) == (1, 2, 4)
    assert (4 >> Pipeable(lambda x, y: x + y) >> 5) == 9

def fred():
    @Pipeable
    def Cholesky(A):
        return numpy.linalg.cholesky(A)

    @Pipeable
    def _Identity(x):
        return x

    @Pipeable
    def _Sum(*args):
        return sum(args)

    @Pipeable
    def _Product(*args):
        answer = args[0]
        for x in args[1:]:
            answer *= x
        return answer


def test_consumesLHS():
    # the two cases in mind at the moment are
    # list >> Apply >> Fn - Apply calls Fn so not reversed
    # Fn >> Each >> list - Each calls Fn so is reversed

    assert ([1, 2, 3] >> Apply >> _Identity) == [1, 2, 3]
    assert ([[1,1], [2,2], [3,3]] >> ApplyArgs >> _Sum) == [2, 4, 6]

    assert (_Identity >> Each >> [1, 2, 3]) == [1, 2, 3]
    assert (_Sum >> EachArgs >> [[1,1], [2,2], [3,3]]) == [2, 4, 6]
    # `a`b ,' `c`d
    # [1,2,3] >> EachBoth(Sum) >> [1,2,3] == [2,4,6]

    # assert ((_Sum, _Product) >> Apply >> Over(1, [1,2,3])) == [7,6]

def test_shape():
    @Pipeable
    def Shape(x):
        return x.shape
    with AssertRaises(Exception):
        assert (np.zeros((1,2)) >> Shape) == (1,2)
    assert (Shape >> np.zeros((1, 2))) == (1, 2)

def test_numpy():
    rho = np.array((
        (1.00, 0.95, 0.80),
        (0.95, 1.00, 0.90),
        (0.80, 0.90, 1.00)
    ))
    # numpy implements nd.array >> rhs so can only call Pipeable >> np.ndarray unfortunately
    result = Cholesky >> rho
    assert isiinstance(result, np.ndarray)


def main():
    overview()
    print('pass')


if __name__ == '__main__':
    main()

