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

from batteries.collections import LambdaDictionary, concreteSlice
from batteries.testing import ErrorTypeRaised


def test_concreteSlice():
    s = concreteSlice(slice(None), 5)
    assert (s.start, s.stop) == (0, 5)
    s = concreteSlice(slice(None,-1), 5)
    assert (s.start, s.stop) == (0, 4)
    s = concreteSlice(slice(1, None), 5)
    assert (s.start, s.stop) == (1, 5)
    s = concreteSlice(slice(1, -1), 5)
    assert (s.start, s.stop) == (1, 4)
    s = concreteSlice(slice(-4, -1), 5)
    assert (s.start, s.stop) == (1, 4)
    s = concreteSlice(slice(-5, -5), 5)
    assert (s.start, s.stop) == (0, 0)
    assert ErrorTypeRaised(concreteSlice, slice(-6, None), 5) == ValueError
    assert ErrorTypeRaised(concreteSlice, slice(None, 6), 5) == ValueError
    assert ErrorTypeRaised(concreteSlice, slice(5, 4), 5) == ValueError
    assert ErrorTypeRaised(concreteSlice, slice(-1, -2), 5) == ValueError
    

def test_LambdaDictionary1():
    fred = LambdaDictionary()
    fred.lamb = lambda x: x.upper()
    assert len(fred) == 0
    
    fred["hello"] = 1
    assert len(fred) == 1
    assert fred["HEllo"] == 1
    assert "heLLo" in fred
    assert " hello " not in fred
    assert "HELLO" not in fred.keys()
    assert "HELLO" in fred._keys()
    assert fred.items()[0][0] == "hello"
    fred["hello "] = 2
    assert len(fred) == 2
   
   
def test_LambdaDictionary2():
    fred = LambdaDictionary()
    fred.lamb = lambda x: x.replace(" ","").upper()
    assert len(fred) == 0
    
    fred["h ello "] = 1
    assert len(fred) == 1
    assert fred.keys() == ["h ello "], fred.keys()
    assert fred._keys() == ["HELLO"], fred._keys()
    assert fred["HEllo"] == 1
    assert fred.has_key(" h e L l O ")
    assert "heLLo" in fred
    assert " hello " in fred
    assert "HELLO" not in fred.keys()
    assert fred.items()[0][0] == "h ello "
    
    fred["Hello"] = 2
    assert len(fred) == 1
    assert "h ello " not in fred.keys()
    
    