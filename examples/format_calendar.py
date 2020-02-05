#*******************************************************************************
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
#*******************************************************************************



# A python implementation of  https://wiki.dlang.org/Component_programming_with_ranges
# I found developing this a little too hard to do in a jupyter notebook so used PyCharm community edition


# When I first read the article I was bothered as my mind was asking "where's the magic?". To
# print the calendar the algorithm must visit each actual dates 3 times - once to generate
# the month chunks which happens in the take(3) statement (which also returns 3 new ranges that
# start on the month boundaries - once I figured that out my mind stopped asking where's the magic),
# once to determine the month widths (in pasteBlocks), and lastly to format the actual calendar.
#
# From the top down I think there are 2 key things to notice in order to solve the problem, 1) that the
# problem involves creating 4 rows of 3 separate month streams, and, 2) that formatting a month only
# requires one pass through each stream. The rest is mechanics.
#
# Two more questions to answer, performance and code style
#
# As a high level array and matrix programmer who only uses low level languages for numerical
# computations, until some colleagues pointed it out to me, I didn't appreciate that:
#     memory speed is slower than processor speed - see the playstation article
#     memory allocation is really expensive
#
# Maybe ranges won't speed up my Python code - especially as I'm binding the arguments to the
# functions in the PipeableFunction class. I can imagine they might help performance and memory
# usage in D.
#
# In Python the final arbiter will be code quality. Can you the reader follow it? How long does it take
# for someone (measure both the author and others) to interesting and unexpected changes to it?
#
# A claim made of D is that it is plastic. Given the foundation of the pipeable module some of this
# plasticity should follow with the usage of the ranges module. I have found it enjoyable to replace
# list comprehensions and for each in iter: statements with piped function calls.
#
# Clearly this code is not currently idiomatic Python, but does the addition of ranges to pipeable
# help or hinder? Answers on a postcard pls.


import datetime
from batteries import *


# ?datesInYear
@Pipeable
def DatesInYear(year):
     return FnAdapterFRange(year >> _IthDateInYear)
@Pipeable
def _IthDateInYear(year, i):
    ithDate = datetime.date(year, 1, 1) + datetime.timedelta(i)
    return FnAdapterFRange.Empty if ithDate.year != year else ithDate


# ?byMonth
@Pipeable
def MonthChunks(datesR):
    return datesR >> ChunkFROnChangeOf >> (lambda x: x.month)


# ?byWeek
@Pipeable
def _UntilWeekdayName(datesR, weekdayName):
    return datesR >> Until(f=lambda d: d >> Weekday >> WeekdayName == weekdayName)
WeekChunks = ChunkUsingSubRangeGenerator(_UntilWeekdayName(weekdayName='Sun'))


@Pipeable
def DateAsDayString(d):
    return d >> Day >> ToStr >> RJust(3)


# ?formatWeek
@Pipeable
class WeekStrings(IForwardRange):
    def __init__(self, rOfWeeks):
        self.rOfWeeks = rOfWeeks

    @property
    def empty(self):
        return self.rOfWeeks.empty

    @property
    def front(self):
        # this exhausts the front week range
        week = self.rOfWeeks.front
        startDay = week.front >> Weekday
        preBlanks = ['   '] * startDay
        dayStrings = week >> RMap >> DateAsDayString >> Materialise
        postBlanks = ['   '] * (7 - ((dayStrings >> Len) + startDay))
        return ''.join(preBlanks + dayStrings + postBlanks)

    def popFront(self):
        self.rOfWeeks.popFront()

    def save(self):
        # TODO delete once we've debugged the underlying save issue
        return _WeekStrings(self.rOfWeeks.save())


# ?monthTitle
@Pipeable
def MonthTitle(month, width):
    return month >> MonthLongName >> CJust(width)


# ?formatMonth
@Pipeable
def MonthLines(monthDays):
    return [
        MonthTitle(monthDays.front.month, 21) >> WrapInList >> IndexableFR,
        monthDays >> WeekChunks >> WeekStrings
    ] >> ChainAsSingleRange


@Pipeable
class RaggedZip(IInputRange):
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
                parts.append(null)
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



