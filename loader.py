# author: Paul Galatic github.com/pgalatic
#
# functionality for saving / loading data
#

import os
import pickle
import datetime
import configparser
from data import Data
from ast import literal_eval
from gui import config_gui
from win32com.client import Dispatch

VERSION = '0.5'

def create_shortcut():
	"""
	Creates a shortcut for the program.
	
	In order for the program to be run on startup automatically, we create and
	insert a shortcut into the Start folder of the Windows computer. When the
	computer starts, the shortcut invokes the program
	"""
	# Locate path to folder that automatically starts scripts
	basepath = os.path.expanduser('~')
	startpath = basepath + '\\AppData\\Roaming\\Microsoft\\Windows\\Start Menu\\Programs\\Startup'
	if not os.path.isdir(startpath):
		# TODO : Allow user to select start path
		raise Exception('Could not find start path. Aborting')
	
	# Create shortcut to script
	shell = Dispatch('WScript.Shell')
	execpath = os.getcwd() + '\\backgrounder_v' + VERSION + '.exe' # path to script
	shortcut = shell.CreateShortcut(startpath + '\\backgrounder_v' + VERSION + '.lnk')
	shortcut.Targetpath = execpath
	shortcut.WorkingDirectory = os.getcwd()
	shortcut.IconLocation = execpath
	shortcut.save()
	
def write_config_file(configdata):
	"""
	Takes config data and writes it to an ini file.
	
	Arguments:
	configdata -- configuration data; assumes it is filled
	"""
	config = configparser.ConfigParser(allow_no_value=True)
	
	# file path preferences
	
	filepath = configdata['filepath']
	config.add_section('filepath')
	config.set('filepath', '# where images will be saved')
	config.set('filepath', 'filepath', filepath)
	
	# subreddit preferences
	
	subreddits = str((configdata['subreddits'])) # create delimited list of subs
	config.add_section('subreddits')
	config.set('subreddits', '# list of subreddits to pull from')
	config.set('subreddits', 'subreddits', str(subreddits))
	
	# post saving preferences
	
	postsave = configdata['postsave']
	config.add_section('postsave')
	config.set('postsave', '# method by which the posts will be saved')
	config.set('postsave', 'method', str(postsave))
	
	with open('backgrounder.ini', 'w') as file:
		config.write(file)

def read_config_file():
	"""Reads the backgrounder.ini file and imports settings from it."""
	config = configparser.ConfigParser(allow_no_value=True)
	configdata = {}
	
	config.read('backgrounder.ini')
	
	configdata['filepath'] = config['filepath']['filepath']
	configdata['subreddits'] = literal_eval(config['subreddits']['subreddits'])
	configdata['postsave'] = int(config['postsave']['method'])
	
	return configdata
	
def install():
	"""Runs installation procedures."""
	dat = Data()
	GUI = config_gui.Config_GUI()
	
	dat.configdata = GUI.activate()
	
	# check to make sure the user didn't exit the installer manually
	if not GUI.installation_completed:
		print('WARN: Installation could not successfully validate. Aborting.')
		return None
	
	write_config_file(dat.configdata)
	
	dat.userdata['image_id'] = 0
	dat.userdata['last_run_datetime'] = datetime.datetime.now()
	
	create_shortcut()
	
	return dat

def read_data():
	"""
	Reads and returns save data. If no save data exists, runs and returns the
	result of the installation procedure.
	
	return: a Dat object representing all user save and configuration data
	"""
	if os.path.isfile('data.pkl'):
		with open('data.pkl', 'rb') as input:
			dat = pickle.load(input)
			# use user config file if that file exists
			configdata = read_config_file()
			if configdata:
				dat.configdata = configdata
			else:
				write_config_file(dat.configdata)
			return dat
	else:
		return install()

def write_data(dat):
	"""Writes save data to disk. Overwrites any existing data."""
	with open('data.pkl', 'wb') as out:
		pickle.dump(dat, out, pickle.HIGHEST_PROTOCOL)
	
def main():
	"""Runs the GUI and reports what the user enters, for debugging."""
	
	configdata = config_gui.Config_GUI().activate()
	
	for key, value in configdata.items():
		print(str(key) + ' : ' + str(value))
	
if __name__ == '__main__':
	main()