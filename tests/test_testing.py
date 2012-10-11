from batteries.testing import StdoutHooker, AssertRaises


def testStdoutHooker():
    lines = []
    h = StdoutHooker(lines)
    with h:
        print "hello"
        assert len(lines) == 1, lines
        assert lines[0] == "hello", lines
        print
        print "there", "is", "\n", "another line\nagain"
        print
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
    
