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
