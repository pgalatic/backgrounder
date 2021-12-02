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

class Backgrounder():
    def __init__(self, dat):
        self._dat = dat
    
    def get_timing_pref(self):
        return self._dat.configdata['timing']
    
    def activate(self):
        download.grab_images(self._dat)
        loader.write_data(self._dat)
        
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
    dat = loader.read_data()
    if dat is None:
        return
    
    backgrounder = Backgrounder(dat)
    backgrounder.activate()
    
    return backgrounder.get_timing_pref()

if __name__ == '__main__':
    run()

