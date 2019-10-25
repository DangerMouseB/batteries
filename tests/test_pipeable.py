#*******************************************************************************
#
#    Copyright (c) 2017 David Briant
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


import sys
print(sys.path)


from ..pipeable import Pipeable, Apply, ApplyArgs, Each, EachArgs, Chain
from ..pmf_tools import Sequence
from ..testing import AssertRaises
import numpy as np


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

    assert Sequence(1, 3) >> Apply >> Update(b=1) == Sequence(2, 4)

    prior = 0
    likelihoods = Sequence(1, 3)
    assert likelihoods >> Chain(prior) >> Update == 6


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
    # the two caes in mind at the moment are
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

def main():
    test_Pipeable()
    test_consumesLHS()
    test_shape()
    print('pass')


if __name__ == '__main__':
    main()

