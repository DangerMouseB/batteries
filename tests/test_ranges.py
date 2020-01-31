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



from ..testing import AssertEqual
from ..pipeable import Pipeable
from ..ranges import IndexableFR, ListOR, ChainRanges


def test_listRanges():
    r = IndexableFR([1,2,3])
    o = ListOR([])
    while not r.empty:
        o.put(r.front)
        r.popFront()
    r.l >> AssertEqual >> o.list

def test_rangeOrRanges():
    rOfR = [] >> ChainRanges
    [e for e in rOfR] >> AssertEqual >> []
    rOfR = (IndexableFR([]), IndexableFR([])) >> ChainRanges
    [e for e in rOfR] >> AssertEqual >> []
    rOfR = (IndexableFR([1]), IndexableFR([2])) >> ChainRanges
    [e for e in rOfR] >> AssertEqual >> [1,2]


def main():
    test_listRanges()
    test_rangeOrRanges()
    print('pass')


if __name__ == '__main__':
    main()



