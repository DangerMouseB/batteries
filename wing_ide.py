#from __future__ import absolute_import
#from .time import time, strftime, gmtime
import time, types, sys, traceback, os, imp, types


debugger = None
DBLogFilename = None
WingLogFilename = None
START_STOP = True

def logToWing(text):
    if WingLogFilename is not None:
        try:
            f = open(WingLogFilename, "a")
            f.write(text)
        finally:
            if f: f.close()

def logToDB(text):
    if DBLogFilename is not None:
        try:
            f = open(DBLogFilename, "a")
            f.write(text)
        finally:
            if f: f.close()

def tbToDB(tb):
    if DBLogFilename is not None:
        try:
            f = open(DBLogFilename, "a")
            traceback.print_tb(tb, file=f)
        finally:
            if f: f.close()

def stackToDB():
    if DBLogFilename is not None:
        try:
            f = open(DBLogFilename, "a")
            traceback.print_stack(file=f)
        finally:
            if f: f.close()


def _ImportWingdb(winghome, user_settings=None):
    """ Find & import the python version appropriate wingdb module. """

    try:
        exec_dict = {}
        execfile(os.path.join(winghome, 'bin', '_patchsupport.py'), exec_dict)
        find_matching = exec_dict['FindMatching']
        dir_list = find_matching('bin', winghome, user_settings)
    except Exception:
        dir_list = []
    dir_list.extend([os.path.join(winghome, 'bin'), os.path.join(winghome, 'src')])
    for path in dir_list:
        try:
            f, p, d = imp.find_module('wingdb', [path])
            try:
                return imp.load_module('wingdb', f, p, d)
            finally:
                if f is not None:
                    f.close()
            break
        except ImportError:
            pass


def createWingDebugger(host, port, listenPort, pwfile_path=None, pwfile_name=None, winghome=None, autoquit=1, logfile=None, very_verbose_log = 0, userSettingsDir=None):

    # A bit of defensive programming
    assert type(logfile) in (types.NoneType, str)
    assert type(very_verbose_log) == int
    assert type(host) == str
    assert type(port) == int
    assert type(listenPort) == int
    assert type(pwfile_path) in (list, str, types.NoneType)
    assert type(pwfile_name) in (str, types.NoneType)
    if type(logfile) == str:
        if logfile == '-' or len(logfile.strip()) == 0:
            logfile = None

    # Load wingdb.py
    if winghome == None:
        if os.environ.get("PROCESSOR_ARCHITEW6432", None) == "AMD64":
            winghome = r"C:\Program Files (x86)\Wing IDE 4.1"
        else:
            winghome = r"c:\Program Files\Wing IDE 4.1"
    wingdb = _ImportWingdb(winghome, userSettingsDir)
    if wingdb == None: raise RuntimeError('Cannot find wingdb.py in $(WINGHOME)/bin or $(WINGHOME)/src\n')

    # Find the netserver module and create an error stream
    netserver = wingdb.FindNetServerModule(winghome, userSettingsDir)
    errStream = wingdb.CreateErrStream(netserver, logfile, very_verbose_log)

    # Create debugger
    debugger = netserver.CNetworkServer(host, port, listenPort, errStream, pwfile_path=pwfile_path, pwfile_name=pwfile_name, autoquit=autoquit)
    os.environ['WINGDB_ACTIVE'] = "1"

    return debugger


def createDefaultDebugger(autoquit=1, logfile=None):
    global debugger
    debugger = createWingDebugger(
        host='localhost',
        port=50005,
        listenPort=50015,
        pwfile_path=[os.path.dirname(__file__), '$<winguserprofile>'],
        pwfile_name='wingdebugpw',
        winghome=r"C:\Program Files\Wing IDE 4.1",
        autoquit=autoquit,
        logfile=logfile)


def startWing():
    global START_STOP, DBLogFilename, WingLogFilename, debugger
    START_STOP = True
    OVERRIDE_PROGRAM_QUIT = False
    try:
        logToWing("##### DBStartWing start\n")
        if debugger is None:
            logToWing("##### Createing debugger start\n")
            try:
                DBLogFilename = r"c:\dev\_db.log"
                WingLogFilename = r"c:\dev\_wing.log"
                if os.environ.get("PROCESSOR_ARCHITEW6432", None) == "AMD64":
                    winghome = r"C:\Program Files (x86)\Wing IDE 4.1"
                else:
                    winghome = r"c:\Program Files\Wing IDE 4.1"
                debugger = createWingDebugger(
                    host='localhost',
                    port=50005,
                    listenPort=50015,
                    pwfile_path=[r"c:\mercury", '$<winguserprofile>'],
                    pwfile_name='wingdebugpw',
                    winghome=winghome,
                    autoquit=0,
                    logfile=WingLogFilename)
                debugger.StartDebug()
                if START_STOP:
                    debugger.StopDebug()
                else:
                    debugger.SuspendDebug()
                if OVERRIDE_PROGRAM_QUIT:
                    debugger.OldProgramQuit = debugger.ProgramQuit
                    def WrapProgramQuit(*args, **kwargs):
                        logToDB("IN PROGRAMQUIT WRAPPER\n")
                        stackToDB()
                        debugger.OldProgramQuit(*args, **kwargs)
                    debugger.ProgramQuit = WrapProgramQuit
                    #debugger.OldProgramQuit = debugger.ProgramQuit
                    #def ProgramQuit(self):
                    #    pass
                    #debugger.ProgramQuit = types.MethodType(ProgramQuit, debugger, debugger.__class__)
                logToDB(time.strftime("%I:%M:%S %p, %a %d %b %Y", time.gmtime(time.time())) + " - DBWing imported %s\n" % debugger)
            except Exception:
                t, v, tb = sys.exc_info()
                logToDB(time.strftime("%I:%M:%S %p, %a %d %b %Y", time.gmtime(time.time())) + " - Error importing DBWing (%s)\n" % traceback.format_exception_only(t, v)[0].strip())
                tbToDB(tb)
        if debugger is None:
            result = "#No debugger!"
        else:
            if debugger.ChannelClosed():
                logToWing("##### ConnectToClient\n")
                debugger.ConnectToClient()
            if debugger.ChannelClosed():
                notConnectedReport = " (Not connected)"
            else:
                notConnectedReport = ""
            if START_STOP:
                debugger.StartDebug()
            else:
                while debugger.ResumeDebug() > 0:
                    logToWing("##### ResumeDebug called\n")
            if debugger.DebugActive():
                logToWing("##### DebugActive\n")
                result = "Active%s" % notConnectedReport
            else:
                logToWing("##### not DebugActive\n")
                result = "#Not Active%s!" % notConnectedReport
        logToWing("##### DBStartWing end\n")
    except Exception:
        f = open(DBLogFilename, "a")
        t, v, tb = sys.exc_info()
        f.write(time.strftime("%I:%M:%S %p, %a %d %b %Y", time.gmtime(time.time())))
        f.write(" - Error calling DBStartWing (%s)\n" % traceback.format_exception_only(t, v)[0].strip())
        traceback.print_tb(tb, file=f)
        f.close()
        result = traceback.format_exception_only(t, v)[0].strip()
    return result

def stopWing():
    global debugger
    try:
        if debugger is None:
            result = "#No debugger!"
        else:
            if debugger.ChannelClosed(): debugger.ConnectToClient()
            if debugger.ChannelClosed():
                notConnectedReport = " (Not connected)"
            else:
                notConnectedReport = ""
            if START_STOP:
                debugger.StopDebug()
            else:
                debugger.SuspendDebug()
            if not debugger.DebugActive():
                result = "Not Active%s" % notConnectedReport
            else:
                result = "#Active%s!" % notConnectedReport
    except Exception:
        t, v, tb = sys.exc_info()
        logToDB(time.strftime("%I:%M:%S %p, %a %d %b %Y", time.gmtime(time.time())) + " - Error calling DBSuspendWing (%s)\n" % traceback.format_exception_only(t, v)[0].strip())
        tbToDB(tb)
        result = traceback.format_exception_only(t, v)[0].strip()
    return result

def dropWing():
    global debugger
    if debugger is not None:
        debugger.ProgramQuit()
        debugger = None
    result = "Dropped"



