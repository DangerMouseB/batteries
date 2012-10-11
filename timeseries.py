from types import NoneType, SliceType
from bisect import bisect_left, bisect_right
from testing import close


class TimestampError(LookupError):
    def __int__(self, *args, **kwargs):
        LookupError.__init__(self, *args, **kwargs)


class ObjectForAllTimeError(RuntimeError):
    def __int__(self, *args, **kwargs):
        RuntimeError.__init__(self, *args, **kwargs)



class Timeseries(object):

    def __init__(self):
        self._timestamps = None
        self._values = None

    def __len__(self):
        if self._timestamps:
            return len(self._timestamps)
        elif self._values:
            return 1
        else:
            return 0

    def __getitem__(self, t):
        if self._timestamps is None:
            if self._values is not None:
                if type(t) in (SliceType,):
                    return [self._values]
                else:
                    return self._values
            raise TimestampError("No value for %s" % t)
        else:
            if type(t) in (int, float):
                iRHS = bisect_right(self._timestamps, t)
                if iRHS == 0: raise TimestampError("Timestamp before first timestamp")
                return self._values[iRHS - 1]
            else:
                if type(t) == SliceType:
                    if t.step is not None: raise NotImplementedError("(<slice>t).step is not None")
                    if t.start is None and t.stop is not None:
                        assert t.stop > 0
                        iRHS = bisect_right(self._timestamps, t.stop)
                        if iRHS == 0: raise TimestampError("t.start before first timestamp")
                        i2 = iRHS
                        return (self._timestamps[:i2], self._values[:i2])
                    elif t.start is not None and t.stop is None:
                        assert t.start > 0
                        iRHS = bisect_right(self._timestamps, t.start)
                        if iRHS == 0: raise TimestampError("t.start before first timestamp")
                        i1 = iRHS - 1
                        return (self._timestamps[i1:], self._values[i1:])
                    elif t.start is not None and t.stop is not None:
                        assert type(t.start) in (int, float)
                        assert type(t.stop) in (int, float)
                        if t.start < 0:
                            assert t.stop > 0
                            iRHS = bisect_right(self._timestamps, t.stop)
                            if iRHS == 0: raise TimestampError("t.start before first timestamp")
                            i2 = iRHS
                            i1 = max(0, i2 + t.start)
                            return (self._timestamps[i1:i2], self._values[i1:i2])
                        else:
                            assert t.stop > 0
                            iRHS = bisect_right(self._timestamps, t.start)
                            if iRHS == 0: raise TimestampError("t.start before first timestamp")
                            i1 = iRHS - 1
                            i2 = i1 + t.stop
                            return (self._timestamps[i1:i2], self._values[i1:i2])
                    else:
                        return (list(self._timestamps), list(self._values))
                else:
                    assert len(t) == 2
                    assert t[0] is not None
                    assert t[1] is not None
                    t = slice(t[0], t[1])
                    if t.start is Ellipsis and t.stop is not Ellipsis:
                        assert t.stop > 0
                        iRHS = bisect_right(self._timestamps, t.stop)
                        if iRHS == 0: raise TimestampError("t.start before first timestamp")
                        i2 = iRHS
                        return (self._timestamps[:i2], self._values[:i2])
                    elif t.start is not Ellipsis and t.stop is Ellipsis:
                        assert t.start > 0
                        iRHS = bisect_right(self._timestamps, t.start)
                        if iRHS == 0: raise TimestampError("t.start before first timestamp")
                        i1 = iRHS - 1
                        return (self._timestamps[i1:], self._values[i1:])
                    elif t.start is not Ellipsis and t.stop is not Ellipsis:
                        assert type(t.start) in (int, float)
                        assert type(t.stop) in (int, float)
                        assert t.start > 0 and t.stop >= t.start
                        iLHS = bisect_left(self._timestamps, t.start)
                        if iLHS == 0:
                            if t.start < self._timestamps[0]: raise TimestampError("t.start before first timestamp")
                        if iLHS == len(self._timestamps): iLHS = max(iLHS - 1, 0)
                        iRHS = bisect_right(self._timestamps, t.stop)
                        if iRHS == 0: raise TimestampError("t.stop before first timestamp")
                        return (self._timestamps[iLHS:iRHS], self._values[iLHS:iRHS])
                    else:
                        return (list(self._timestamps), list(self._values))


    def __setitem__(self, t, value):
        if t is None:
            # one object for all time
            if self._timestamps is not None: raise ObjectForAllTimeError("Currently has time indexed objects - can't create one for all time")
            self._values = value
        else:
            if self._timestamps is None:
                if self._values: raise ObjectForAllTimeError("Currently has one object for all time - cannot add any more")
                self._timestamps = [t]
                self._values = [value]
            else:
                if type(t) in (int, float):
                    i2 = bisect_right(self._timestamps, t)
                    self._timestamps.insert(i2, t)
                    self._values.insert(i2, value)
                else:
                    raise NotImplementedError("__setitem__")

    def addAll(self, tss, values):
        if self._timestamps is None:
            if self._values is None:
                assert type(tss) == list
                assert type(values) == list
                assert len(tss) > 0
                assert len(tss) == len(values)
                self._timestamps = tss
                self._values = values
            else:
                raise ObjectForAllTimeError('Timeseries has been already set with one object for all time')
        else:
            raise NotImplementedError("addAll")

    def __delitem__(self, t):
        if self._timestamps is None:
            if t is None:
                self.__init__()
            else:
                raise ObjectForAllTimeError("Currently has one object for all time - cannot delete any part")
        else:
            if type(t) in (int, float):
                i2 = bisect_right(self._timestamps, t)
                if i2 == 0: raise TimestampError("Timestamp before first timestamp")
                if not close(self._timestamps[i2 - 1], t): raise TimestampError("%s not in timeseries" % t)
                del self._timestamps[i2 - 1]
                del self._values[i2 - 1]
            else:
                raise NotImplementedError("__delitem__")

    def __contains__(self, t):
        if self._timestamps is None:
            return self._values is not None
        else:
            if type(t) in (int, float):
                i2 = bisect_right(self._timestamps, t)
                if i2 == 0: return False
                return close(self._timestamps[i2 - 1], t)
            else:
                raise NotImplementedError("__contains__")

    def removeAll(self):
        self.__init__()

    @property
    def firstTS(self):
        if self._timestamps is None:
            if self._values is None:
                raise TimestampError('No elements')
            else:
                return None     # or -ve infinity or 0?
        else:
            return self._timestamps[0]

    @property
    def lastTS(self):
        if self._timestamps is None:
            if self._values is None:
                raise TimestampError('No elements')
            else:
                return None     # or +ve infinity
        else:
            return self._timestamps[-1]
