# author : Paul Galatic github.com/pgalatic
#
# class for any elements involving graphical user interface
#

import os
import tkinter as tk
from tkinter import messagebox
from tkinter import filedialog
from gui import config_path
from gui import config_subs
from gui import config_save
from gui import config_timing

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

        self.config_path = config_path.Config_Path(topframe)

        # add subreddit preferences from module

        self.config_subs = config_subs.Config_Subs(topframe)

        # Get input for top post saving preferences

        self.config_save = config_save.Config_Save(topframe)

        # Config for min time between runs

        self.config_timing = config_timing.Config_Timing(topframe)
        
        # other options
        
        other_options_frame = tk.Frame(topframe)
        other_options_frame.pack(fill=tk.X, pady=PADY)
        
        duplicates_var = tk.IntVar()
        duplicates_box = tk.Checkbutton(
                            other_options_frame, 
                            text='Ignore duplicates', 
                            variable=duplicates_var
                        )
        duplicates_box.grid(row=0, column=0, sticky=tk.W)

        # Close button

        close_btn = tk.Button(botframe, text='Finish',
                              command=lambda: self.validate_input())
        close_btn.grid(row=0, column=1, pady=PADY)

        # Store relevant state info

        # GUI elements
        self.root = root
        self.duplicates_var = duplicates_var

        # Internal state
        self.installation_completed = False

    def convert_timing_to_seconds(self, dict):
        """Converts user timing pref dict into an amount of seconds"""
        if dict['unit'] == 'SECONDS':
            unit = 1
        elif dict['unit'] == 'HOURS':
            unit = 3600
        elif dict['unit'] == 'DAYS':
            unit = 86400
        else:
            raise Exception('Unit choice not recognized: ' + timing['unit'])
            
        return int(dict['value']) * unit    
    
    def activate(self):
        """
        Activates the GUI and displays it to the user. Collects data afterward.

        return: the configuration data the user submitted
        """
        configdata = {}

        self.root.mainloop()
        
        timing_dict = self.get_timing_pref()

        configdata['filepath'] = self.get_filepath_input()
        configdata['subreddits'] = self.get_subreddit_input()
        configdata['postsave'] = self.get_postsave_input()
        configdata['timing'] = self.convert_timing_to_seconds(timing_dict)
        configdata['other'] = self.get_other_options()

        return configdata

    def get_filepath_input(self):
        """Returns a string -- where the user chose to store their images."""
        return self.config_path.get_path_input()

    def get_subreddit_input(self):
        """Returns a list of strings -- subreddits the user chose"""
        return self.config_subs.get_subreddit_input()

    def get_postsave_input(self):
        """Returns an integer -- which post saving method the user chose"""
        return self.config_save.get_save_pref()

    def get_timing_pref(self):
        """Returns a dict -- describes the min time between saving images"""
        return self.config_timing.get_timing_pref()
    
    def get_other_options(self):
        """Returnsa dict -- describes extraneous checkbox options"""
        dict = {}
        dict['ignore_duplicates'] = self.duplicates_var.get()
        
        return dict

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
        timing_valid = False

        # is the chosen filepath a valid directory?
        filepath = self.get_filepath_input()
        if os.path.isdir(filepath):
            filepath_valid = True

        # was at least one subreddit chosen?
        subreddits = self.get_subreddit_input()
        if len(subreddits) > 0:
            subreddits_valid = True

        # was a postsave setting selected?
        postsave = self.get_postsave_input()
        if postsave >= 0:
            postsave_valid = True

        # is the entered time an integer?
        timing = self.get_timing_pref()
        if timing['value'].isdigit():
            timing_valid = True

        # warn user
        if not filepath_valid:
            tk.messagebox.showinfo(
                'Warning', 'Chosen filepath is not a valid directory. Please choose a new filepath.')
        elif not subreddits_valid:
            tk.messagebox.showinfo(
                'Warning', 'Please choose at least one subreddit.')
        elif not postsave_valid:
            tk.messagebox.showinfo(
                'Warning', 'Please choose a method by which to have your posts saved.')
        elif not timing_valid:
            tk.messagebox.showinfo(
                'Warning', 'Please enter an integer in the \"time between runs\" window.')
        else:
            self.installation_completed = True
            self.root.destroy()


if __name__ == '__main__':
    """DEPRECATED"""
    # TODO : Move testing for GUI package back into GUI package
    print("DEPRECATED")
