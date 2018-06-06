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

    def __init__(self, frame):

        self.frame = tk.Frame(frame)
        self.frame.pack(fill=tk.X, pady=PADY)

        self.input = tk.StringVar(self.frame)

        self.lbl = tk.Label(
            self.frame, text='Select a folder to store images in.')
        self.lbl.grid(row=0, column=0, sticky=tk.W)

        self.txt = tk.Entry(
            self.frame, textvariable=self.input, width=50)
        self.txt.grid(row=1, column=0, sticky=tk.W)

        self.btn = tk.Button(
            self.frame,
            text='...',
            width=5,
            command=lambda: self.request_directory()
        )
        self.btn.grid(row=1, column=1, sticky=tk.E, padx=PADX)

    def request_directory(self):
        """
        Displays a prompt for the user to select a directory. Once selected,
        that information is stored in an Entry.
        """
        filepath = filedialog.askdirectory(
            parent=self.frame,
            initialdir=os.getcwd(),
            title='Please select a folder:'
        )

        self.txt.delete(0, 'end')

        self.txt.insert(0, filepath)

    def get_path_input(self):
        return self.input.get()
