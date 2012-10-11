"""@xl_func("int port : string", category="RainPlayDev")
def RPConnectToPyCharm(port):
    if port == 0: port = 30000
    try:
        if not pydevd.isGood(): reload(pydevd)
        pydevd.settrace(stdoutToServer=True,stderrToServer=True,port=port,suspend=False) #,suspend=True,trace_only_current_thread=True)
        return "Connected"
    except pydevd.RemoteDebuggerNotAvailable:
        return "Not connected"
    except Exception:
        return "Unknown error: %s" % e
"""
