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


from batteries.testing import AssertEqual
from ..count_lines_jsp import countLinesJsp, countLinesTrad, countLinesRanges1, countLinesRanges2, countLinesRanges3


home = '/Users/david/shared/repos/github/DangerMouseB/anotherworld/examples/tests/'
filename = "linesForCounting.txt"
expected = [
    ('aaa\n', 2),
    ('bb\n', 1),
    ('aaa\n', 1),
    ('bb\n', 3),
    ('aaa\n', 1)
]

def main():
    with open(home + filename) as f:
        actual = countLinesJsp(f)
    actual >> AssertEqual >> expected

    with open(home + filename) as f:
        actual = countLinesTrad(f)
    actual >> AssertEqual >> expected

    with open(home + filename) as f:
        actual = countLinesRanges1(f)
    actual >> AssertEqual >> expected

    with open(home + filename) as f:
        actual = countLinesRanges2(f)
    actual >> AssertEqual >> expected

    with open(home + filename) as f:
        actual = countLinesRanges3(f)
    actual >> AssertEqual >> expected

    print('pass')


if __name__ == '__main__':
    main()


