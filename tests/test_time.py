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

from batteries.time import xlFromGreg, gregFromXL, xlFromString, gregFromString, date, hhmmssusFromFloat, floatFromhhmmssus, MON, TUE, WED, THU, FRI, SAT, SUN, dayOnOrAfter
from batteries.testing import AssertRaises
from datetime import datetime

def test_ordinals():
    assert xlFromString("29/2/2012") == 40968, xlFromString("29/2/2012")
    assert gregFromString("29/2/2012") == 734562, gregFromString("29/2/2012")
    assert gregFromXL(40968) == 734562
    assert xlFromGreg(734562) == 40968
    
    
def test_timeComponents():
    assert hhmmssusFromFloat(0.5) == (12, 0, 0, 0)
    assert hhmmssusFromFloat(0.5 + 1.0 / 24.0 / 60.0) == (12, 1, 0, 0)
    assert hhmmssusFromFloat(0.5 + 1.0 / 24.0 / 60.0 / 60.0) == (12, 0, 1, 0)
    assert hhmmssusFromFloat(0.5 + 1.0 / 24.0 / 60.0 / 60.0 / 1000.0) == (12, 0, 0, 1000), hhmmssusFromFloat(0.5 + 1.0 / 24.0 / 60.0 / 60.0 / 1000.0)
    assert hhmmssusFromFloat(0.5 + 4.9 / 24.0 / 60.0 / 60.0 / 1000.0 / 10) == (12, 0, 0, 0)
    assert hhmmssusFromFloat(0.5 + 5.0 / 24.0 / 60.0 / 60.0 / 1000.0 / 10) == (12, 0, 0, 1000)
    assert hhmmssusFromFloat(floatFromhhmmssus(23, 59, 59, 999600)) == (24, 0, 0, 0), hhmmssusFromFloat(floatFromhhmmssus(23, 59, 59, 999.6))
    
def test_date():
    with AssertRaises(TypeError):
        d0 = date(1)
    with AssertRaises(TypeError):
        d0 = date("2012/2/29", "%Y/%m/%d")
    d1 = date("29/2/2012")
    result = d1.d, d1.m, d1.y, d1.hh, d1.mm, d1.ss, d1.us, d1.xl, d1.greg, d1.day
    assert result == (29, 2, 2012, 0, 0, 0, 0, 40968, 734562, WED), result
    d1 = date("2012/2/29", format="%Y/%m/%d")        
    result = d1.d, d1.m, d1.y, d1.hh, d1.mm, d1.ss, d1.us, d1.xl, d1.greg, d1.day
    assert result == (29, 2, 2012, 0, 0, 0, 0, 40968, 734562, WED), result
    d1 = date(xl=xlFromString("29/2/2012"))
    result = d1.d, d1.m, d1.y, d1.hh, d1.mm, d1.ss, d1.us, d1.xl, d1.greg, d1.day    
    assert result == (29, 2, 2012, 0, 0, 0, 0, 40968, 734562, WED), result
    d1 += 0.5
    assert (d1.hh, d1.mm, d1.ss, d1.us) == (12, 0, 0, 0)
    d1 -= date(ms=1)
    assert (d1.hh, d1.mm, d1.ss, d1.us) == (11, 59, 59, 999000)
    d2 = date(dt=datetime(2012, 2, 29))
    assert (d2.d, d2.m, d2.y, d2.hh, d2.mm, d2.ss, d2.us, d2.xl, d2.greg, d2.day) == (29, 2, 2012, 0, 0, 0, 0, 40968, 734562, WED)
    d3 = date(greg=734562)
    assert d2 == d3 and d2 is not d3
    d1 += 0.5 + date(ms=1)      # radd as well as add
    d3 += 1
    assert d1 == d3
    d3 -= 1
    d4 = d3.firstOfMonth
    result = (d4.day, d4.d, d4.m)
    assert result == (WED, 1, 2), result
    d5 = dayOnOrAfter(d4, THU)
    assert (d5.day, d5.d) == (THU, 2)
    d6 = d5 + date(m=1)
    assert (d6.d, d6.m) == (2, 3), (d6.d, d6.m)
    d1 = date("31/12/2010") + date(y=1,m=2)
    result = d1.d, d1.m, d1.y, d1.hh, d1.mm, d1.ss, d1.us, d1.xl, d1.greg, d1.day
    assert result == (29, 2, 2012, 0, 0, 0, 0, 40968, 734562, WED), result
    d7 = date("02/03/2011")
    d7 -= date(m=1)
    assert (d7.d, d7.m) == (2, 2), (d7.d, d7.m)
    d7 = date("01/03/2011")
    d7 -= date(m=3)
    assert (d7.d, d7.m, d7.y) == (1, 12, 2010), (d7.d, d7.m, d7.y)
    
    
    
if __name__ == '__main__':
    test_date()