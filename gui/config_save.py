# author : Paul Galatic github.com/pgalatic
#
# class for getting user's post saving method
#

import os
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from gui import config_subs

PADX = 20
PADY = 10


class Config_Save():
    """
    Used to get image saving preferences from user.
    """

    def __init__(self, frame):

        self.frame = tk.Frame(frame)
        self.frame.pack(fill=tk.X, pady=PADY)

        self.lbl = tk.Label(
            self.frame, text='Select how you would like posts to be saved.')

        self.lbl.grid(row=0, column=0, sticky=tk.W)

        self.var = tk.IntVar()

        self.var.set(-1)

        tk.Radiobutton(
            self.frame,
            text='Select top post from all selected subreddits',
            variable=self.var,
            value=0
        ).grid(row=1, column=0, sticky=tk.W)

        tk.Radiobutton(
            self.frame,
            text='Select all top posts from all selected subreddits',
            variable=self.var,
            value=1
        ).grid(row=2, column=0, sticky=tk.W)

        tk.Radiobutton(
            self.frame,
            text='Select top post from a random subreddit among those selected',
            variable=self.var,
            value=2
        ).grid(row=3, column=0, sticky=tk.W)

    def get_save_pref(self):
        return str(self.var.get())

