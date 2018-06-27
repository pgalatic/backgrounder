# author : Paul Galatic github.com/pgalatic
#
# class for getting user's post save path preference
#

import os
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from gui import config_subs

PADX = 20
PADY = 10


class Config_Path():
    """
    Used to get data path from user.
    """

    def __init__(self, frame_in):

        self.frame = tk.Frame(frame_in)
        self.frame.pack(fill=tk.X, pady=PADY)
        frame = self.frame

        self.install_input = tk.StringVar(frame)
        self.image_input = tk.StringVar(frame)
        
        install_lbl = tk.Label(
            frame, text='[IN PROGRESS] Select an installation directory.')
        install_lbl.grid(row=0, column=0, sticky=tk.W)
        
        install_txt = tk.Entry(
            frame, textvariable=self.install_input, width=50)
        install_txt.grid(row=1, column=0, sticky=tk.W)

        image_lbl = tk.Label(
            frame, text='Select a folder to store images in.')
        image_lbl.grid(row=2, column=0, sticky=tk.W)

        image_txt = tk.Entry(
            frame, textvariable=self.image_input, width=50)
        image_txt.grid(row=3, column=0, sticky=tk.W)

        dir_installer = lambda: self.request_directory(install_txt)
        dir_image = lambda: self.request_directory(image_txt)
        
        tk.Button(
            frame,
            text='...',
            width=5,
            command=dir_installer
        ).grid(row=1, column=1, sticky=tk.E, padx=PADX)
        
        tk.Button(
            frame,
            text='...',
            width=5,
            command=dir_image
        ).grid(row=3, column=1, sticky=tk.E, padx=PADX)
        
    def request_directory(self, txt):
        """
        Displays a prompt for the user to select a directory. Once selected,
        that information is stored in an Entry.
        """
        filepath = filedialog.askdirectory(
            parent=self.frame,
            initialdir=os.getcwd(),
            title='Please select a folder:'
        )

        txt.delete(0, 'end')

        txt.insert(0, filepath)

    def get_path_input(self):
        dict = {}
        dict['install'] = str(self.install_input.get())
        dict['image'] = str(self.image_input.get())
        return dict
