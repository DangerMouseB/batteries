#************************************************************************************************************************************************
#
#    Copyright (c) 2011-2012 David Briant - see https://github.com/DangerMouseB
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#************************************************************************************************************************************************

from batteries.timeseries import Timeseries, TimestampError, ObjectForAllTimeError
from batteries.testing import AssertRaises



def test_forAllTime():

    ts = Timeseries()
    assert len(ts) == 0

    ts[None] = 1
    assert len(ts) == 1
    assert ts[None] == 1
    assert ts[-1] == 1
    assert ts[0] == 1
    assert ts[1] == 1

    ts[None] = 2
    assert ts[None] == 2
    assert ts[-1] == 2
    assert ts[0] == 2
    assert ts[1] == 2

    with AssertRaises(ObjectForAllTimeError):
        ts[1] = 3

    with AssertRaises(ObjectForAllTimeError):
        del ts[1]

    del ts[None]
    assert len(ts) == 0

    ts[None] = 1
    assert len(ts) == 1
    ts.removeAll()
    assert len(ts) == 0

    ts[1]= 1
    with AssertRaises(ObjectForAllTimeError):
        ts[None] = 2


def test_setSeriesAndSingleAsOf():
    ts = Timeseries()
    assert len(ts) == 0

    objA = ('A',)
    ts[1] = objA
    assert len(ts) == 1
    assert ts.firstTS == 1
    assert ts.lastTS == 1
    with AssertRaises(TimestampError):
        ts[0]
    assert ts[1] == objA
    assert ts[2] == objA

    objB = ('B',)
    ts[2] = objB
    assert len(ts) == 2
    assert ts.firstTS == 1
    assert ts.lastTS == 2
    with AssertRaises(TimestampError):
        ts[0]
    assert ts[1] == objA
    assert ts[1.5] == objA
    assert ts[2] == objB
    assert ts[2.5] == objB


def test_del():
    ts = Timeseries()
    assert len(ts) == 0
    ts[1] = 'A'
    assert len(ts) == 1
    ts[2] = 'B'
    assert len(ts) == 2
    with AssertRaises(TimestampError):
        del ts[1.5]
    del ts[1]
    assert len(ts) == 1
    with AssertRaises(TimestampError):
        del ts[1]
    del ts[2]
    assert len(ts) == 0


def test_sliceAccess():
    ts = Timeseries()
    ts.addAll([1,3,7,8,9,10], [11,12,13,14,15,16])

    # test expected slice exceptions
    with AssertRaises(TimestampError):
        ts[0.5:1]       # t1 before first timestamp
    with AssertRaises(TimestampError):
        ts[0.5:]       # t1 before first timestamp
    with AssertRaises(TimestampError):
        ts[:0.5]       # t2 before first timestamp
    with AssertRaises(NotImplementedError):
        ts[slice(None, None, 1)]       # stride not handled (yet?)
    with AssertRaises(AssertionError):
        ts[-1:]         # negative t1 without t2
    with AssertRaises(AssertionError):
        ts[:-1]         # t2 before first timestamp
    with AssertRaises(AssertionError):
        ts[4:-3]        # negative t2


    # no ellipsis because python doesn't allow them in slice notation
    assert ts[4:3] == ([3,7,8], [12,13,14]), ts[4:3]
    assert ts[4:100] == ([3,7,8,9,10], [12,13,14,15,16]), ts[4:100]
    assert ts[9.5:1] == ([9], [15]), ts[9.5:1]
    assert ts[9.5:2] == ([9,10], [15,16]), ts[9.5:2]
    assert ts[9.5:] == ([9,10], [15,16]), ts[9.5:]

    assert ts[-100:4] == ([1,3], [11,12]), ts[-100:4]
    assert ts[-1:7.5] == ([7], [13])
    assert ts[-2:7.5] == ([3,7], [12,13])
    assert ts[-1:20] == ([10], [16])
    assert ts[:20] == ([1,3,7,8,9,10], [11,12,13,14,15,16])

    assert ts[:] == ([1,3,7,8,9,10], [11,12,13,14,15,16])

    # test expected tuple exceptions
    with AssertRaises(AssertionError):
        ts[-1,]
    with AssertRaises(AssertionError):
        ts[None,10]
    with AssertRaises(AssertionError):
        ts[1,None]
    with AssertRaises(AssertionError):
        ts[None,None]
    with AssertRaises(AssertionError):
        ts[-1,1]
    with AssertRaises(AssertionError):
        ts[1,-1]
    with AssertRaises(AssertionError):
        ts[5,1]
    with AssertRaises(TimestampError):
        ts[0.5,1]

    assert ts[1,2] == ([1], [11]), ts[1,2]
    assert ts[1,8.5] == ([1,3,7,8], [11,12,13,14]), ts[1,8.5]
    assert ts[1,20] == ([1,3,7,8,9,10], [11,12,13,14,15,16]), ts[1,20]
    assert ts[10,20] == ([10], [16]), ts[10,20]
    assert ts[20,20] == ([10], [16]), ts[20,20]

    assert ts[9.5,...] == ([9,10], [15,16]), ts[9.5,...]
    assert ts[...,20] == ([1,3,7,8,9,10], [11,12,13,14,15,16]), ts[...,20]
    assert ts[...,...] == ([1,3,7,8,9,10], [11,12,13,14,15,16]), ts[...,20]


    """
    ts[date1:100] - 100 elements asOf date1
    ts[-100:date2] 100 elements upto asOf date2
    ts[date1,date2] asOf date1 to asOf date2
    ts[:date2] - all up to
    ts[...:date2] - all up to
    ts[date1:] - asOf + remainder
    ts[date1:...] - asOf + remainder
    ts[date] - asOf
    ts[None] - last
    ts[-1] - last
    ts[0] - first
    ts.firstTS
    ts.lastTS

    asOf - > mode exact?
    date in ts - true if has exact date
    ts.get(date, something) - exact match, something if None else raise IndexError

    ts.timestamps[] etc



    """



def tdest_asOfJoin():
    assert False
    # create 2 timeseries
    # do a + (plus) operation



if __name__ == "__main__":
    test_sliceAccess()

