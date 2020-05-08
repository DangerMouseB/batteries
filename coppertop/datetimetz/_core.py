#*******************************************************************************
#
#    Copyright (c) 2020 David Briant
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

# TODO handle offset formats
# TODO handle locales

# Here we just support microseconds in the storage (although the api is designed to handle second and
# millisecond precision and could be extended to nano-second etc precision).

# To help prevent accidentally looking into the future, time aware types with different precisions are not
# substitutable, although can easily be asOf converted to less precision.

# We want to be as strongly typed as possible - so at the application level a decision wil be made as to precision.
# You cannot take a microsecond precision timestamp and compare it with a millisecond precision timestamp
# So UTC.subseconds returns None, millis or micros depending on precision

# There's a peculiar view expressed in the [java.time documentation](https://docs.oracle.com/javase/9/docs/api/java/time/package-summary.html) -
# "ZonedDateTime stores a date and time with a time-zone. This is useful if you want to perform accurate
# calculations of dates and times taking into account the ZoneId, such as 'Europe/Paris'. Where possible,
# it is recommended to use a simpler class without a time-zone. The widespread use of time-zones tends
# to add considerable complexity to an application."
#
# Since we are financially focused, instead we insist that all time aware types have a timezone but we
# encourage using a city as the observers context rather than a fixed offet to UTC (which changes during
# DST. We have strived to make the api better at reducing the above alleged complexity.
#
# Our initial focus here is a good interface and possibly later reimplementation is a fast systems language.


# FORMATTING CODES
# yyyy - four digit year
# yy - double digit year
# y - single digit year (e.g. for futures contracts)
# MMMM - long month name in locale
# MMM - short (TLA) month name in locale
# MM - month number 01 - 12
# M - month number 1-12
# dddd - full day name in locale
# ddd - short (TLA) day name in locale
# dd - day number 01-31
# d - day number 1-31
# hh - hours 00-23
# h - hours 0-23
# HH - hours 1-12
# H - hours 1-12
# mm - minutes 00-60
# m - minutes 0-60
# ss - seconds 00-61
# s - seconds 0-61
# tt - AM/PM
# t - A/P
# ms - millisecond precision
# us - microsecond precision
# ns - nanosecond precision
# FFFF, IIII, ZZZZ - FpML City, Iana City, Iana Tz
# ZZZ - common DST aware time-zone name, e.g. GMT, BST, EST, EDT etc
# HMUZ - futures contract month code


from typing import Union
from datetime import datetime as _datetime, date as _date, time as _time, timedelta as _timedelta
from pytz import timezone as _timezone
import math
from _strptime import _strptime
from collections import namedtuple

from ..pipeable import Pipeable, Missing
from ._enums import Tz, FpMLCity, IanaCity, IanaTz, Precision, FpMLCityForName, IanaCityForName, IanaTzForName, ToIanaCity

_YMDHMSSPZ = namedtuple('_YMDHMSSPZ', ['y', 'M', 'd', 'h', 'm', 's', 'ss', 'p', 'z'])

_dispatcherByFnName = {}

class _Dispatcher(object):
    def __init__(self, fnName):
        self._fnName = fnName
        self._fnByTypes = {}    #  this can be replaced with something that can handle subtypes etc
    def __call__(self, *args, **kwargs):
        types = tuple(arg.__class__ for arg in args)
        fn = self._fnByTypes.get(types)
        if fn is None:
            raise TypeError("no match")
        return fn(*args, **kwargs)
    def register(self, types, function):
        self._fnByTypes[types] = function
        return self

def overload(*types):
    def registerMultiMethod(function):
        fnName = function.__name__
        return _dispatcherByFnName.setdefault(fnName, _Dispatcher(fnName)).register(types, function)
    return registerMultiMethod



class UTC(object):
    def __init__(self, *args):
        if len(args) == 1:
            # YMDHMS
            self._dt = _datetime(*args)
            self.precision = Precision.sa.t
        elif len(args) == 1:
            # YMDHMS
            self._dt = _datetime(*args)
            self.precision = Precision.s
        elif len(args) == 5:
            # y, M, d, H, M
            self._dt = _datetime(*args)
            self.precision = Precision.s
        elif len(args) == 6:
            # y, M, d, H, M, S
            self._dt = _datetime(*args)
            self.precision = Precision.s
        elif len(args) == 8:
            # y, M, d, H, M, S, subSeconds, precision
            subseconds, precision = args[6:8]
            micro = subseconds * 1000 if precision == Precision.ms else subseconds
            self._dt = _datetime(*(args[0:6] + (micro, )))
            self.precision = precision
        else:
            raise TypeError('%s args passed, 5, 6 or 8 required - y, M, d, H, M, [S], [subSeconds, precision]')
    def __repr__(self):
        return 'UTC(%s, %s, %s, %s, %s, %s, %s, %s)' % (
            self._dt.year,
            self._dt.month,
            self._dt.day,
            self._dt.hour,
            self._dt.minute,
            self._dt.second,
            self.subsecond,
            self.precision
        )
    @property
    def year(self):
        return self._dt.year
    @property
    def month(self):
        return self._dt.month
    @property
    def day(self):
        return self._dt.day
    @property
    def hour(self):
        return self._dt.hour
    @property
    def minute(self):
        return self._dt.minute
    @property
    def second(self):
        return self._dt.second
    @property
    def subsecond(self):
        if self.precision == Precision.s:
            return None
        elif self.precision == Precision.ms:
            return int(self._dt.microsecond / 1000)
        elif self.precision == Precision.us:
            return self._dt.microsecond
        elif self.precision == Precision.ns:
            raise TypeError('ns not handled')
        else:
            raise TypeError('Unknown precision type')
    def __eq__(self, other):
        if not isinstance(other, UTC):
            raise TypeError('RHS (%s) is not UTC' % repr(other))
        if self.precision != other.precision:
            raise TypeError('LHS Precision(%s) != RHS Precision(%s)' % (self.precision, other.precision))
        return (self._dt == other._dt)


class Date(_date):
    def __repr__(self):
        return 'Date(%s, %s, %s)' % (
            self.year,
            self.month,
            self.day
        )

class TimeTz(object):
    def __init__(self, *args):
        # Tz, H, M, [S], [subSeconds, precision]
        if len(args) == 3:
            tz = args[2]

class DateTimeTz(object):
    def __init__(self):
        # Date, TimeTz
        # Date, HMS, Tz
        # Date, H, M, [S], [subSeconds, precision], Tz
        # YMDHMS, Tz
        # y, M, d, HMS, Tz
        # y, M, d, H, M, [S], [subSeconds, precision], Tz
        pass

class HMS(object):
    def __init__(self, *args):
        # H, M, [S], [subSeconds, precision]
        pass

class YMDHMS(object):
    def __init__(self, *args):
        # y, M, d, H, M, [S], [subSeconds, precision]
        pass

class YearMonth(object): pass
class MonthDay(object): pass



#*******************************************************************************
# Parsing Utilities
#*******************************************************************************

def _parseDTTz(x, format):
    # rework to be more efficient in bulk by parsing format separately from x or handle x as an array / range
    if format.find('ns') > -1:
        raise NotImplementedError('format ns (nano seconds) has not been implemented yet')
    if format.find('ms') > -1:
        precision = Precision.ms
    elif format.find('us') > -1:
        precision = Precision.us
    else:
        precision = Precision.s
    cFormat = _simpleFormatToCTimeFormat(format)
    if (i := cFormat.find(' FFFF')) > -1:
        iRightmostSpace = x.rfind(' ')
        datePart = x[:iRightmostSpace]
        dateFormat = cFormat[0:i]
        tzPart = x[iRightmostSpace + 1:]
        tz = ParseFpMLCity(tzPart)
    elif (i := cFormat.find(' IIII')) > -1:
        iRightmostSpace = x.rfind(' ')
        datePart = x[:iRightmostSpace]
        dateFormat = cFormat[0:i]
        tzPart = x[iRightmostSpace + 1:]
        tz = ParseIanaCity(tzPart)
    elif (i := cFormat.find(' ZZZZ')) > -1:
        iRightmostSpace = x.rfind(' ')
        datePart = x[:iRightmostSpace]
        dateFormat = cFormat[0:i]
        tzPart = x[iRightmostSpace + 1:]
        tz = ParseIanaTz(tzPart)
    else:
        datePart = x
        dateFormat = cFormat
        tz = None
    dt, micro, _ = _strptime(datePart, dateFormat)
    seconds = dt[5]
    _checkPrecision(seconds, micro, precision)
    return _YMDHMSSPZ(dt[0], dt[1], dt[2], dt[3], dt[4], seconds, micro, precision, tz)

def _roundToPrecision(seconds, micro, precision):
    if precision == Precision.s:
        return seconds + (1 if micro > 0 else 0), 0
    elif precision == Precision.ms:
        return 0, math.ceil(micro / 1000.0) * 1000
    elif precision == Precision.us:
        return seconds, micro
    else:
        raise TypeError('%s not handled' % repr(precision))

def _checkPrecision(seconds, micro, precision):
    if precision == Precision.s:
        if micro > 0:
            raise ValueError("micro must be zero for %s" % repr(precision))
        return True
    elif precision == Precision.ms:
        if micro != math.ceil(micro / 1000.0) * 1000:
            raise ValueError("microseconds present for %s" % repr(precision))
    elif precision == Precision.us:
        return True
    else:
        raise TypeError('%s not handled' % repr(precision))

def _simpleFormatToCTimeFormat(simpleFormat):
    # a little care is needed here to avoid clashes between formats
    answer = simpleFormat
    answer = answer.replace('HH', '%I')
    answer = answer.replace('H', '%<single-digit-12hour>')
    answer = answer.replace('hh', '%H')
    answer = answer.replace('h', '%<single-digit-24hour>')
    answer = answer.replace('ms', '%f')
    answer = answer.replace('us', '%f')
    answer = answer.replace('tt', '%p')
    answer = answer.replace('t', '%<single-digit-AM/PM>')
    answer = answer.replace('yyyy', '%Y')
    answer = answer.replace('yy', '%y')
    answer = answer.replace('y', '%<single-digit-year>')
    answer = answer.replace('%%<single-digit-year>', '%y')        # correct the mis-substitution above
    answer = answer.replace('MMMM', '%B')
    answer = answer.replace('MMM', '%b')
    answer = answer.replace('MM', '%m')
    answer = answer.replace('M', '%<single-digit-month>')
    answer = answer.replace('dddd', '%A')
    answer = answer.replace('ddd', '%a')
    answer = answer.replace('dd', '%d')
    answer = answer.replace('d', '%e')
    answer = answer.replace('%%e', '%d')        # correct the mis-substitution above
    answer = answer.replace('mm', '%M')
    answer = answer.replace('m', '%<single-digit-minute>')
    answer = answer.replace('%%<single-digit-minute>', '%m')
    answer = answer.replace('ss', '%S')
    answer = answer.replace('s', '%<single-digit-second>')
    answer = answer.replace('zzz', '%Z')
    return answer

# fast formats - _ can be slash, dot, hyphen or any other single character
YY_MM_DD = 1
YYYY_MM_DD = 2
DD_MM_YY = 3
DD_MM_YYYY = 4
MM_DD_YY = 5
MM_DD_YYYY = 6
# etc tbc

@Pipeable
def ParseUTC(format, s, locale=Missing):
    args = _parseDTTz(s, format)
    assert args[-1] == None
    return UTC(*args[0:8])

@Pipeable
def ParseDateTimeTz(format, s, locale=Missing):
    # "2020.01.01 16:15 GBLN" >> ToDateTimeTz
    pass

@Pipeable
def ParseDate(format, s, locale=Missing):
    if isinstance(format, int):

        if format == YY_MM_DD:
            YY = int(s[0:2])
            YYYY = YY + 1900 if YY >= 70 else YY + 2000
            return Date(YYYY, int(s[3:5]), int(s[6:8]))

        elif format == YYYY_MM_DD:
            return Date(int(s[0:4]), int(s[5:7]), int(s[8:10]))

        elif format == DD_MM_YY:
            YY = int(s[6:8])
            YYYY = YY + 1900 if YY >= 70 else YY + 2000
            return Date(YYYY, int(s[3:5]), int(s[0:2]))

        elif format == DD_MM_YYYY:
            return Date(int(s[6:10]), int(s[3:5]), int(s[0:2]))

        elif format == MM_DD_YY:
            YY = int(s[6:8])
            YYYY = YY + 1900 if YY >= 70 else YY + 2000
            return Date(YYYY, int(s[0:2]), int(s[3:5]))

        elif format == MM_DD_YYYY:
            return Date(int(s[6:10]), int(s[0:2]), int(s[3:5]))

    else:
        args = _parseDTTz(s, format)
        assert args[-1] == None
        return Date(*args[0:3])

@Pipeable
def ParseTimeTz(format, s, locale=Missing):
    pass

@Pipeable
def ParseTz(format, s, locale=Missing):
    pass

@Pipeable
def ParseFpMLCity(s, locale=Missing):
    return FpMLCityForName(s)

@Pipeable
def ParseIanaCity(s, locale=Missing):
    return IanaCityForName(s)

@Pipeable
def ParseIanaTz(s, locale=Missing):
    return IanaTzForName(s)

@Pipeable
def ParseOffsetTz(s, locale=Missing):
    pass

@Pipeable
def ParseYMDHMS(format, s, locale=Missing):
    pass

@Pipeable
def ParseHMS(format, s, locale=Missing):
    pass

@Pipeable
def ParseYearMonth(format, s, locale=Missing):
    pass

@Pipeable
def ParseMonthDay(format, s, locale=Missing):
    pass



#*******************************************************************************
# TimeZone Conversions
#*******************************************************************************

def _example():
    LON = _timezone('Europe/London')
    UTC = _timezone('UTC')
    NYC = _timezone('America/New_York')

    a = LON.localize(_datetime(2020,6,1,16,15))
    b = a.astimezone(NYC)
    c = b.astimezone(UTC)
    
@overload(Tz, UTC)
def ToTz(tz, u):
    assert isinstance(tz, (FpMLCity, IanaCity, IanaTz))
    raise NotImplementedError()

@overload(Tz, DateTimeTz)
def ToTz(tz, dttz: Union[FpMLCity, IanaCity, IanaTz]):
    # Converts a DateTimeTz into a new DateTimeTz for the given Tz
    # aDTTz >> ToDateTimeTz(GBLN)
    assert isinstance(tz, (FpMLCity, IanaCity, IanaTz))
    raise NotImplementedError()

@overload(DateTimeTz)
def ToUTC(dttz):
    raise NotImplementedError()



#*******************************************************************************
# Precision Conversions
#*******************************************************************************

@Pipeable
def AsOfSecond(x):
    assert isinstance(x, (UTC, DateTimeTz, TimeTz, YMDHMS, HMS))
    raise NotImplementedError

@Pipeable
def AsOfMilli(x):
    assert isinstance(x, (UTC, DateTimeTz, TimeTz, YMDHMS, HMS))
    raise NotImplementedError

@Pipeable
def AsOfMicro(x):
    assert isinstance(x, (UTC, DateTimeTz, TimeTz, YMDHMS, HMS))
    raise NotImplementedError

@Pipeable
def AsOfNano(x):
    assert isinstance(x, (UTC, DateTimeTz, TimeTz, YMDHMS, HMS))
    raise NotImplementedError



#*******************************************************************************
# String Formatting
#*******************************************************************************

@overload(str, UTC)
def ToString(format, u, locale=Missing):
    return repr(u)

@overload(Date)
def ToString(format, d, locale=Missing):
    return repr(d)

@overload(str, DateTimeTz)
def ToString(format, dttz, locale=Missing):
    return repr(dttz)

@overload(str, TimeTz)
def ToString(format, ttz, locale=Missing):
    return repr(ttz)

@overload(str, HMS)
def ToString(format, ttz, locale=Missing):
    return repr(ttz)

@overload(str, YMDHMS)
def ToString(format, ttz, locale=Missing):
    return repr(ttz)

@overload(str, YearMonth)
def ToString(format, ym, locale=Missing):
    return repr(ym)

ToString = Pipeable(ToString)



#*******************************************************************************
# Simple arithmetic
#*******************************************************************************

@Pipeable
def AddDays(numDays, d):
    # typical usage aDate >> AddDays(n)
    pyDate = _date(d.year, d.month, d.day) + _timedelta(numDays)
    return Date(pyDate.year, pyDate.month, pyDate.day)


