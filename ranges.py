# *******************************************************************************
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
# *******************************************************************************


# d style ranges
# http://www.informit.com/articles/printerfriendly/1407357 - Andrei Alexandrescu
# https://www.drdobbs.com/architecture-and-design/component-programming-in-d/240008321 - Walter Bright


from __future__ import annotations

from batteries import Pipeable
from typing import Any, Union
import sys


class _EMPTY(object):
    def __bool__(self):
        return False
    def __repr__(self):
        # for pretty display in pycharm debugger
        return 'EMPTY'

if not hasattr(sys, '_EMPTY'):
    sys._EMPTY = _EMPTY()
EMPTY = sys._EMPTY


# empty - checks for end-of-input and fills a one-element buffer held inside the range object
# front - returns the buffer
# popFront() - sets an internal flag that tells empty to read the next element when called
# moveFront() - moves to the start

class IInputRange(object):
    @property
    def empty(self) -> bool:
        raise NotImplementedError()
    @property
    def front(self) -> Any:
        raise NotImplementedError()
    def moveFront(self) -> Any:
        raise NotImplementedError()
    def popFront(self) -> None:
        raise NotImplementedError()

    # assignable
    @front.setter
    def front(self, value: Any) -> None:
        raise NotImplementedError()

    # python iterator interface
    # this is convenient but possibly too convenient and it may muddy things hence the ugly name
    @property
    def _GetIter(self):
        return IInputRange._IterDelegator(self)

    class _IterDelegator(object):
        def __init__(self, r):
            self.r = r
        def __iter__(self) -> IInputRange:
            return self.r

    def __next__(self) -> Any:
        if self.empty: raise StopIteration
        answer = self.front
        self.popFront()
        return answer


class IForwardRange(IInputRange):
    def save(self) -> IForwardRange:
        raise NotImplementedError()


class IBidirectionalRange(IForwardRange):
    @property
    def back(self) -> Any:
        raise NotImplementedError()
    def moveBack(self) -> Any:
        raise NotImplementedError()
    def popBack(self) -> None:
        raise NotImplementedError()

    # assignable
    @back.setter
    def back(self, value: Any) -> None:
        raise NotImplementedError()


class IRandomAccessFinite(IBidirectionalRange):
    def moveAt(self, i: int) -> Any:
        raise NotImplementedError()
    def __getitem__(self, i: Union[int, slice]) -> Union[Any, IRandomAccessFinite]:
        raise NotImplementedError()
    @property
    def length(self) -> int:
        raise NotImplementedError()

    # assignable
    def __setitem__(self, i: int, value: Any) -> None:
        raise NotImplementedError()


class IRandomAccessInfinite(IForwardRange):
    def moveAt(self, i: int) -> Any:
        raise NotImplementedError()

    def __getitem__(self, i: int) -> Any:
        """Answers an element"""
        raise NotImplementedError()


class IOutputRange(object):
    def put(self, value: Any):
        """Answers void"""
        raise NotImplementedError()


class FnAdapterFRange(IForwardRange):
    # adpats a unary function (that takes a position index) into a forward range
    Empty = EMPTY
    def __init__(self, f):
        self.f = f
        self.i = 0
        self.current = self.f(self.i)
    @property
    def empty(self):
        return self.current == FnAdapterFRange.Empty
    @property
    def front(self):
        return self.current
    def popFront(self):
        self.i += 1
        if not self.empty:
            self.current = self.f(self.i)
    def save(self):
        new = FnAdapterFRange(self.f)
        new.i = self.i
        new.current = new.f(new.i)
        return  new
    def repr(self):
        return 'FnAdapterFRange(%s)[%s]' % (self.f, self.i)


@Pipeable
def ChunkUsing(r, f):
    return _ChunkUsingFR(r, f)

class _ChunkUsingFR(IForwardRange):
    def __init__(self, r, f):
        assert isinstance(r, IForwardRange)
        self.r = r
        self.f = f
        self.lastF = None if self.r.empty else self.f(self.r.front)
    @property
    def empty(self):
        return self.r.empty
    @property
    def front(self):
        assert not self.r.empty
        return _Chunk(self.r, self.f, self.lastF)
    def popFront(self):
        assert not self.r.empty
        while not self.r.empty and self.f(self.r.front) == self.lastF:
            self.r.popFront()
        if not self.r.empty:
            self.lastF = self.f(self.r.front)
    def save(self):
        return _ChunkUsingFR(self.r.save(), self.f)
    def __repr__(self):
        return '_ChunkUsingFR(%s,%s)' % (self.r, self.curF)

class _Chunk(IForwardRange):
    def __init__(self, r, f, curF):
        self.r = r
        self.f = f
        self.curF = curF
    @property
    def empty(self):
        return self.r.empty or self.curF != self.f(self.r.front)
    @property
    def front(self):
        return self.r.front
    def popFront(self):
        assert not self.r.empty
        self.r.popFront()
    def save(self):
        return _Chunk(self.r.save(), self.f, self.curF)
    def __repr__(self):
        return '_Chunk(%s)' % self.curF


@Pipeable
def Until(f, r):
    return _Until(r, f)

class _Until(IForwardRange):
    def __init__(self, r, f):
        if not isinstance(r, IForwardRange):
            raise TypeError(str(r))
        self.r = r
        self.f = f
        self.hasFound = False
    @property
    def empty(self):
        return self.r.empty or self.hasFound
    @property
    def front(self):
        assert not self.r.empty
        return self.r.front
    def popFront(self):
        assert not self.empty
        self.hasFound = self.f(self.r.front)
        self.r.popFront()

    def save(self):
        return _Until(self.r.save(), self.f)
    def __repr__(self):
        return '_Until(%s,%s)' % (self.r, self.f)


@Pipeable
def ChunkUsingSubRangeGenerator(f, r):
    return _ChunkUsingSubRangeGenerator(r, f)

class _ChunkUsingSubRangeGenerator(IForwardRange):
    def __init__(self, r, f):
        self.r = r
        self.f = f
        self.curSR = None if self.r.empty else self.f(self.r)
    @property
    def empty(self):
        return self.r.empty
    @property
    def front(self):
        assert not self.r.empty
        return self.curSR
    def popFront(self):
        self.curSR = None if self.r.empty else self.f(self.r)

    def save(self) -> IForwardRange:
        new = _ChunkUsingSubRangeGenerator(self.r.save(), self.f)
        new.curSR = None if self.curSR is None else self.curSR.save()
        return new


@Pipeable
def IndexableFR(indexable):
    return _IndexableForwardRange(indexable)

class _IndexableForwardRange(IForwardRange):
    def __init__(self, indexable):
        self.indexable = indexable
        self.i= 0
    @property
    def empty(self):
        return self.i >= len(self.indexable)
    @property
    def front(self):
        return self.indexable[self.i]
    def popFront(self):
        self.i += 1
    def save(self):
        new = _IndexableForwardRange(self.indexable.__class__(self.indexable))
        new.i = self.i
        return new


@Pipeable
def ListOR(l):
    return _ListOutputRange(l)

class _ListOutputRange(IOutputRange):
    def __init__(self, list):
        self.list = list
    def put(self, value):
        self.list.append(value)


@Pipeable
def ChainRanges(listOfRanges):
    return _RangeOfRanges(listOfRanges)

class _RangeOfRanges(IForwardRange):
    def __init__(self, listOfRanges):
        self.rOfR = listOfRanges >> IndexableFR
        if self.rOfR.empty:
            self.curR = None
        else:
            self.curR = self.rOfR.front
            self.rOfR.popFront()
    @property
    def empty(self):
        if self.curR is None: return True
        while self.curR.empty and not self.rOfR.empty:
            self.curR = self.rOfR.front
            self.rOfR.popFront()
        return self.curR.empty
    @property
    def front(self):
        assert not self.curR.empty
        return self.curR.front
    def popFront(self):
        if not self.curR.empty:
            self.curR.popFront()


@Pipeable
def Find(r, value):
    while not r.empty:
        if r.front == value:
            break
        r.popFront()
    return r

@Pipeable
def Front(r):
    return r.front

@Pipeable
def Back(r):
    return r.back

@Pipeable
def Length(r):
    return r.length

@Pipeable
def Empty(r):
    return r.empty

@Pipeable(rightToLeft=True, pipeOnly=True)
def PopFront(r):
    r.popFront()
    return r

@Pipeable(rightToLeft=True, pipeOnly=True)
def PopBack(r):
    r.popBack()
    return r

@Pipeable(leftToRight=True, pipeOnly=True)
def GetIter(r):
    # name is deliberately semi-ugly
    return r._GetIter


@Pipeable
def Materialise(r):
    answer = _MaterialisedRange()
    while not r.empty:
        e = r.front
        if isinstance(e, IInputRange) and not isinstance(e, IRandomAccessInfinite):
            answer.append(e >> Materialise)
            if not r.empty:  # the sub range may exhaust this range
                r.popFront()
        else:
            answer.append(e)
            r.popFront()
    return answer
class _MaterialisedRange(list):
    def __repr__(self):
        return 'MR' + super().__repr__()


# RMap rather than Map to make explicit that it is unrelated to python's map
@Pipeable
def RMap(r, f):
    return _RMap(r, f)
class _RMap(IForwardRange):
    def __init__(self, r, f):
        self.r = r
        self.f = f
    @property
    def empty(self):
        return self.r.empty
    @property
    def front(self):
        return self.f(self.r.front)
    def popFront(self):
        self.r.popFront()
    def save(self):
        return _RMap(self.r.save(), self.f)


@Pipeable
def RFold(r, f):
    raise NotImplementedError()


@Pipeable
def RFoldSeed(seed, r, f):
    raise NotImplementedError()


@Pipeable
def RFilter(r, f):
    raise NotImplementedError()

@Pipeable
def RTake(x):
    raise NotImplementedError()

@Pipeable
def RTakeBack(x):
    raise NotImplementedError()

@Pipeable
def RDrop(x):
    raise NotImplementedError()

@Pipeable
def RDropBack(x):
    raise NotImplementedError()


@Pipeable(leftToRight=True, pipeOnly=True)
def PushInto(inR, outR):
    while not inR.empty:
        outR.put(inR.front)
        inR.popFront()
    return outR

@Pipeable(rightToLeft=True)
def PullFrom(inR, outR):
    while not inR.empty:
        outR.put(inR.front)
        inR.popFront()
    return None

