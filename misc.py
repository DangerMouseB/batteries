import sys
from functools import wraps

def onErrorReturnDescription(fn):
    @wraps(fn)
    def wrapper(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except Exception:
            et, ev, tb = sys.exc_info()
            return "%s" % ev
    return wrapper
