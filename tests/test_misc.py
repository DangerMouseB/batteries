from batteries.misc import onErrorReturnDescription

def test1():
    @onErrorReturnDescription
    def fred():
        raise Exception("hello")
    result = fred()
    assert result == "hello", result
