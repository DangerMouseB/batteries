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

from ..wranglers import DataWrangler, WranglerException
from ..testing import AssertRaises



#TODO
# 1d lists
# enforce regular cubeness
# distinguish bewteen addSide += which is over loaded to be able to add elements and list of elements and addSide element to sid
# insertSide, removeSide


def dimsLike(a, b):
    if len(a) != len(b):
        return False
    return True


def test_appending2D():
    w = DataWrangler(nd=2)
    assert w.nd == 2
    with AssertRaises(WranglerException):
        w += 1          # 1D appending should not work on 2D lists
    with AssertRaises(WranglerException):
        w *= [1]          # 1D appending should not work on 2D lists
    with AssertRaises(WranglerException):
        w -= 1          # 1D preappending should not work on 2D lists
    with AssertRaises(WranglerException):
        w /= [1]          # 1D preappending should not work on 2D lists

    w.rows += [1,3]
    assert dimsLike(w._cols, [[1],[3]])
    w.rows += [2,4]
    assert dimsLike(w._cols, [[1,2],[3,4]])
    w.cols += [5,6]
    assert dimsLike(w._cols, [[1, 2], [3, 4], [5,6]])

    assert w.nRows == 2
    assert w.rows.n == 2
    with AssertRaises(NotImplementedError):
        assert w.d1.n == 2
    with AssertRaises(NotImplementedError):
        assert w.d[1].n == 2

    assert w.nCols == 3
    assert w.cols.n == 3
    with AssertRaises(NotImplementedError):
        assert w.d2.n == 3
    with AssertRaises(NotImplementedError):
        assert w.d[2].n == 3

    with AssertRaises(NotImplementedError):
        assert w.d.n == 2



def test_slicing():
    w = DataWrangler([[1,2],[3,4],[5,6]])
    assert w[0,:].list == [[1],[3],[5]]
    assert w.row[0] == 1



def main():
    test_appending2D()
    test_slicing()


if __name__ == '__main__':
    main()

