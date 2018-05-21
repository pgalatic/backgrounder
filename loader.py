# author: Paul Galatic github.com/pgalatic
#
# functionality for first-time app setup
#

import os
import pickle
import datetime
import configparser
import tkinter as tk
from data import Data
from ast import literal_eval
from tkinter import messagebox
from tkinter import filedialog
from win32com.client import Dispatch

VERSION = '0.3'
DEFAULTS = {'Wallpaper'				: 'General wallpapers',
			'Wallpapers'			: 'General pop culture wallpapers', 
			'MinimalWallpaper'		: 'Minimalist wallpapers',
			'Hi_Res'				: 'High resolution wallpapers',
			'EarthPorn'				: 'Images of nature',
			'BackgroundArt'			: 'Images of art'}

class Config_GUI():
	""""""
	def __init__(self):
		root = tk.Tk()
		root.title('Backgrounder')
		root.geometry('500x500')
		root.borderwidth = 1
	
		topframe = tk.Frame(root, height=450, width=500)
		topframe.borderwidth = 20
		topframe.pack()
		
		botframe = tk.Frame(root, height=50, width=400)
		botframe.borderwidth = 20
		botframe.pack()
		
		# Get input for file path
		
		filepath_frame = tk.Frame(topframe, height=150, width=400)
		filepath_frame.borderwidth = 20
		filepath_frame.pack()
		
		filepath_input = tk.StringVar(filepath_frame)
		
		filepath_lbl = tk.Label(filepath_frame, text='Select a folder to store images in.')
		filepath_lbl.grid(row=0, column=0)
		
		filepath_btn = tk.Button(filepath_frame, text='Set', command=lambda: self.request_directory())
		filepath_btn.grid(row=0, column=1)
		
		filepath_txt = tk.Entry(filepath_frame, textvariable=filepath_input, width=50)
		filepath_txt.readonly = True
		filepath_txt.grid(row=1, column=0)
		
		# Get input for subreddit preferences
		
		subreddits_frame = tk.Frame(topframe, height=300, width=400)
		subreddits_frame.borderwidth = 20
		subreddits_frame.pack()
		
		subreddits_lbl = tk.Label(subreddits_frame, text='Select which subreddits to pull images from.')
		subreddits_lbl.grid(row=0, column=0)
		
		i = 0
		subreddit_vars = [tk.IntVar() for subreddit in DEFAULTS]
		for subreddit, description in DEFAULTS.items():
			tk.Checkbutton(subreddits_frame, text=subreddit, variable=subreddit_vars[i]).grid(row=1+i, column=0)
			tk.Label(subreddits_frame, text=description).grid(row=1+i, column=1)
			i += 1
		
		# Get input for top post saving preferences
		
		postsave_frame = tk.Frame(topframe, height=150, width=400)
		postsave_frame.borderwidth = 20
		postsave_frame.pack()
		
		postsave_lbl = tk.Label(postsave_frame, text='Select how you would like posts to be saved.')
		postsave_lbl.grid(row=0, column=0)
		
		postsave_var = tk.IntVar()
		postsave_var.set(-1)
		
		tk.Radiobutton(	
					postsave_frame, 
					text='Select top post from all selected subreddits', 
					variable=postsave_var,
					value=0
				).grid(row=1, column=0)
		
		tk.Radiobutton(
					postsave_frame,
					text='Select all top posts from all selected subreddits',
					variable=postsave_var,
					value=1
				).grid(row=2, column=0)
		
		tk.Radiobutton(
					postsave_frame,
					text='Select top post from a random subreddit among those selected',
					variable=postsave_var,
					value=2
				).grid(row=3, column=0)
		
		# Close button
		
		close_btn = tk.Button(botframe, text='Finish', command=lambda: self.validate_input())
		close_btn.grid(row=0, column=1)
		
		# Store relevant state info
		
		self.root = root
		self.topframe = topframe
		self.filepath_input = filepath_input
		self.filepath_txt = filepath_txt
		self.subreddit_vars = subreddit_vars
		self.postsave_var = postsave_var
		
	def activate(self):
		self.root.mainloop()
		
	def request_directory(self):
		filepath = filedialog.askdirectory(
					parent=self.root,
					initialdir=os.getcwd(),
					title='Please select a folder:'
				)
		self.filepath_txt.insert(0, filepath)
	
	def get_filepath_input(self):
		return self.filepath_input.get()
	
	def get_subreddit_input(self):
		subreddits = []
		i = 0
		for subreddit in DEFAULTS:
			if self.subreddit_vars[i].get() == 1:
				subreddits.append(subreddit)
			i += 1
		
		return subreddits
	
	def get_postsave_input(self):
		return self.postsave_var.get()
	
	def validate_input(self):
		# TODO: Validate config file
		filepath_valid = False
		subreddits_valid = False
		postsave_valid = False
	
		# is the chosen filepath a valid directory?
		filepath = self.get_filepath_input()
		if os.path.isdir(filepath):
			filepath_valid = True
		
		# was at least one subreddit chosen?
		subreddits = self.get_subreddit_input()
		if len(subreddits) > 0:
			subreddits_valid = True
		
		postsave = self.get_postsave_input()
		if postsave >= 0:
			postsave_valid = True
		
		# warn user
		if not filepath_valid:
			tk.messagebox.showinfo('Warning', 'Chosen filepath is not a valid directory. Please choose a new filepath.')
		elif not subreddits_valid:
			tk.messagebox.showinfo('Warning', 'Please choose at least one subreddit.')
		elif not postsave_valid:
			tk.messagebox.showinfo('Warning', 'Please choose a method by which to have your posts saved.')
		else:
			self.root.destroy()

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

def write_praw_ini():
	"""
	Creates a praw.ini file if one does not already exist.
	
	The Python-Reddit API Wrapper (PRAW) requires a .ini file in order to run.
	If that file is not present, the executable will fail. This function writes
	that file out for the user if it is not present (as I am not tempted to dig
	into Pyinstaller to figure out why it isn't being included in the exe file
	in the first place). The executable version is temperamental about actually
	writing the file, so temper with this function at your own risk.
	
	For more detail, visit:
	praw.readthedocs.io/en/latest/getting_started/configuration/prawini.html
	"""
	with open('praw.ini', 'w') as out:
		out.write('[DEFAULT]\ncheck_for_updates=True\ncomment_kind=t1\n')
		out.write('message_kind=t4\nredditor_kind=t2\nsubmission_kind=t3\n')
		out.write('subreddit_kind=t5\noauth_url=https://oauth.reddit.com\n')
		out.write('reddit_url=https://www.reddit.com\n')
		out.write('short_url=https://redd.it\n')
	
def write_config_file(configdata):
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
	config = configparser.ConfigParser(allow_no_value=True)
	configdata = {}
	
	config.read('backgrounder.ini')
	
	configdata['filepath'] = config['filepath']['filepath']
	configdata['subreddits'] = literal_eval(config['subreddits']['subreddits'])
	configdata['postsave'] = int(config['postsave']['method'])
	
	return configdata
		
def request_config():
	configdata = {}
	
	GUI = Config_GUI()
	GUI.activate()
	
	configdata['filepath'] = GUI.get_filepath_input()
	configdata['subreddits'] = GUI.get_subreddit_input()
	configdata['postsave'] = GUI.get_postsave_input()
	
	return configdata
	
def install():
	dat = Data()
	
	dat.configdata = request_config()
	write_config_file(dat.configdata)
	write_praw_ini()
	
	dat.userdata['image_id'] = 0
	dat.userdata['last_run_datetime'] = datetime.datetime.now()
	
	create_shortcut()
	
	return dat

def read_data():
	"""
	Reads and returns save data. If no save data exists, runs and returns the
	result of the installation procedure.
	"""
	if os.path.isfile('data.pkl'):
		with open('data.pkl', 'rb') as input:
			dat = pickle.load(input)
			dat.configdata = read_config_file()
			return dat
	else:
		return install()

def write_data(dat):
	"""Writes save data to disk. Overwrites any existing data."""
	with open('data.pkl', 'wb') as out:
		pickle.dump(dat, out, pickle.HIGHEST_PROTOCOL)
	
def main():
	"""Runs the GUI separate from the rest of the app, for debugging."""
	
	configdata = request_config()
	
	for key, value in configdata.items():
		print(str(key) + ' : ' + str(value))
	
if __name__ == '__main__':
	main()