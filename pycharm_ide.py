#************************************************************************************************************************************************
#
#    Copyright (c) 2011-2012 David Briant - see https://github.com/DangerMouseB
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU Lesser General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU Lesser General Public License for more details.
#
#    You should have received a copy of the GNU Lesser General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#************************************************************************************************************************************************

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
