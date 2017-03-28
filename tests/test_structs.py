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


from batteries_bakup.structs import  PoD, PoDGroup, NA, Absent, NaN
from batteries_bakup.stats import Sum, N, Avg


def TestPoDAsColumn():
    # PoD as column
    a = PoD()
    p = 2
    a.D4 = p
    a.D6 = p
    a.D8 = p
    a.D10 = p
    a.D12 = p
    a.D20 = p
    assert list(1 + a + 1) == [1 + p + 1] * 6
    assert list(a + a) == [p + p] * 6
    assert list(([1] * 6) + a + ([1] * 6)) == [1 + p + 1] * 6
    assert list(PoDGroup([1] * 6) + a + PoDGroup([1] * 6)) == [1 + p + 1] * 6

    assert list(1 - a - 1) == [1 - p - 1] * 6
    assert list(a - a) == [p - p] * 6
    assert list(([1] * 6) - a - ([1] * 6)) == [1 - p - 1] * 6
    assert list(PoDGroup([1] * 6) - a - PoDGroup([1] * 6)) == [1 - p - 1] * 6

    assert list(2 * a * 2) == [2 * p * 2] * 6
    assert list(a * a) == [p * p] * 6
    assert list(([2] * 6)  * a * ([2] * 6)) == [2 * p * 2] * 6
    assert list(PoDGroup([2] * 6) * a * PoDGroup([2] * 6)) == [2 * p * 2] * 6

    assert list(4 / a / 2) == [4 / p / 2] * 6
    assert list(a / a) == [p / p] * 6
    assert list(([4] * 6)  / a / ([2] * 6)) == [4 / p / 2] * 6
    assert list(PoDGroup([4] * 6) / a / PoDGroup([2] * 6)) == [4 / p / 2] * 6

    assert a >> Sum == 12
    assert a >> N == 6
    assert a >> Avg == 2


def another_test():
    a = PoD()
    a.size = 10
    a.price1 = 5
    a.client = 'a'
    b = PoD()
    b.size = 4
    b.price = 10
    b.client = 'a'
    c = PoD()
    c.size = 10
    c.price = 3
    c.client = 'b'

    t = PoDGroup([a, b, c])
    assert (t.size * 2)._values == [20, 8, 20]
    assert sum(t.size * t.price) == 70

    assert NA * 1 is NA
    assert NA + 1 is 1

    a.price = 5
    assert t.size >> Sum == 24
    assert t.size >> Avg == 8
    (t.size * t.price) >> Avg == 40


def test_PoDGroup():
    assert PoDGroup([NA, 1]) >> Sum == 1

    assert (1 + PoDGroup([1, 2]) + 1)._values == [3, 4]  # Single + Group
    assert (PoDGroup([1, 2]) + PoDGroup([1, 2]))._values == [2, 4]  # Group + Group
    assert (Absent + PoDGroup([1, 2]) + Absent)._values == [Absent, Absent]  # Absent (Single) + Group
    assert (1 + PoDGroup([1, Absent]) + 1)._values == [3, Absent]  # Group with Absent + Single

    assert (0 * PoDGroup([1, 2]) * 1)._values == [0, 0]  # Single + Group
    assert (PoDGroup([1, 2]) * PoDGroup([1, 2]))._values == [1, 4]  # Group + Group

    a = PoD()
    a.asset = 'Gold'
    a.size = 10
    a.entry = 5
    a.client = 'a'

    b = PoD()
    b.asset = 'Silver'
    b.size = -5
    b.entry = 8
    b.client = 'a'

    markPx = 6
    g1 = PoDGroup([e for e in [a, b] if e.size != 0])
    g2 = PoDGroup()

    assert len(g1) == 2
    assert len(g2) == 0

    c = PoD()
    c.asset = 'Rock'
    c.size = -5
    c.entry = 8
    c.client = 'b'

    d = PoD()
    d.asset = 'Paper'
    d.size = -5
    d.entry = Absent
    d.client = 'b'

    g3 = PoDGroup([a, b, c, d])
    gg1 = g3.GroupBy.client
    assert len(gg1) == 1
    assert gg1.GroupedBy == 'client'
    assert len(gg1.a) == 2

    gg2 = g3.GroupBy('asset', ('Gold', 'Silver', 'LiveCattle'))
    assert len(gg2) == 3
    assert len(gg2.LiveCattle) == 0
    actual_result = []
    for key, subgroup in gg2.GroupItems:
        assert subgroup == gg2[key]
        actual_result.append([key, len(subgroup), (subgroup.size * subgroup.price) >> Sum])
    expected_result = [
        ['Gold', 1, 50],
        ['Silver', 1, -40],
        ['LiveCattle', 0, NA],
        #[AllOthers, 2, Absent]
    ]
    assert actual_result == expected_result


def test_PoD():
    a = PoD()
    a.a = 1
    assert len(a) == 1
    assert a.b is NA
    a._a = 0
    assert len(a) == 1
    assert str(a) == 'PoD( a=1 )'
    assert repr(a) == 'PoD( a=1 )'
    assert dir(a) == ['a']
    assert list([_ for _ in a]) == [1]
    a = PoD(PoDType='A')
    a.a = 1
    a.b = 1
    a._a = 0
    assert str(a) == 'A( a=1, b=1 )'
    assert repr(a) == 'A( a=1, b=1 )'
    assert dir(a) == ['a', 'b']
    assert list([_ for _ in a]) == [1, 1]
    a.Add('2')
    assert str(a) == 'A( a=1, b=1, 0=2 )'
    a.longStuff = 'fred'
    a._suppressRepr.append('longStuff')
    assert str(a) == 'A( a=1, b=1, 0=2, longStuff=... )'
    assert len(a) == 4


def test_Singles():
    assert NA is NA
    assert NA == NA
    assert 1 + NA + 0 == 1
    assert 1 - NA - 1 == 0
    assert 1 * NA * 0 is NA
    assert NA / 1 is NA
    assert 1 / NA is NaN
    assert NA / NA is NA
    assert abs(NA) is NA
    assert (-NA) is NA


test_PoD()
test_Singles()
another_test()
TestPoDAsColumn()
#test_PoDGroup()  # not implemented yet


print("pass")