#*******************************************************************************
#
#    Copyright (c) 2011-2019 David Briant
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


# TODO resurect LambdaDict and IdentitySet for Python 3 if and when needed

class Collector(list):
    def __lshift__(self, other):
        # self << other
        self.append(other)
        return self


def concreteSlice(aSlice, sequenceSize):
    """Returns a new slice object with Nones and -x replaced with absolute indexes (assuming sequenceSize)"""
    start, stop, step = aSlice.start, aSlice.stop, aSlice.step
    if step is not None: raise NotImplementedError("step != None not implemented yet")
    if start is None:
        start = 0
    elif start < 0:
        start += sequenceSize
    if stop is None:
        stop = sequenceSize
    elif stop < 0:
        stop += sequenceSize
    if start > sequenceSize or stop > sequenceSize or start < 0 or stop < 0 or start > stop: 
        raise ValueError("old(%s, %s)=>new(%s, %s)" % (aSlice.start, aSlice.stop, start, stop))
    return slice(start, stop)
    
    
# class LambdaDictionary(DictMixin):
#
#     # level-1 definitions support higher levels
#
#     def __init__(self,lamb=None):
#         self._valuesMap = {}
#         self._keysMap = {}
#         if lamb is None:
#             self.lamb = lambda x: x
#         else:
#             self.lamb = lamb
#
#     def _keys(self):
#         return self._keysMap.keys()
#
#     def copy(self):
#         answer = self.__class__()
#         answer._dict = self._dict.copy()
#         answer._keysMap = self._keysMap.copy()
#         answer.lamb = self.lamb
#
#     def __getitem__(self, key):
#         privateKey = self.lamb(key)
#         value = self._valuesMap.get(privateKey, Missing)
#         if value is not Missing: return value
#         if hasattr(self.__class__, "__missing__"):
#             return self.__class__.__missing__(self, key)
#         raise KeyError(key)
#
#     def __setitem__(self, key, item):
#         privateKey = self.lamb(key)
#         self._keysMap[privateKey] = key
#         self._valuesMap[privateKey] = item
#
#     def __delitem__(self, key):
#         privateKey = self.lamb(key)
#         if privateKey not in self._keysMap: raise KeyError(key)
#         del self._valuesMap[privateKey]
#         del self._keysMap[privateKey]
#
#     def copy(self):
#         if self.__class__ is UserDict:
#             return UserDict(self.data.copy())
#         import copy
#         data = self.data
#         try:
#             self.data = {}
#             c = copy.copy(self)
#         finally:
#             self.data = data
#         c.update(self)
#         return c
#
#     def keys(self):
#         return self._keysMap.values()

"""
class SavedLambdaDictionary(DictMixin):

    # level-1 definitions support higher levels

    def __init__(self,lamb=None):
        self._dict = {}
        self._keysMap = {}
        if lamb is None:
            self.lamb = lambda x: x
        else:
            self.lamb = lamb

    def _keys(self):
        return self._keysMap.keys()

    def copy(self):
        answer = self.__class__()
        answer._dict = self._dict.copy()
        answer._keysMap = self._keysMap.copy()
        answer.lamb = self.lamb

    def __getitem__(self, key):
        privateKey = self.lamb(key)
        if privateKey in self._keysMap:
            return self._dict[self._keysMap[privateKey]]
        if hasattr(self.__class__, "__missing__"):
            return self.__class__.__missing__(self, key)
        raise KeyError(key)

    def __setitem__(self, key, item):
        privateKey = self.lamb(key)
        # check to see if the is a key corresponding to privateKey and if so remove it (more efficient to check to see if key is same and replace item?)
        if privateKey in self._keysMap: del self._dict[self._keysMap[privateKey]]
        self._keysMap[privateKey] = key
        self._dict[key] = item

    def __delitem__(self, key):
        privateKey = self.lamb(key)
        if privateKey not in self._keysMap: raise KeyError(key)
        del self._dict[self._keysMap[privateKey]]
        del self._keysMap[privateKey]

    def copy(self):
        if self.__class__ is UserDict:
            return UserDict(self.data.copy())
        import copy
        data = self.data
        try:
            self.data = {}
            c = copy.copy(self)
        finally:
            self.data = data
        c.update(self)
        return c

    def keys(self):
        return self._dict.keys()
"""

# class IdentitySet(object):
#     """A set that considers only object id() for uniqueness.
#
#     This strategy has edge cases for builtin types- it's possible to have
#     two 'foo' strings in one of these sets, for example.  Use sparingly.
#
#     """
#
#     _working_set = set
#
#     def __init__(self, iterable=None):
#         self._members = dict()
#         if iterable:
#             for o in iterable:
#                 self.add(o)
#
#     def add(self, value):
#         self._members[id(value)] = value
#
#     def __contains__(self, value):
#         return id(value) in self._members
#
#     def remove(self, value):
#         del self._members[id(value)]
#
#     def discard(self, value):
#         try:
#             self.remove(value)
#         except KeyError:
#             pass
#
#     def pop(self):
#         try:
#             pair = self._members.popitem()
#             return pair[1]
#         except KeyError:
#             raise KeyError('pop from an empty set')
#
#     def clear(self):
#         self._members.clear()
#
#     def __cmp__(self, other):
#         raise TypeError('cannot compare sets using cmp()')
#
#     def __eq__(self, other):
#         if isinstance(other, IdentitySet):
#             return self._members == other._members
#         else:
#             return False
#
#     def __ne__(self, other):
#         if isinstance(other, IdentitySet):
#             return self._members != other._members
#         else:
#             return True
#
#     def issubset(self, iterable):
#         other = type(self)(iterable)
#
#         if len(self) > len(other):
#             return False
#         for m in itertools.ifilterfalse(other._members.has_key,
#                                         self._members.iterkeys()):
#             return False
#         return True
#
#     def __le__(self, other):
#         if not isinstance(other, IdentitySet):
#             return NotImplemented
#         return self.issubset(other)
#
#     def __lt__(self, other):
#         if not isinstance(other, IdentitySet):
#             return NotImplemented
#         return len(self) < len(other) and self.issubset(other)
#
#     def issuperset(self, iterable):
#         other = type(self)(iterable)
#
#         if len(self) < len(other):
#             return False
#
#         for m in itertools.ifilterfalse(self._members.has_key,
#                                         other._members.iterkeys()):
#             return False
#         return True
#
#     def __ge__(self, other):
#         if not isinstance(other, IdentitySet):
#             return NotImplemented
#         return self.issuperset(other)
#
#     def __gt__(self, other):
#         if not isinstance(other, IdentitySet):
#             return NotImplemented
#         return len(self) > len(other) and self.issuperset(other)
#
#     def union(self, iterable):
#         result = type(self)()
#         # testlib.pragma exempt:__hash__
#         result._members.update(
#             self._working_set(self._member_id_tuples()).union(_iter_id(iterable)))
#         return result
#
#     def __or__(self, other):
#         if not isinstance(other, IdentitySet):
#             return NotImplemented
#         return self.union(other)
#
#     def update(self, iterable):
#         self._members = self.union(iterable)._members
#
#     def __ior__(self, other):
#         if not isinstance(other, IdentitySet):
#             return NotImplemented
#         self.update(other)
#         return self
#
#     def difference(self, iterable):
#         result = type(self)()
#         # testlib.pragma exempt:__hash__
#         result._members.update(
#             self._working_set(self._member_id_tuples()).difference(_iter_id(iterable)))
#         return result
#
#     def __sub__(self, other):
#         if not isinstance(other, IdentitySet):
#             return NotImplemented
#         return self.difference(other)
#
#     def difference_update(self, iterable):
#         self._members = self.difference(iterable)._members
#
#     def __isub__(self, other):
#         if not isinstance(other, IdentitySet):
#             return NotImplemented
#         self.difference_update(other)
#         return self
#
#     def intersection(self, iterable):
#         result = type(self)()
#         # testlib.pragma exempt:__hash__
#         result._members.update(
#             self._working_set(self._member_id_tuples()).intersection(_iter_id(iterable)))
#         return result
#
#     def __and__(self, other):
#         if not isinstance(other, IdentitySet):
#             return NotImplemented
#         return self.intersection(other)
#
#     def intersection_update(self, iterable):
#         self._members = self.intersection(iterable)._members
#
#     def __iand__(self, other):
#         if not isinstance(other, IdentitySet):
#             return NotImplemented
#         self.intersection_update(other)
#         return self
#
#     def symmetric_difference(self, iterable):
#         result = type(self)()
#         # testlib.pragma exempt:__hash__
#         result._members.update(
#             self._working_set(self._member_id_tuples()).symmetric_difference(_iter_id(iterable)))
#         return result
#
#     def _member_id_tuples(self):
#         return ((id(v), v) for v in self._members.itervalues())
#
#     def __xor__(self, other):
#         if not isinstance(other, IdentitySet):
#             return NotImplemented
#         return self.symmetric_difference(other)
#
#     def symmetric_difference_update(self, iterable):
#         self._members = self.symmetric_difference(iterable)._members
#
#     def __ixor__(self, other):
#         if not isinstance(other, IdentitySet):
#             return NotImplemented
#         self.symmetric_difference(other)
#         return self
#
#     def copy(self):
#         return type(self)(self._members.itervalues())
#
#     __copy__ = copy
#
#     def __len__(self):
#         return len(self._members)
#
#     def __iter__(self):
#         return self._members.itervalues()
#
#     def __hash__(self):
#         raise TypeError('set objects are unhashable')
#
#     def __repr__(self):
#         return '%s(%r)' % (type(self).__name__, self._members.values())