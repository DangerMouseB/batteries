from batteries.parsing import uStrip

def test_uStrip():
    assert uStrip("  hell  o  ") == "HELLO"
