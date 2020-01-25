#*******************************************************************************
#
#    Copyright (c) 2011-2012 David Briant
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



from ..testing import StdoutHooker, AssertRaises


def testStdoutHooker():
    lines = []
    h = StdoutHooker(lines)
    with h:
        print("hello")
        assert len(lines) == 1, lines
        assert lines[0] == "hello", lines
        print()
        print("there", "is", "\n", "another line\nagain")
        print()
        assert len(lines) == 6, lines
        assert lines[2] == "there is ", lines
        assert lines[3] == "another line", lines
        assert lines[4] == "again", lines
        assert lines[5] == "", lines


def testAssertRaises():
    
    # test correct error
    with AssertRaises(NotImplementedError) as e:
        raise NotImplementedError()
    assert e.exceptionType == NotImplementedError, (e.type, e.e)
    
    # test correct error
    with AssertRaises(NotImplementedError) as e:
        raise NotImplementedError
    assert e.exceptionType == NotImplementedError, (e.type, e.e)
    
    # test no error
    try:
        with AssertRaises(NotImplementedError) as e:
            pass
    except AssertionError:
        assert e.exceptionType == None, (e.type, e.e)
    except Exception as e:
        assert False, e
    
    # test wrong error
    class Fred(Exception): pass
    try:
        with AssertRaises(NotImplementedError) as e:
            raise Fred
    except AssertionError:
        assert e.exceptionType == Fred, (e.exceptionType, e.e)
    except Exception as e:
        assert False, e


def main():
    testStdoutHooker()
    testAssertRaises()
    print('pass')


if __name__ == '__main__':
    main()

