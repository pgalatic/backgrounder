# author: Paul Galatic github.com/pgalatic
#
# functionality for first-time app setup
#

import os
import datetime
import configparser
import tkinter as tk
from data import Data
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
	
def create_config_file(settings):
	config = configparser.ConfigParser()
	
	config.add_section('subreddits')
	config.set('subreddits', '# list of subreddits to pull from')
	subslist = ','.join(settings['subreddits']) # create delimited list of subs
	config.set('subreddits', 'subreddits', subslist)
	
	with open('backgrounder.ini') as file:
		config.write(file)
		
def request_config():
	configdata = {}
	
	print('yes')
	
	root = tk.Tk()
	root.title('Backgrounder')
	
	frame = tk.Frame(root, height=500, width=500)
	frame.pack()
	
	filepath_lbl = tk.Label(frame, text='Select a folder to store images in.')
	filepath_lbl.grid(row=0, column=0)
	
	filepath_btn = tk.Button(frame, text='Set', command=request_directory(root, configdata))
	filepath_btn.grid(row=0, column=1)
	
	print('yes2')
	
	root.mainloop()
	
	print('yes3')

def request_directory(root, configdata):
	configdata['picture_path'] = filedialog.askdirectory(
									parent=root,
									initialdir=os.getcwd(),
									title='Please select a folder:'
								)
	
def install():	
	tk.messagebox.showinfo('Backgrounder', 'Save file not found.\n\n'
										   'Running installer.')
	
	dat = Data()
	
	dat.configdata = request_config()
	create_config_file(dat.configdata)
	
	dat.userdata['image_id'] = 0
	dat.userdata['last_run_datetime'] = datetime.datetime.now()
	
	create_shortcut()
	
	return dat
	
def main():
	"""Tests the GUI, for debugging."""
	
	configdata = request_config()
	
	for key, value in configdata.items():
		print(str(key) + ' : ' + str(value))
	
if __name__ == '__main__':
	main()