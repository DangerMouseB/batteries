#*******************************************************************************
#
#    Copyright (c) 2011-2012 David Briant
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
    
    