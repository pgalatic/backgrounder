# author: Paul Galatic github.com/pgalatic
#
# main file
#

import os
import sys
import ctypes
import loader
import download
import win32event
import win32service
import servicemanager
import win32serviceutil
from data import Data

DEBUG = True

class Backgrounder():
    def __init__(self, dat):
        self._dat = dat
    
    def get_timing_pref(self):
        return self._dat.configdata['timing']
    
    def activate(self):
        download.grab_images(self._dat)
        loader.write_data(self._dat)

class AppServerSvc (win32serviceutil.ServiceFramework):
    """
    Runs the script as a Windows service. Edited from the original to add 
    functionality and flexibility.
    
    source https://stackoverflow.com/questions/32404/how-do-you-run-a-python-script-as-a-service-in-windows?rq=
    """
    _svc_name_ = "Backgrounder"
    _svc_display_name_ = "Backgrounder"

    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self,args)
        socket.setdefaulttimeout(60)
        
        self._hWaitStop = win32event.CreateEvent(None,0,0,None)

    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        win32event.SetEvent(self._hWaitStop)

    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                              servicemanager.PYS_SERVICE_STARTED,
                              (self._svc_name_,''))
                
        rc = None
        while rc != win32event.WAIT_OBJECT_0:
            # run, then wait
            wait = run()
            rc = win32event.WaitForSingleObject(self.hWaitStop, wait)
        
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False
    
def run():
    """
    Main function. If there is no save data, run the loader and generate save 
    data.
    """
    # request admin and rerun if not admin

    
    dat = loader.read_data(DEBUG)
    if dat is None:
        return
    
    backgrounder = Backgrounder(dat)
    backgrounder.activate()
    
    return backgrounder.get_timing_pref()

if __name__ == '__main__':
    if DEBUG:
        run()
    else:
        # TODO : https://mail.python.org/pipermail/python-win32/2010-July/010648.html
        if len(sys.argv) == 1:
            servicemanager.Initialize()
            servicemanager.PrepareToHostSingle(AppServerSvc)
            servicemanager.StartServiceCtrlDispatcher()
        else:
            win32serviceutil.HandleCommandLine(AppServerSvc)
