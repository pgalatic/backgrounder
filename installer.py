# author: Paul Galatic github.com/pgalatic
#
# functionality for first-time app setup
#

import os
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog

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
	
	return dict