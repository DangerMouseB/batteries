#*******************************************************************************
#
#    Copyright (c) 2017 David Briant
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


from ..pmf_tools import RvAdd, Normalised, PoD, d6, Mix, ToXY
from ..testing import close


def test_alot():
    d4 = PoD(*[(1, 1), (2, 1), (3, 1), (4, 1)]) >> Normalised
    rv = d4 >> RvAdd >> d4
    assert rv[2] == 1/16

    mix = d4 >> Mix >> d6
    result = mix[1]
    expected = (1/4 + 1/6) / (4 * (1/4 + 1/6)  + 2 * 1/6)
    assert close(result, expected, 0.00001), '%s != %s' % (result, expected)

    assert (d4 >> ToXY)[0] == (1.0, 2.0, 3.0, 4.0)


def main():
    test_alot()
    print('pass')


if __name__ == '__main__':
    main()
