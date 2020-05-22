#*******************************************************************************
#
#    Copyright (c) 2019-2020 David Briant
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



from ..testing import AssertEqual, AssertRaises
from ..ranges import IndexableFR, ListOR, ChainAsSingleRange, RMap, Materialise
from ..range_interfaces import GetIRIter



def test_listRanges():
    r = IndexableFR([1,2,3])
    o = ListOR([])
    while not r.empty:
        o.put(r.front)
        r.popFront()
    r.indexable >> AssertEqual >> o.list

def test_rangeOrRanges():
    rOfR = [] >> ChainAsSingleRange
    [e for e in rOfR >> GetIRIter] >> AssertEqual >> []
    rOfR = (IndexableFR([]), IndexableFR([])) >> ChainAsSingleRange
    [e for e in rOfR >> GetIRIter] >> AssertEqual >> []
    rOfR = (IndexableFR([1]), IndexableFR([2])) >> ChainAsSingleRange
    [e for e in rOfR >> GetIRIter] >> AssertEqual >> [1,2]

def test_other():
    with AssertRaises(TypeError):
        [1, 2, 3] >> RMap(lambda x: x) >> Materialise >> AssertEqual >> [1, 2, 3]
    [1, 2, 3] >> RMap >> (lambda x: x) >> Materialise >> AssertEqual >> [1, 2, 3]

def main():
    test_listRanges()
    test_rangeOrRanges()
    test_other()
    print('pass')


if __name__ == '__main__':
    main()


