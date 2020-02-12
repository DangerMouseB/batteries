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


# see - https://en.wikipedia.org/wiki/Jackson_structured_programming
# this file show four ways of implementing the line counting problem - two are
# translations from the wikipedia article and the remaining two take the "traditional"
# program and transform it into range style code - given that CountEquals exhausts
# the range r I'm not sure how one can claim it is functional.


from batteries import *


def countLinesTrad(f):
    answer = []

    count = 0
    firstLineOfGroup = ''
    line = f.readline()
    while line != '':
        if firstLineOfGroup == '' or line != firstLineOfGroup:
            if firstLineOfGroup != '':
                answer.append((firstLineOfGroup, count))
            count = 0
            firstLineOfGroup = line
        count += 1
        line = f.readline()

    if (firstLineOfGroup != ''):
        answer.append((firstLineOfGroup, count))

    return answer



def countLinesRanges1(f):
    r = FileLineIR(f)
    out = ListOR([])

    count = 0
    firstLineOfGroup = ''
    while not r.empty:
        if firstLineOfGroup == '' or r.front != firstLineOfGroup:
            if firstLineOfGroup != '':
                out >> Put >> (firstLineOfGroup, count)
            count = 0
            firstLineOfGroup = r.front
        count += 1
        r.popFront()

    if firstLineOfGroup != '':
        out >> Put >> (firstLineOfGroup, count)

    return out.list



def countLinesRanges2(f):
    out = ListOR([])
    r = FileLineIR(f)
    while not r.empty:
        count = r >> CountEquals >> (firstLineOfGroup := r.front)
        out >> Put >> (firstLineOfGroup, count)
    return out.list


@Pipeable
def CountEquals(r, value):
    count = 0
    while not r.empty and r.front == value:
        count += 1
        r.popFront()
    return count



def countLinesRanges3(f):
    return FileLineIR(f) >> RepititionCounter >> PushInto >> ListOR([]) >> GetAttr >> 'list'


@Pipeable
def RepititionCounter(r):
    return _RepititionCounter(r)

class _RepititionCounter(IInputRange):
    def __init__(self, r):
        self.r = r
    @property
    def empty(self):
        return self.r.empty
    @property
    def front(self):
        firstInGroup = self.r.front
        count = 0
        while not self.r.empty and self.r.front ==firstInGroup:
            count += 1
            self.r.popFront()
        return firstInGroup, count
    def popFront(self):
        pass





# "Jackson criticises the traditional version, claiming that it hides the relationships which exist between
# the input lines, compromising the program's understandability and maintainability by, for example,
# forcing the use of a special case for the first line and forcing another special case for a final output operation."

def countLinesJsp(f):
    answer = []

    line = f.readline()
    while line != '':
        count = 0
        firstLineOfGroup = line

        while line != '' and line == firstLineOfGroup:
            count += 1
            line = f.readline()
        answer.append((firstLineOfGroup, count))

    return answer