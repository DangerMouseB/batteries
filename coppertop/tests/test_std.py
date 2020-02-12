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



from ..testing import AssertEqual
from ..pipeable import Pipeable
from coppertop._std import Chain, Each, EachArgs

def test_stuff():
    2 >> AssertEqual >> 2

    @Pipeable
    def SquareIt(x):
        return x * x

    @Pipeable
    def Add(x, y):
        return x + y

    [1,2,3] >> Each >> SquareIt >> Chain(seed=0) >> Add >> AssertEqual >> 14

    [[1,2], [2,3], [3,4]] >> EachArgs >> Add >> AssertEqual >> [3, 5, 7]



def main():
    test_stuff()
    print('pass')


if __name__ == '__main__':
    main()

