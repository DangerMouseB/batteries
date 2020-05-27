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


from coppertop.examples.format_calendar import *
from coppertop.examples.format_calendar import _UntilWeekdayName
from coppertop import time
from coppertop.time import AddPeriod, DaySecond, ParseAbstractDate, YYYY_MM_DD


# see notes in format_calendar.py


# utilities to help testing

@Pipeable
def _IthDateBetween(start, end, i):
    ithDate = start >> time.AddPeriod(DaySecond(i))
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
    test_firstQuarter()
    print('pass')


def test_allDaysInYear():
    actual = []
    o = 2020 >> DatesInYear >> PushInto >> ListOR(actual)
    actual[0] >> AssertEqual >> time.AbstractDate(2020, 1, 1)
    actual[-1] >> AssertEqual >> time.AbstractDate(2020, 12, 31)
    [e for e in 2020 >> DatesInYear >> GetIRIter] >> Len >> AssertEqual >> 366


def test_datesBetween():
    ('2020.01.16' >> ParseAbstractDate(YYYY_MM_DD)) >> DatesBetween >> ('2020.01.29' >> ParseAbstractDate(YYYY_MM_DD)) \
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
    dates = [d for d in r >> _UntilWeekdayName(weekdayName='Sun') >> GetIRIter]
    dates[-1] >> AssertEqual >> time.AbstractDate(2020, 1, 5)   # the sunday
    r >> Front >> AssertEqual >> time.AbstractDate(2020, 1, 6) # the monday


def test_WeekChunks():
    datesR = DatesBetween('2020.01.16' >> ParseAbstractDate(YYYY_MM_DD), '2020.01.29' >> ParseAbstractDate(YYYY_MM_DD))
    weeksR = datesR >> ChunkUsingSubRangeGenerator(_UntilWeekdayName(weekdayName='Sun'))
    actual = []
    while not weeksR.empty:
        weekR = weeksR.front
        actual.append([d >> Day for d in weekR >> GetIRIter])
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
    [ws for ws in weekStringsR >> GetIRIter] >> AssertEqual >> expectedJan2020

    actual = [ws for ws in weekStringsR2 >> GetIRIter]
    if actual >> AssertEqual(returnResult=True) >> expectedJan2020 >> Not: "fix WeekStrings.save()" >> PP


def test_MonthTitle():
    1 >> MonthTitle(..., 21) >> WrapInList >> IndexableFR \
        >> RMap >> Strip >> Materialise \
        >> AssertEqual \
        >> ['January']


def test_oneMonthsOutput():
    [
        1 >> MonthTitle(width=21) >> WrapInList >> IndexableFR,
        2020 >> DatesInYear
            >> MonthChunks
            >> Front
            >> WeekChunks
            >> WeekStrings
    ] >> ChainAsSingleRange \
        >> Materialise >> AssertEqual >> Jan2020TitleAndDateLines

    # equivalently
    AssertEqual(
        Materialise(MonthLines(Front(MonthChunks(DatesInYear(2020))))),
        Jan2020TitleAndDateLines
    )


def test_firstQuarter():
    2020 >> DatesInYear \
        >> MonthChunks \
        >> RTake(3) \
        >> RRaggedZip >> RMap >> MonthStringsToCalendarRow(na, " "*21, " ")



Jan2020DateLines = [
    '        1  2  3  4  5',
    '  6  7  8  9 10 11 12',
    ' 13 14 15 16 17 18 19',
    ' 20 21 22 23 24 25 26',
    ' 27 28 29 30 31      ',
]

Jan2020TitleAndDateLines = ['       January       '] + Jan2020DateLines

Q1_2013TitleAndDateLines = [
    "       January              February                March        ",
    "        1  2  3  4  5                  1  2                  1  2",
    "  6  7  8  9 10 11 12   3  4  5  6  7  8  9   3  4  5  6  7  8  9",
    " 13 14 15 16 17 18 19  10 11 12 13 14 15 16  10 11 12 13 14 15 16",
    " 20 21 22 23 24 25 26  17 18 19 20 21 22 23  17 18 19 20 21 22 23",
    " 27 28 29 30 31        24 25 26 27 28        24 25 26 27 28 29 30",
    "                                             31                  "
]


if __name__ == '__main__':
    main()


