# author: Paul Galatic github.com/pgalatic
#
# functionality for first-time app setup
#

import os
import datetime
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from win32com.client import Dispatch

VERSION = '0.2'

def create_shortcut():
	# Locate path to folder that automatically starts scripts
	basepath = os.path.expanduser('~')
	startpath = basepath + '\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup'
	if not os.path.isdir(startpath):
		# TODO : Allow user to select start path
		raise Exception('Could not find start path. Aborting')
	
	# Create shortcut to script
	shell = Dispatch('WScript.Shell')
	execpath = os.getcwd() + '\\backgrounder_v' + VERSION + '.exe'
	shortcut = shell.CreateShortcut(startpath + '\\backgrounder_v' + VERSION + '.lnk')
	shortcut.Targetpath = execpath
	shortcut.WorkingDirectory = os.getcwd()
	shortcut.IconLocation = execpath
	shortcut.save()

def install():
	dict = {}
	
	root = tk.Tk()
	root.withdraw()
	
	# ask for path to images folder
	tk.messagebox.showinfo('Backgrounder', 'Save file not found.\n\nPlease enter the folder where you would like images stored.')
	
	picture_path = filedialog.askdirectory(parent=root,
										   initialdir=os.getcwd(),
										   title="Please select a folder:")
	
	dict['picture_path'] = picture_path
	dict['image_id'] = 0
	dict['last_run_datetime'] = datetime.datetime.now()
	
	create_shortcut()
	
	return dict