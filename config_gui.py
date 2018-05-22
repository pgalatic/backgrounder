# author : Paul Galatic github.com/pgalatic
#
# class for any elements involving graphical user interface
#

import os
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog

# Default options available to users
DEFAULTS = {'Wallpaper'				: 'General wallpapers',
			'Wallpapers'			: 'General pop culture wallpapers', 
			'MinimalWallpaper'		: 'Minimalist wallpapers',
			'Hi_Res'				: 'High resolution wallpapers',
			'EarthPorn'				: 'Images of nature',
			'BackgroundArt'			: 'Images of art'}
			
PADX = 20
PADY = 10

class Config_GUI():
	"""
	Module used to get configuration data from user.
	
	The configuration data isn't processed, only reported back to the main
	program.
	"""
	def __init__(self):
		"""
		Main GUI window. Creates all elements for the user to interact with.
		"""
		root = tk.Tk()
		root.title('Backgrounder')
	
		topframe = tk.Frame(root)
		topframe.pack(padx=PADX, pady=PADY)
		
		botframe = tk.Frame(root)
		botframe.pack(padx=PADX)
		
		# Get input for file path
		
		filepath_frame = tk.Frame(topframe)
		filepath_frame.pack(fill=tk.X, pady=PADY)
		
		filepath_input = tk.StringVar(filepath_frame)
		
		filepath_lbl = tk.Label(filepath_frame, text='Select a folder to store images in.')
		filepath_lbl.grid(row=0, column=0, sticky=tk.W)
		
		filepath_btn = tk.Button(filepath_frame, text='Choose', width=10, command=lambda: self.request_directory())
		filepath_btn.grid(row=0, column=1, sticky=tk.E, padx=PADX)
		
		filepath_txt = tk.Entry(filepath_frame, textvariable=filepath_input, width=50)
		filepath_txt.readonly = True
		filepath_txt.grid(row=1, column=0, sticky=tk.W)
		
		# Get input for subreddit preferences
		
		subreddits_frame = tk.Frame(topframe)
		subreddits_frame.pack(fill=tk.X, pady=PADY)
		
		subreddits_lbl = tk.Label(subreddits_frame, text='Select which subreddits to pull images from.')
		subreddits_lbl.grid(row=0, column=0)
		
		i = 0
		subreddit_vars = [tk.IntVar() for subreddit in DEFAULTS]
		for subreddit, description in DEFAULTS.items():
			tk.Checkbutton(
				subreddits_frame, 
				text=subreddit, 
				variable=subreddit_vars[i]
			).grid(row=1+i, column=0, sticky=tk.W)
			
			tk.Label(
				subreddits_frame, 
				text=description
			).grid(row=1+i, column=1, sticky=tk.E)
			
			i += 1
		
		# Get input for top post saving preferences
		
		postsave_frame = tk.Frame(topframe)
		postsave_frame.pack(fill=tk.X, pady=PADY)
		
		postsave_lbl = tk.Label(postsave_frame, text='Select how you would like posts to be saved.')
		postsave_lbl.grid(row=0, column=0, sticky=tk.W)
		
		postsave_var = tk.IntVar()
		postsave_var.set(-1)
		
		tk.Radiobutton(	
					postsave_frame, 
					text='Select top post from all selected subreddits', 
					variable=postsave_var,
					value=0
				).grid(row=1, column=0, sticky=tk.W)
		
		tk.Radiobutton(
					postsave_frame,
					text='Select all top posts from all selected subreddits',
					variable=postsave_var,
					value=1
				).grid(row=2, column=0, sticky=tk.W)
		
		tk.Radiobutton(
					postsave_frame,
					text='Select top post from a random subreddit among those selected',
					variable=postsave_var,
					value=2
				).grid(row=3, column=0, sticky=tk.W)
		
		# TODO : Add config for min time between runs
		
		# Close button
		
		close_btn = tk.Button(botframe, text='Finish', command=lambda: self.validate_input())
		close_btn.grid(row=0, column=1, pady=PADY)
		
		# Store relevant state info
		
		self.root = root
		self.topframe = topframe
		self.filepath_input = filepath_input
		self.filepath_txt = filepath_txt
		self.subreddit_vars = subreddit_vars
		self.postsave_var = postsave_var
		
		self.installation_completed = False
		
	def activate(self):
		"""
		Activates the GUI and displays it to the user. Collects data afterward.
		
		return: the configuration data the user submitted
		"""
		configdata = {}
		
		self.root.mainloop()
		
		configdata['filepath'] = self.get_filepath_input()
		configdata['subreddits'] = self.get_subreddit_input()
		configdata['postsave'] = self.get_postsave_input()
		
		return configdata
		
	def request_directory(self):
		"""
		Displays a prompt for the user to select a directory. Once selected, 
		that information is stored in an Entry.
		"""
		filepath = filedialog.askdirectory(
					parent=self.root,
					initialdir=os.getcwd(),
					title='Please select a folder:'
				)
		self.filepath_txt.delete(0, 'end')
		self.filepath_txt.insert(0, filepath)
	
	def get_filepath_input(self):
		"""Returns a string -- where the user chose to store theiri images."""
		return self.filepath_input.get()
	
	def get_subreddit_input(self):
		"""Returns a list of strings -- subreddits the user chose"""
		subreddits = []
		i = 0
		for subreddit in DEFAULTS:
			if self.subreddit_vars[i].get() == 1:
				subreddits.append(subreddit)
			i += 1
		
		return subreddits
	
	def get_postsave_input(self):
		"""Returns an integer -- which post saving method the user chose"""
		return self.postsave_var.get()
	
	def validate_input(self):
		"""
		Validates that the user's input was legitimate.
		
		This function checks to make sure all the input is valid before 
		allowing the installer to progress. If all the data is valid, it notes
		that in the state of the GUI.
		"""
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
			self.installation_completed = True
			self.root.destroy()
			
def main():
	"""Runs the GUI and reports what the user enters, for debugging."""
	
	configdata = Config_GUI().activate()
	
	for key, value in configdata.items():
		print(str(key) + ' : ' + str(value))
	
if __name__ == '__main__':
	main()