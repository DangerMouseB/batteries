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


from batteries.examples.format_calendar import *
from batteries.examples.format_calendar import _UntilWeekdayName


# see notes in format_calendar.py


# utilities to help testing

@Pipeable
def _IthDateBetween(start, end, i):
    ithDate = start + datetime.timedelta(i)
    return FnAdapterFRange.Empty if ithDate > end else ithDate

@Pipeable
def DatesBetween(start, end):
     return FnAdapterFRange((start, end) >> args >> _IthDateBetween)



# tests

def main():
    test_allDaysInYear()
    test_datesBetween()
    test_chunkingIntoMonths()
    test_checkNumberOfDaysInEachMonth()
    test__UntilWeekdayName()
    test_WeekChunks()
    test_WeekStrings()
    test_MonthTitle()
    test_oneMonthsOutput()
    print('pass')


def test_allDaysInYear():
    actual = []
    o = 2020 >> DatesInYear >> PushInto >> ListOR(actual)
    actual[0] >> AssertEqual >> datetime.date(2020, 1, 1)
    actual[-1] >> AssertEqual >> datetime.date(2020, 12, 31)
    [e for e in 2020 >> DatesInYear >> GetIter] >> Len >> AssertEqual >> 366


def test_datesBetween():
    ('2020.01.16' >> ToDate) >> DatesBetween >> ('2020.01.29' >> ToDate) \
        >> RMap >> Day \
        >> Materialise >> AssertEqual >> [16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29]


def test_chunkingIntoMonths():
    2020 >> DatesInYear \
        >> MonthChunks \
        >> Materialise \
        >> Len >> AssertEqual >> 12


def test_checkNumberOfDaysInEachMonth():
    2020 >> DatesInYear \
        >> MonthChunks \
        >> Materialise >> Each >> Len \
        >> AssertEqual >> [31,29,31,30,31,30,31,31,30,31,30,31]


def test__UntilWeekdayName():
    r = 2020 >> DatesInYear
    dates = [d for d in r >> _UntilWeekdayName(weekdayName='Sun') >> GetIter]
    dates[-1] >> AssertEqual >> datetime.date(2020,1,5)   # the sunday
    r >> Front >> AssertEqual >> datetime.date(2020,1,6) # the monday


def test_WeekChunks():
    datesR = DatesBetween('2020.01.16' >> ToDate, '2020.01.29' >> ToDate)
    weeksR = datesR >> ChunkUsingSubRangeGenerator(_UntilWeekdayName(weekdayName='Sun'))
    actual = []
    while not weeksR.empty:
        weekR = weeksR.front
        actual.append([d >> Day for d in weekR >> GetIter])
        weeksR.popFront()
    actual >> AssertEqual >> [[16, 17, 18, 19], [20, 21, 22, 23, 24, 25, 26], [27, 28, 29]]


def test_WeekStrings():
    expectedJan2020 = [
        '        1  2  3  4  5',
        '  6  7  8  9 10 11 12',
        ' 13 14 15 16 17 18 19',
        ' 20 21 22 23 24 25 26',
        ' 27 28 29 30 31      ',
    ]
    weekStringsR = (
        2020 >> DatesInYear
        >> MonthChunks
        >> Front
        >> WeekChunks
        >> WeekStrings
    )
    weekStringsR2 = weekStringsR.save()
    [ws for ws in weekStringsR >> GetIter] >> AssertEqual >> expectedJan2020

    actual = [ws for ws in weekStringsR2 >> GetIter]
    if actual >> AssertEqual(returnResult=True) >> expectedJan2020 >> Not: "fix WeekStrings.save()" >> PP


def test_MonthTitle():
    1 >> MonthTitle(..., 21) >> WrapInList >> IndexableFR \
        >> RMap >> Strip >> Materialise \
        >> AssertEqual \
        >> ['January']


def test_oneMonthsOutput():
    expectedJan2020 = [
        '       January       ',
        '        1  2  3  4  5',
        '  6  7  8  9 10 11 12',
        ' 13 14 15 16 17 18 19',
        ' 20 21 22 23 24 25 26',
        ' 27 28 29 30 31      ',
    ]
    [
        1 >> MonthTitle(width=21) >> WrapInList >> IndexableFR,
        2020 >> DatesInYear
            >> MonthChunks
            >> Front
            >> WeekChunks
            >> WeekStrings
    ] >> ChainRanges \
        >> Materialise >> AssertEqual >> expectedJan2020

    2020 >> DatesInYear \
        >> MonthChunks \
        >> Front \
        >> MonthLines \
        >> Materialise >> AssertEqual >> expectedJan2020


if __name__ == '__main__':
    main()


