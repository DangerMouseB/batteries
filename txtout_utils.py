#*******************************************************************************
#
#    Copyright (c) 2018-2019 David Briant
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


from .missing import Missing
from .collections import Collector
from collections import namedtuple
from .pipeable import Pipeable

Titles = namedtuple('Titles', ['title', 'subTitles'])

def FormatAsTable(listOfRows, headingDefs=Missing, title=Missing):
    # for moment only handle one level of grouping
    columnTitles = Collector()
    i = 0
    groupTitles = []
    hasGroupTitles = False
    for headingDef in headingDefs:
        if isinstance(headingDef, str):
            groupTitles.append((i, i, ''))
            columnTitles << headingDef
            i += 1
        elif not headingDef:
            groupTitles.append((i, i, ''))
            columnTitles << ''
            i += 1
        else:
            groupTitles.append((i, i + len(headingDef.subTitles) - 1, headingDef.title))
            columnTitles += headingDef.subTitles
            i += len(headingDef.subTitles)
            hasGroupTitles = True
    allRows = ([columnTitles] if headingDefs else []) + [list(row) for row in listOfRows]
    widths = [1] * len(allRows[0])
    lines = Collector()
    for row in allRows:
        for j, cell in enumerate(row):
            row[j] = str(row[j])
            widths[j] = widths[j] if widths[j] >= len(row[j]) else len(row[j])
    cellsWidth = sum(widths) + 2 * len(widths)
    if title is not Missing:
        titleLine = '- ' + title + ' -' if title else ''
        LHWidth = int((cellsWidth - len(titleLine)) / 2)
        RHWidth = (cellsWidth - len(titleLine)) - LHWidth
        titleLine = ('-' * LHWidth) + titleLine + ('-' * RHWidth)
        lines.append(titleLine)
    if groupTitles:
        line = ''
        for i1, i2, groupTitle in groupTitles:
            width = sum([widths[i] for i in range(i1, i2 + 1)])
            width += 2 * (i2-i1)
            line += (' %' + str(width) + 's|') % groupTitle[:width]
        lines << line
    for i, row in enumerate(allRows):
        line = ''
        for j, cell in enumerate(row):
            line += (' %' + str(widths[j]) + 's|') % cell
        lines << line
        if i == 0 and headingDefs:
            line = ''
            for width in widths:
                line += '-' * (width + 1) + '|'
            lines << line
    return lines


@Pipeable
def PrintLines(lines):
    for line in lines:
        print(line)