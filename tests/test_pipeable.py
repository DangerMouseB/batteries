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
import numpy as np


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

    # numpy arrays implement >> so must be wrapped first using arg(myNumpyArray) but it's not great so we'd have to not np.ndarrays
    # from any function that might be piped later
    assert (1 >> add >> arg(np.zeros(5)))[0] == 1

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


def main():
    overview()
    print('pass')


if __name__ == '__main__':
    main()

