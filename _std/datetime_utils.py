#*******************************************************************************
#
#    Copyright (c) 2017-2020 David Briant
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



import datetime
from .misc import ToInt
from .iter_utils import Each
from ..pipeable import Pipeable
from .._core import Missing


@Pipeable
def ToDate(x, strFormat=Missing):
    if strFormat is Missing:
        # assume kdb format
        # TODO implement other conversions
        return datetime.date(*x.split(".") >> Each >> ToInt)
    else:
        raise NotImplementedError()

@Pipeable
def Weekday(x):
    return x.weekday()

@Pipeable
def Year(x):
    return x.year

@Pipeable
def Month(x):
    return x.month

@Pipeable
def Day(x):
    return x.day

@Pipeable
def WeekdayName(x, locale=Missing):
    # TODO implement for other locales
    return ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'][x]

@Pipeable
def WeekdayLongName(x, locale=Missing):
    # TODO implement for other locales
    return ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday'][x]

@Pipeable
def MonthName(month, locale=Missing):
    # TODO implement for other locales
    return ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'][month - 1]

@Pipeable
def MonthLongName(month, locale=Missing):
    # TODO implement for other locales
    return ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December'][month - 1]
