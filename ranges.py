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
from ._core import Null


if not hasattr(sys, '_EMPTY'):
    class _EMPTY(object):
        def __bool__(self):
            return False

        def __repr__(self):
            # for pretty display in pycharm debugger
            return 'EMPTY'
    sys._EMPTY = _EMPTY()
_EMPTY = sys._EMPTY


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
    def popFront(self) -> None:
        raise NotImplementedError()
    def moveFront(self) -> Any:
        raise NotImplementedError()

    # assignable
    @front.setter
    def front(self, value: Any) -> None:
        raise NotImplementedError()

    # python iterator interface
    # this is convenient but possibly too convenient and it may muddy things hence the ugly name
    @property
    def _GetIRIter(self):
        return IInputRange._Iter(self)

    class _Iter(object):
        def __init__(self, r):
            self.r = r
        def __iter__(self) -> IInputRange:
            return self
        def __next__(self) -> Any:
            if self.r.empty: raise StopIteration
            answer = self.r.front
            self.r.popFront()
            return answer

@Pipeable(leftToRight=True, pipeOnly=True)
def GetIRIter(r):
    # the name is deliberately semi-ugly to discourge but not prevent
    return r._GetIRIter


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
    # adapts a unary function (that takes a position index) into a forward range
    Empty = _EMPTY
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
class ChunkFROnChangeOf(IForwardRange):
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
        return ChunkFROnChangeOf(self.r.save(), self.f)
    def __repr__(self):
        return 'ChunkFROnChangeOf(%s,%s)' % (self.r, self.curF)

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
class Until(IForwardRange):
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
        return Until(self.r.save(), self.f)
    def __repr__(self):
        return 'Until(%s,%s)' % (self.r, self.f)


@Pipeable
class ChunkUsingSubRangeGenerator(IForwardRange):
    def __init__(self, f, r):
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
        new = ChunkUsingSubRangeGenerator(self.f, self.r.save())
        new.curSR = None if self.curSR is None else self.curSR.save()
        return new


@Pipeable
class IndexableFR(IForwardRange):
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
        new = IndexableFR(self.indexable.__class__(self.indexable))
        new.i = self.i
        return new


@Pipeable
class ListOR(IOutputRange):
    def __init__(self, list):
        self.list = list
    def put(self, value):
        self.list.append(value)


@Pipeable
class ChainAsSingleRange(IForwardRange):
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
class RMap(IForwardRange):
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
        return RMap(self.r.save(), self.f)


@Pipeable
class FileLineIR(IInputRange):
    def __init__(self, f, stripNL=False):
        self.f = f
        self.line = self.f.readline()
    @property
    def empty(self):
        return self.line == ''
    @property
    def front(self):
        return self.line
    def popFront(self):
        self.line = self.f.readline()


@Pipeable
class RRaggedZip(IInputRange):
    """As RZip but input ranges do not need to be of same length, shorter ranges are post padded with Null"""
    def __init__(self, ror):
        self.ror = ror
        self.allEmpty = ror >> AllSubRangesExhausted
    @property
    def empty(self):
        return self.allEmpty
    @property
    def front(self) -> list:
        parts = []
        ror = self.ror.save()
        while not ror.empty:
            subrange = ror.front
            if subrange.empty:
                parts.append(Null)
            else:
                parts.append(subrange.front)
            if not subrange.empty:
                subrange.popFront()
        return parts
    def popFront(self):
        ror = self.ror.save()
        self.allEmpty = True
        while not ror.empty:
            subrange = ror.front
            if not subrange.empty:
                subrange.popFront()
                if not subrange.empty:
                    self.allEmpty = False
            ror.popFront()


@Pipeable
def AllSubRangesExhausted(ror):
    ror = ror.save()
    answer = True
    while not ror.empty:
        if not ror.front.empty:
            answer = False
            break
    return answer

