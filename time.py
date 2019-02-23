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


try:
    from _strptime import strptime
    _version = 24
except ImportError:
    from _strptime import _strptime as strptime
    _version = 27

from datetime import datetime
import math



SAT = 0
SUN = 1
MON = 2
TUE = 3
WED = 4
THU = 5
FRI = 6

def noneAsZero(floatOrNone):
    if floatOrNone is None: return 0.0
    return floatOrNone
    
def gregFromXL(xl):
    return xl - 25569 + 719163

def xlFromGreg(gr):
    return gr - 719163 + 25569
    
def xlFromString(dateString, format="%d/%m/%Y"):
    return xlFromGreg(gregFromString(dateString, format))

def gregFromString(dateString, format="%d/%m/%Y"):
    """format codes:

    %a - abbreviated weekday name
    %A - full weekday name
    %b - abbreviated month name
    %B - full month name
    %c - preferred date and time representation
    %C - century number (the year divided by 100, range 00 to 99)
    %d - day of the month (01 to 31)
    %D - same as %m/%d/%y
    %e - day of the month (1 to 31)
    %g - like %G, but without the century
    %G - 4-digit year corresponding to the ISO week number (see %V).
    %h - same as %b
    %H - hour, using a 24-hour clock (00 to 23)
    %I - hour, using a 12-hour clock (01 to 12)
    %j - day of the year (001 to 366)
    %m - month (01 to 12)
    %M - minute
    %n - newline character
    %p - either am or pm according to the given time value
    %r - time in a.m. and p.m. notation
    %R - time in 24 hour notation
    %S - second
    %t - tab character
    %T - current time, equal to %H:%M:%S
    %u - weekday as a number (1 to 7), Monday=1. Warning: In Sun Solaris Sunday=1
    %U - week number of the current year, starting with the first Sunday as the first day of the first week
    %V - The ISO 8601 week number of the current year (01 to 53), where week 1 is the first week that has at least 4 days in the current year, and with Monday as the first day of the week
    %W - week number of the current year, starting with the first Monday as the first day of the first week
    %w - day of the week as a decimal, Sunday=0
    %x - preferred date representation without the time
    %X - preferred time representation without the date
    %y - year without a century (range 00 to 99)
    %Y - year including the century
    %Z or %z - time zone or name or abbreviation
    %% - a literal % character
"""
    st = strptime(dateString, format)
    if _version == 27: st = st[0]
    return datetime(st.tm_year, st.tm_mon, st.tm_mday, st.tm_hour, st.tm_min, st.tm_sec).toordinal()


def hhmmssusFromFloat(f):
    # f is the fraction of the day - a la xl
    t = round(f * 24.0 * 60.0 * 60.0 * 1000.0)
    r = math.floor(t / 1000.0)
    ms = t - r * 1000.0
    t, r = r, math.floor(r / 60.0)
    ss = t - r * 60.0
    t, r = r, math.floor(r / 60.0)
    mm = t - r * 60.0
    t, r = r, math.floor(r / 24.0)
    hh = t - r * 24.0
    if ms >= 1000.0: ss, ms = ss + 1.0, ms - 1000.0
    if ss > 60.0: mm, ss = mm + 1.0, ss - 60.0
    if mm > 60.0: hh, mm = hh + 1.0, mm - 60.0
    return (int(hh + r * 24.0), int(mm), int(ss), int(ms) * 1000)

def floatFromhhmmssus(hh, mm, ss, us):
    return (hh + (mm + (ss + us / 1000000.0) / 60.0) / 60.0) / 24.0


class date(object):
    
    # adds the idea of a floating ordinal with the fraction representing a fraction of a day (a la xl)
    # combines xl and gregorian ordinals with a datetime object - removes the concept of timedelta to make simple addition easier
    # rounded to the nearest millisecond
    # time arithmatic is straight forward since we ignore leap seconds
    # dates can be full or partial (xl & greg are full), dt can be partial
    # arithmatic with ints and floats assumes xl ordinals


    # TODO
    # consider timezone
    # use a strptime equivalent that can handle milli, and micro seconds etc
    
    
    def __initProperties__(self):
        self._xl = None
        self._greg = None
        self._dt = None
        self._day = None
        self._d = None
        self._m = None
        self._y = None
        self._hh = None
        self._mm = None
        self._ss = None
        self._us = None        # 0 to 999999 micro seconds, with excel only really use the ms interface since a double only has ms resolution
    
    def __init__(self, *args, **kwargs):
        if len(args) == 1: 
            if type(args[0]) not in (str): raise TypeError("arg[0] must be a date string")
            self.__initProperties__()
            fmt = kwargs.get('format')
            if fmt is None: fmt = "%d/%m/%Y"              # apologies to any North American's
            st = strptime(args[0], fmt)
            if _version == 27: st = st[0]
            self._y, self._m, self._d, self._hh, self._mm, self._ss, self._us = st.tm_year, st.tm_mon, st.tm_mday, st.tm_hour, st.tm_min, st.tm_sec, 0
            return None
        elif len(args) > 1:
            raise TypeError("len(args) > 1")
        elif len(kwargs) == 0:
            raise TypeError("Must initialise with either *args or **kwargs")
        elif len(kwargs) > 0:
            self.__initProperties__()
            for k, v in kwargs.items():
                if k == "xl":
                    assert len(kwargs) == 1
                    self._xl = v
                elif k == "greg" in kwargs:
                    assert len(kwargs) == 1
                    self._greg = v
                elif "dt" in kwargs:
                    assert len(kwargs) == 1
                    self._dt = v
                elif k == "d":
                    self._d = v
                elif k == "m":
                    self._m = v
                elif k == "y":
                    self._y = v
                elif k == "hh":
                    self._hh = v
                elif k == "mm":
                    self._mm = v
                elif k == "ss":
                    self._ss = v
                elif k == "ms":
                    assert self._us is None
                    self._us = v * 1000
                elif k == "us":
                    assert self._us is None
                    self._us = v
                else:
                    raise AttributeError("Unknown attribute in __init__ kwargs")

    def _fillComponents(self):
        if self._dt is None:
            if self._greg is None:
                if self._xl is None:
                    return None
                self._greg = gregFromXL(self._xl)
            self._dt = datetime.fromordinal(int(self._greg))
        d = self._dt
        self._y, self._m, self._d, self._hh, self._mm, self._ss, self._us = (d.year, d.month, d.day) + hhmmssusFromFloat(self.xl - math.floor(self.xl))

    def _fillXL(self):
        if self._greg is None:
            if self._dt is None:
                if None in (self._y, self._m, self._d, self._hh, self._mm, self._ss, self._us):
                    return None
                self._dt = datetime(self._y, self._m, self._d, self._hh, self._mm, self._ss, self._us)
            dt = self._dt
            self._greg = dt.toordinal() + floatFromhhmmssus(dt.hour, dt.minute, dt.second, dt.microsecond)
        self._xl = xlFromGreg(self._greg)
        
    def _fillGreg(self):
        if self._xl is None:
            if self._dt is None:
                if None in (self._y, self._m, self._d, self._hh, self._mm, self._ss, self._us):
                    return None
                self._dt = datetime(self._y, self._m, self._d, self._hh, self._mm, self._ss, self._us)
            dt = self._dt
            self._greg = dt.toordinal() + floatFromhhmmssus(dt.hour, dt.minute, dt.second, dt.microsecond)
            self._xl = xlFromGreg(self._greg)
        else:
            self._greg = gregFromxl(self._xl)

    @property
    def xl(self):
        if self._xl is not None: return self._xl
        self._fillXL()
        return self._xl
    
    @property
    def greg(self):
        if self._greg is not None: return self._greg
        self._fillGreg()
        return self._greg
    
    @property
    def dt(self):
        raise NotImplementedError()
    
    @property
    def d(self):
        if self._d is not None: return self._d
        self._fillComponents()
        return self._d
    
    @property
    def m(self):
        if self._m is not None: return self._m
        self._fillComponents()
        return self._m
    
    @property
    def y(self):
        if self._y is not None: return self._y
        self._fillComponents()
        return self._y
    
    @property
    def hh(self):
        if self._hh is not None: return self._hh
        self._fillComponents()
        return self._hh
    
    @property
    def mm(self):
        if self._mm is not None: return self._mm
        self._fillComponents()
        return self._mm
    
    @property
    def ss(self):
        if self._ss is not None: return self._ss
        self._fillComponents()
        return self._ss
    
    @property
    def us(self):
        if self._us is not None: return self._us
        self._fillComponents()
        return self._us
    
    @property
    def day(self):
        if self._xl is not None: return self._xl % 7
        if self._dt is not None: return (self._dt.isoweekday() + 1) % 7
        if self._greg is not None: 
            self._xl = xlFromGreg(self._greg)
            return self._xl % 7
        return None
    
    @property
    def isPartial(self):
        if self._xl: return False
        if self._greg: return False
        if None not in (self._y, self._m, self._d, self._hh, self._mm, self._ss, self._us): return False
        return True
    
    @property
    def isComplete(self):
        return not self.isPartial
    
    def _selfCompleteAddPartial(self, partial):
        monthsToAdd = 0
        if partial.y is not None: monthsToAdd = partial.y * 12
        if partial.m is not None: monthsToAdd += partial.m
        d, hh, mm, ss, us = partial.d, partial.hh, partial.mm, partial.ss, partial.us
        if monthsToAdd > 0:
            assert d == None and hh == None and mm == None and ss == None and us == None
            m = self.m + monthsToAdd
            y, m = self.y + m // 12, m % 12
            d, hh, mm, ss, us = self.d, self.hh, self.mm, self.ss, self.us
            answer = None
            while answer is None:
                try:
                    answer = date(dt=datetime(y, m, d, hh, mm, ss, us))
                except:
                    d -= 1
            return answer
        else:
            d, hh, mm, ss, us = noneAsZero(d), noneAsZero(hh), noneAsZero(mm), noneAsZero(ss), noneAsZero(us)
            frac = d + floatFromhhmmssus(hh, mm, ss, us)
            return date(xl=self.xl + frac)
    
    def _selfCompleteSubPartial(self, partial):
        # allow complete - years, complete - months, complete - years and months or complete - days and/or time
        monthsToSub = 0
        if partial.y is not None: monthsToSub = partial.y * 12
        if partial.m is not None: monthsToSub = partial.m
        d, hh, mm, ss, us = partial.d, partial.hh, partial.mm, partial.ss, partial.us
        if monthsToSub > 0:
            assert d == None and hh == None and mm == None and ss == None and us == None
            m = self.m - monthsToSub
            y = self.y
            if m == 0:
                m, y = m + 12, y - 1            
            y, m = y + m // 12, m % 12
            if m == 0:
                m, y = m + 12, y - 1            
            d, hh, mm, ss, us = self.d, self.hh, self.mm, self.ss, self.us
            answer = None
            while answer is None:
                try:
                    answer = date(dt=datetime(y, m, d, hh, mm, ss, us))
                except:
                    d -= 1
            return answer
        else:
            d, hh, mm, ss, us = noneAsZero(d), noneAsZero(hh), noneAsZero(mm), noneAsZero(ss), noneAsZero(us)
            frac = d + floatFromhhmmssus(hh, mm, ss, us)
            return date(xl=self.xl - frac)
    
    def _floatAddPartialSelf(self, f):
        hh, mm, ss, us = hhmmssusFromFloat(f)
        return date(
                d=0 + noneAsZero(self.d), 
                hh=hh + noneAsZero(self.hh),
                mm=mm + noneAsZero(self.mm),
                ss=ss + noneAsZero(self.ss),
                us=us + noneAsZero(self.us)
                )

    def __add__(self, other):        
        if self.isComplete:
            if type(other) in (int, float):
                return date(xl=self.xl + other)
            elif type(other) is date:
                if other.isComplete:
                    return date(xl=self.xl + other.xl)
                else:
                    return self._selfCompleteAddPartial(other)
            raise TypeError("RHS is unhandled type '%s'" % type(other))
        else:
            raise ValueError("Can't add enything to partial LHS")
    
    def __radd__(self, other):
        if self.isComplete:
            if type(other) in (int, float):
                return date(xl=other + self.xl)
            elif type(other) is date:
                raise RuntimeError("Should have been dispatched to __add__ rather than __radd__")
            else:
                raise TypeError("LHS is unhandled type '%s'" % type(other))
        else:
            if type(other) in (int, float):
                return self._floatAddPartialSelf(other)
            elif type(other) is date:
                raise RuntimeError("Should have been dispatched to __add__ rather than __radd__")
            else:
                raise TypeError("LHS is unhandled type '%s'" % type(other))
    
    def __sub__(self, other):
        if self.isComplete:
            if type(other) in (int, float):
                return date(xl=self.xl - other)
            elif type(other) is date:
                if other.isComplete:
                    return date(xl=self.xl - other.xl)
                else:
                    return self._selfCompleteSubPartial(other)
            raise TypeError("Other is unhandled type '%s'" % type(other))
        else:
            raise ValueError("Can't do partial date - anything")
      
    def __rsub__(self, other):
        if self.isComplete:
            if type(other) in (int, float):
                return date(xl=other - self.xl)
            elif type(other) is date:
                raise RuntimeError("Should have been dispatched to __sub__ rather than __rsub__")
            else:
                raise TypeError("LHS is unhandled type '%s'" % type(other))
        else:
            if type(other) is date:
                raise RuntimeError("Should have been dispatched to __sub__ rather than __rsub__")
            else:
                raise TypeError("LHS must be a date since RHS is partial")

    def __mul__(self, other):
        raise NotImplementedError()
      
    def __rmul__(self, other):
        raise NotImplementedError()
      
    def __div__(self, other):
        raise NotImplementedError()
      
    def __rdiv__(self, other):
        raise NotImplementedError()
    
    def __eq__(self, other):
        if self.isComplete:
            if type(other) in (int, float):
                return  self.xl == other
            elif type(other) is date:
                if other.isComplete:
                    return self.xl == other.xl
                else:
                    return False
            else:
                return False
        else:
            if type(other) is date:
                if other.isPartial:
                    raise NotImplementedError()
            return False
    
    def __ne__(self, other):
        return not self == other
    
    def __lt__(self, other):
        if self.isComplete:
            if type(other) in (int, float):
                return self.xl < other
            elif type(other) is date:
                if other.isComplete:
                    return self.xl < other.xl
                else:
                    raise TypeError("LHS is complete RHS is not")
            else:
                raise TypeError("Can't compare LHS with RHS of type '%s'" % type(other))
        else:
            if type(other) is date:
                if other.isPartial:
                    raise NotImplementedError()
            raise TypeError("Can't compare partial LHS with RHS of type '%s'" % type(other))
    
    def __le__(self, other):
        raise NotImplementedError()
    
    def __gt__(self, other):
        raise NotImplementedError()
    
    def __ge__(self, other):
        raise NotImplementedError()
    
    @property
    def firstOfMonth(self):
        if self.isPartial:
            raise RunTime("Partial can't answer first of month")
        else:
            return date(dt=datetime(self.y, self.m, 1))
    
def dayOnOrAfter(d, day):
    while d.day != day:
        d += 1
    return d

    
    
    