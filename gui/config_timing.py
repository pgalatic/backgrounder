# author : Paul Galatic github.com/pgalatic
#
# class for getting user's desired min time between runs
#

import os
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from gui import config_subs
from gui.tooltip import Tooltip

PADX = 20
PADY = 10

CHOICES = ['SECONDS', 'HOURS', 'DAYS']
MIN_RUN_TIME = 300 # min five minutes between runs

class Config_Timing():
    """
    Used to get image saving preferences from user.
    """
    def __init__(self, frame):

        self.frame = tk.Frame(frame)
        self.frame.pack(fill=tk.X, pady=PADY)

        self.lbl = tk.Label(
            self.frame, text='Enter the minimum amount of time between downloads.')

        self.lbl.grid(row=0, column=0, sticky=tk.W)

        self.value = tk.StringVar(self.frame)
        self.value.set(0)
        self.choice = tk.StringVar(self.frame)
        self.choice.set(CHOICES[1])

        self.entry = tk.Entry(
                self.frame, textvariable=self.value, width=10)
        self.entry.grid(row=1, column=0, sticky=tk.W)
        Tooltip(self.entry, \
            'If Backgrounder is run before this amount of time has elapsed, '
            'it will not download an image. Helpful if you want to avoid '
            'downloading too many images. Minimum time: %d seconds.' \
            % MIN_RUN_TIME)

        self.dropdown = tk.OptionMenu(self.frame, self.choice, *CHOICES)
        self.dropdown.grid(row=1, column=1, sticky=tk.W)

    def convert(self, dict):
        """Converts user timing pref dict into an int amount of seconds"""
        
        try:
            int(dict['value'])
        except ValueError:
            return None # sentinel value -- will be picked up later

        if dict['unit'] == 'SECONDS':
            unit = 1
        elif dict['unit'] == 'HOURS':
            unit = 3600
        elif dict['unit'] == 'DAYS':
            unit = 86400
        else:
            raise Exception('Unit choice not recognized: ' + timing['unit'])
        
        return max(int(dict['value']) * unit, MIN_RUN_TIME)
        
    def get_timing_pref(self):
        """
        Returns a string describing the user's chosen options, in seconds.
        """
        value = str(self.value.get())
        unit = str(self.choice.get())
        
        return str(self.convert({'value': value, 'unit': unit}))

