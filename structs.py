#************************************************************************************************************************************************
#
# Copyright 2017 David Briant
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#************************************************************************************************************************************************


# python imports
from collections import OrderedDict

# 3rd party imports
import numpy as np

# local imports
from .pipeable import Pipeable


__all__ = ['NaN', 'PoD', 'PoDGroup', 'NA', 'Absent', 'Sum', 'SumIgnoreAbsent', 'Avg', 'N']

NaN = float('nan')


@Pipeable
def Sum(summable):
    if isinstance(summable, PoD):
        return _Sum(list(summable))
    elif isinstance(summable, PoDGroup):
        return _Sum(summable._values)
    else:
        return np.sum(summable)

@Pipeable
def SumIgnoreAbsent(summable):
    if isinstance(summable, PoD):
        return _Sum(list(summable), True)
    elif isinstance(summable, PoDGroup):
        return _Sum(summable._values, True)
    else:
        return _Sum(summable, True)

def _Sum(values, ignoreAbsent=False):
    answer = NA
    if ignoreAbsent:
        for v in values:
            if v is not Absent:
                if answer is NA:
                    answer = v
                else:
                    answer += v
    else:
        for v in values:
            if answer is NA:
                answer = v
            else:
                answer += v
    return NA if answer is NA else 1.0 * answer


@Pipeable
def N(countable):
    if isinstance(countable, PoD):
        return _N(list(countable))
    elif isinstance(countable, PoDGroup):
        return _N(countable._values)
    else:
        return len(countable)

def _N(values, ignoreAbsent=False):
    answer = NA
    if ignoreAbsent:
        for v in values:
            if v is not Absent:
                if answer is NA:
                    if v is not NA:
                        answer = 1
                else:
                    if v is not NA:
                        answer += 1
    else:
        for v in values:
            if answer is NA:
                if v is not NA:
                    answer = 1
            else:
                if v is not NA:
                    answer += 1
    return answer


@Pipeable
def Avg(numberSequence):
    return Sum(numberSequence) / N(numberSequence)



class PoD(object):
    __slots__ = ['_dict']

    def __init__(self, *args, **kwargs):
        '''
        args are either sequence<pair<k, v>> or [PoD]
        could also allow pair<sequence<k>, sequence<v>> but for moment insist on PoD(*zip(ks, vs))
        kwargs may
            contain 'suppressRepr' which is a list of keys to suppress in the __repr__
            contain 'PoDType' which is it's display type
            be key value pairs - which has the side effect of being randomly ordered
                which can mess with the element wise arithmetic operators but allows PoD(name='Fred', age=10)
        '''
        _dict = OrderedDict()
        object.__setattr__(self, '_dict', _dict)
        _type = kwargs.pop('PoDType', None)
        if _type:
            _dict['_type'] = _type
        _dict['_suppressRepr'] = kwargs.pop('suppressRepr', [])
        if len(args) == 1 and isinstance(args[0], PoD):
            for k, v in args[0]._dict.items():
                _dict[k] = v
        else:
            for k, v in args:
                _dict[k] = v
        for k, v in kwargs.items():
            _dict[k] = v
            _dict['_unordered'] = True
        _dict['_seed'] = 0

    def Add(self, value):
        _dict = object.__getattribute__(self, '_dict')
        seed = _dict['_seed']
        if seed in _dict:
            raise ValueError('Appending would cause override of key in _dict')
        _dict[seed] = value
        _dict['_seed'] = seed + 1
        return value

    def __getattr__(self, name):
        _dict = object.__getattribute__(self, '_dict')
        if name == '_dict':
            return _dict
        else:
            return _dict.get(name, NA)

    def __setattr__(self, name, value):
        object.__getattribute__(self, '_dict')[name] = value

    def __delattr__(self, name):
        del object.__getattribute__(self, '_dict')[name]

    def __getitem__(self, name_or_name_and_type):
        # if the item is missing and a type is provided add a new instance of the type at key name and return the new instance
        _dict = object.__getattribute__(self, '_dict')
        if isinstance(name_or_name_and_type, tuple) and len(name_or_name_and_type) == 2:
            name, aType = name_or_name_and_type
            if isinstance(aType, type):
                value = _dict.get(name, NA)
                if value is NA:
                    _dict[name] = value = aType()
                return value
            if isinstance(aType, (int, float)):
                value = _dict.get(name, NA)
                if value is NA:
                    _dict[name] = value = aType
                return value
        return object.__getattribute__(self, '_dict').get(name_or_name_and_type, NA)

    def __setitem__(self, name, value):
        object.__getattribute__(self, '_dict')[name] = value

    def __delitem__(self, name):
        del object.__getattribute__(self, '_dict')[name]

    def __contains__(self, name):
        return name in object.__getattribute__(self, '_dict')

    def __len__(self):
        num_visible = 0
        for k in object.__getattribute__(self, '_dict').keys():
            if not isinstance(k, str):
                num_visible += 1
                continue
            else:
                if k[:1] != '_':
                    num_visible += 1
        return num_visible

    def __str__(self):
        _dict = object.__getattribute__(self, '_dict')
        suppressRepr = _dict['_suppressRepr']
        answer = _dict.get('_type', 'PoD') + '({key_value_pairs})'
        kv_pairs = []
        for k, v in _dict.items():
            if not isinstance(k, str) or k[:1] != '_':
                kv_pairs.append('%s=%s' % (str(k), ('...' if k in suppressRepr else str(v))))
        answer = answer.format(key_value_pairs=(' ' + ', '.join(kv_pairs) + ' ') if kv_pairs else '')
        return answer

    def __repr__(self):
        return self.__str__()

    def __iter__(self):
        # this allows PoD to feel like a list, i.e. grow a complex PoD without requiring a different type (e.g. PodGroup), e.g.
        # family = PoD()
        # family['people', PoD].Add(fred)
        # family.people.Add(joe)
        # for person in family.people:
        #     PP << person.name
        # we could easily insist on family['people', PoDGroup].Add(fred) or family.people = PodGroup()
        # but it feels like it breaks the flow of thought
        values = []
        for k, v in object.__getattribute__(self, '_dict').items():
            if isinstance(k, str) and k[:1] == '_':
                continue
            values.append(v)
        return values.__iter__()

    def KvIter(self):
        # this allows us to access the name value pairs of the PoD
        kvs = []
        _dict = object.__getattribute__(self, '_dict').items()
        for k, v in object.__getattribute__(self, '_dict').items():
            if isinstance(k, str) and k[:1] == '_':
                continue
            kvs.append((k, v))
        return kvs.__iter__()

    def __dir__(self):
        return [k for k in object.__getattribute__(self, '_dict').keys() if not isinstance(k, str) or k[:1] != '_']

    def __add__(self, other):
        # self + other
        _dict = object.__getattribute__(self, '_dict')
        answer = self.__class__()
        if isinstance(other, PoD):
            # otherDict = object.__getattribute__(other, '_dict')
            for (sk, sv), (ok, ov) in zip(self.KvIter(), other.KvIter()):
                if (sk != ok):
                    raise RuntimeError('sk != ok')
                answer[sk] = sv + ov
            return answer
        if isinstance(other, PoDGroup):
            for (sk, sv), ov in zip(self.KvIter(), other._values):
                answer[sk] = sv + ov
            return answer
        if isinstance(other, (list, tuple)):  # etc
            for (sk, sv), ov in zip(self.KvIter(), other):
                answer[sk] = sv + ov
            return answer
        if isinstance(other, (float, int)):
            for sk, sv in self.KvIter():
                answer[sk] = sv + other
            return answer
        else:
            return NotImplemented

    def __radd__(self, other):
        # other + self
        return self.__add__(other)

    def __sub__(self, other):
        # self - other
        _dict = object.__getattribute__(self, '_dict')
        answer = self.__class__()
        if isinstance(other, PoD):
            # otherDict = object.__getattribute__(other, '_dict')
            for (sk, sv), (ok, ov) in zip(self.KvIter(), other.KvIter()):
                if (sk != ok):
                    raise RuntimeError('sk != ok')
                answer[sk] = sv - ov
            return answer
        if isinstance(other, PoDGroup):
            for (sk, sv), ov in zip(self.KvIter(), other._values):
                answer[sk] = sv - ov
            return answer
        if isinstance(other, (list, tuple)):  # etc
            for (sk, sv), ov in zip(self.KvIter(), other):
                answer[sk] = sv - ov
            return answer
        if isinstance(other, (float, int)):
            for sk, sv in self.KvIter():
                answer[sk] = sv - other
            return answer
        else:
            return NotImplemented

    def __rsub__(self, other):
        # other - self
        _dict = object.__getattribute__(self, '_dict')
        answer = self.__class__()
        if isinstance(other, PoD):
            # otherDict = object.__getattribute__(other, '_dict')
            for (sk, sv), (ok, ov) in zip(self.KvIter(), other.KvIter()):
                if (sk != ok):
                    raise RuntimeError('sk != ok')
                answer[sk] = ov - sv
            return answer
        if isinstance(other, PoDGroup):
            for (sk, sv), ov in zip(self.KvIter(), other._values):
                answer[sk] = ov - sv
            return answer
        if isinstance(other, (list, tuple)):  # etc
            for (sk, sv), ov in zip(self.KvIter(), other):
                answer[sk] = ov - sv
            return answer
        if isinstance(other, (float, int)):
            for sk, sv in self.KvIter():
                answer[sk] = other - sv
            return answer
        else:
            return NotImplemented

    def __mul__(self, other):
        # self * other
        _dict = object.__getattribute__(self, '_dict')
        answer = self.__class__()
        if isinstance(other, PoD):
            # otherDict = object.__getattribute__(other, '_dict')
            for (sk, sv), (ok, ov) in zip(self.KvIter(), other.KvIter()):
                if (sk != ok):
                    raise RuntimeError('sk != ok')
                answer[sk] = sv * ov
            return answer
        if isinstance(other, PoDGroup):
            for (sk, sv), ov in zip(self.KvIter(), other._values):
                answer[sk] = sv * ov
            return answer
        if isinstance(other, (list, tuple)):  # etc
            for (sk, sv), ov in zip(self.KvIter(), other):
                answer[sk] = sv * ov
            return answer
        if isinstance(other, (float, int)):
            for sk, sv in self.KvIter():
                answer[sk] = sv * other
            return answer
        else:
            return NotImplemented

    def __rmul__(self, other):
        # other * self
        return self.__mul__(other)

    def __div__(self, other):
        # self / other
        #P2
        return self.__truediv__(other)

    def __rdiv__(self, other):
        # other / self
        # P2
        return self.__rtruediv__(other)

    def __truediv__(self, other):
        # self / other
        _dict = object.__getattribute__(self, '_dict')
        answer = self.__class__()
        if isinstance(other, PoD):
            # otherDict = object.__getattribute__(other, '_dict')
            for (sk, sv), (ok, ov) in zip(self.KvIter(), other.KvIter()):
                if (sk != ok):
                    raise RuntimeError('sk != ok')
                answer[sk] = sv / ov
            return answer
        if isinstance(other, PoDGroup):
            for (sk, sv), ov in zip(self.KvIter(), other._values):
                answer[sk] = sv / ov
            return answer
        if isinstance(other, (list, tuple)):  # etc
            for (sk, sv), ov in zip(self.KvIter(), other):
                answer[sk] = sv / ov
            return answer
        if isinstance(other, (float, int)):
            for sk, sv in self.KvIter():
                answer[sk] = sv / other
            return answer
        else:
            return NotImplemented

    def __rtruediv__(self, other):
        # other / self
        _dict = object.__getattribute__(self, '_dict')
        answer = self.__class__()
        if isinstance(other, PoD):
            # otherDict = object.__getattribute__(other, '_dict')
            for (sk, sv), (ok, ov) in zip(self.KvIter(), other.KvIter()):
                if (sk != ok):
                    raise RuntimeError('sk != ok')
                answer[sk] = ov / sv
            return answer
        if isinstance(other, PoDGroup):
            for (sk, sv), ov in zip(self.KvIter(), other._values):
                answer[sk] = ov / sv
            return answer
        if isinstance(other, (list, tuple)):  # etc
            for (sk, sv), ov in zip(self.KvIter(), other):
                answer[sk] = ov / sv
            return answer
        if isinstance(other, (float, int)):
            for sk, sv in self.KvIter():
                answer[sk] = other / sv
            return answer
        else:
            return NotImplemented



class PoDGroup(object):
    def __init__(self, values=None):
        self._values = [] if values is None else values

    def __str__(self):
        return "PoDGroup[ " + str(self._values) + " ]"

    def __repr__(self):
        return str(self)

    def __getattr__(self, name):
        return PoDGroup([getattr(e, name) for e in self._values])

    def __getitem__(self, name):
        return PoDGroup([getattr(e, name) for e in self._values])

    def __setitem__(self, name, value):
        raise NotImplementedError()

    def __delitem__(self, name):
        raise NotImplementedError()

    def __iter__(self):
        return self._values.__iter__()

    def __len__(self):
        size = 0
        for e in self._values:
            size += 0 if e is NA else 1
        return size

    def Add(self, element):
        self._values.append(element)
        return self

    def __lshift__(self, other):
        # self << other1 << other2
        self._values.append(other)
        return self

    def __add__(self, other):
        # self + other
        if isinstance(other, PoD):
            return NotImplemented
        if isinstance(other, PoDGroup):
            assert len(self._values) == len(other._values)
            return PoDGroup([s + o for o, s in zip(other._values, self._values)])
        if isinstance(other, (list, tuple)):  # etc
            assert len(self._values) == len(other._values)
            return PoDGroup([s + o for o, s in zip(other, self._values)])
        return PoDGroup([s + other for s in self._values])

    def __radd__(self, other):
        # other + self
        return self.__add__(other)

    def __sub__(self, other):
        # self - other
        if isinstance(other, PoD):
            return NotImplemented
        if isinstance(other, PoDGroup):
            assert len(self._values) == len(other._values)
            return PoDGroup([s - o for o, s in zip(other._values, self._values)])
        if isinstance(other, (list, tuple)):  # etc
            assert len(self._values) == len(other)
            return PoDGroup([s - o for o, s in zip(other, self._values)])
        return PoDGroup([s - other for s in self._values])

    def __rsub__(self, other):
        # other - self
        if isinstance(other, PoD):
            return NotImplemented
        if isinstance(other, PoDGroup):
            assert len(self._values) == len(other._values)
            return PoDGroup([o - s for o, s in zip(other._values, self._values)])
        if isinstance(other, (list, tuple)):  # etc
            assert len(self._values) == len(other)
            return PoDGroup([o - s for o, s in zip(other, self._values)])
        return PoDGroup([other - s for s in self._values])

    def __mul__(self, other):
        # self * other
        if isinstance(other, PoD):
            return NotImplemented
        if isinstance(other, PoDGroup):
            assert len(self._values) == len(other._values)
            return PoDGroup([s * o for o, s in zip(other._values, self._values)])
        if isinstance(other, (list, tuple)):  # etc
            assert len(self._values) == len(other)
            return PoDGroup([s * o for o, s in zip(other, self._values)])
        return PoDGroup([s * other for s in self._values])

    def __rmul__(self, other):
        # other * self
        return self.__mul__(other)

    def __div__(self, other):
        # self / other
        #P2
        return self.__truediv__(other)

    def __rdiv__(self, other):
        # other / self
        # P2
        return self.__rtruediv__(other)

    def __truediv__(self, other):
        # self / other
        if isinstance(other, PoD):
            return NotImplemented
        if isinstance(other, PoDGroup):
            assert len(self._values) == len(other._values)
            return PoDGroup([s / o for s, o in zip(self._values, other._values)])
        if isinstance(other, (list, tuple)):  # etc
            assert len(self._values) == len(other)
            return PoDGroup([s / o for s, o in zip(self._values, other)])
        return PoDGroup([s * other for s in self._values])

    def __rtruediv__(self, other):
        # other / self
        if isinstance(other, PoD):
            return NotImplemented
        if isinstance(other, PoDGroup):
            assert len(self._values) == len(other._values)
            return PoDGroup([o / s for s, o in zip(self._values, other._values)])
        if isinstance(other, (list, tuple)):  # etc
            assert len(self._values) == len(other)
            return PoDGroup([o / s for s, o in zip(self._values, other)])
        return PoDGroup([other / s for s in self._values])

    def Apply(self, fn):
        return PoDGroup([fn(s) for s in self._values])


class _AbsentClass(type):
    def __add__(cls, other):
        # cls + other
        if isinstance(other, PoDGroup):
            return NotImplemented
        return Absent

    def __radd__(cls, other):
        # other + cls
        if isinstance(other, PoDGroup):
            return NotImplemented
        return Absent

    def __sub__(cls, other):
        # cls - other
        if isinstance(other, PoDGroup):
            return NotImplemented
        return Absent

    def __rsub__(cls, other):
        # other - cls
        if isinstance(other, PoDGroup):
            return NotImplemented
        return Absent

    def __mul__(cls, other):
        # cls * other
        if isinstance(other, PoDGroup):
            return NotImplemented
        return Absent

    def __rmul__(cls, other):
        # other * cls
        if isinstance(other, PoDGroup):
            return NotImplemented
        return Absent

    def __div__(cls, other):
        # cls / other for P2
        return cls.__truediv__(other)

    def __rdiv__(cls, other):
        # other / cls for P2
        return cls.__rtruediv__(other)

    def __truediv__(cls, other):
        # cls / other
        if isinstance(other, PoDGroup):
            return NotImplemented
        return Absent

    def __rtruediv__(cls, other):
        # other / cls
        if isinstance(other, PoDGroup):
            return NotImplemented
        return Absent

    def __str__(cls):
        return 'Absent'

    def __repr__(cls):
        return 'Absent'

    def __call__(cls):
        return Absent


class Absent(object, metaclass=_AbsentClass):
    pass


class _NAClass(type):
    def __add__(cls, other):
        # cls + other
        if isinstance(other, PoDGroup):
            return NotImplemented
        return other

    def __radd__(cls, other):
        # other + cls
        if isinstance(other, PoDGroup):
            return NotImplemented
        return other

    def __sub__(cls, other):
        # cls - other
        if isinstance(other, PoDGroup):
            return NotImplemented
        return -1.0 * other

    def __rsub__(cls, other):
        # other - cls
        if isinstance(other, PoDGroup):
            return NotImplemented
        return other

    def __mul__(cls, other):
        # cls * other
        if isinstance(other, PoDGroup):
            return NotImplemented
        return NA

    def __rmul__(cls, other):
        # other * cls
        if isinstance(other, PoDGroup):
            return NotImplemented
        return NA

    def __div__(cls, other):
        # cls / other for P2
        return cls.__truediv__(other)

    def __rdiv__(cls, other):
        # other / cls for P2
        return cls.__rtruediv__(other)

    def __truediv__(cls, other):
        # cls / other
        if isinstance(other, PoDGroup):
            return NotImplemented
        return NA

    def __rtruediv__(cls, other):
        # other / cls
        if isinstance(other, PoDGroup):
            return NotImplemented
        elif other is NA:
            # NA / NA = NA
            return NA
        else:
            return NaN

    def __abs__(cls):
        return NA

    def __neg__(cls):
        return NA

    def __str__(cls):
        return 'NA'

    def __repr__(cls):
        return 'NA'

    def __call__(cls):
        return NA


class NA(object, metaclass=_NAClass):
    pass



