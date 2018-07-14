# author : Paul Galatic github.com/pgalatic
#
# class for any elements involving graphical user interface
#

# extra junk to make sure we can import from a parent directory
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
import os
import loader
import tkinter as tk
from gui import config_path
from gui import config_subs
from gui import config_save
from gui import config_timing
from gui.tooltip import Tooltip
from tkinter import messagebox
from tkinter import filedialog

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
        Tooltip(duplicates_box, \
            'If selected, the program will not download the same image more'
            'than once. Attempts to download duplicates will be logged.')
        
        imgur_var = tk.IntVar()
        imgur_box = tk.Checkbutton(
                        other_options_frame,
                        text='Download entire imgur gallery',
                        variable=imgur_var
        )
        imgur_box.grid(row=1, column=0, sticky=tk.W)
        Tooltip(imgur_box, \
            'If selected, if the top post happens to be an imgur album, the '
            'program will download the entire imgur album. This could result '
            'in the download of dozens of images, so be careful.')

        # Close button

        close_btn = tk.Button(botframe, text='Finish',
                              command=lambda: self.validate())
        close_btn.grid(row=0, column=1, pady=PADY)

        # Store relevant state info

        # GUI elements
        self.root = root
        self.duplicates_var = duplicates_var
        self.imgur_var = imgur_var

        # Internal state
        self.installation_completed = False
    
    def activate(self):
        """
        Activates the GUI and displays it to the user. Collects data afterward.

        return: the configuration data the user submitted
        """
        self.root.mainloop()
        
        return self.get_all_data()

    def get_path_input(self):
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
        dict['ignore_duplicates'] = str(self.duplicates_var.get())
        dict['download_gallery'] = str(self.imgur_var.get())
        
        return dict

    def get_all_data(self):
        data = {}
        data['path'] = self.get_path_input()
        data['subreddits'] = self.get_subreddit_input()
        data['postsave'] = self.get_postsave_input()
        data['timing'] = self.get_timing_pref()
        data['other'] = self.get_other_options()
        return data
        
    def validate(self):
        """
        Validates that the user's input was legitimate.

        This function checks to make sure all the input is valid before
        allowing the installer to progress. If all the data is valid, it notes
        that in the state of the GUI.
        """
        configdata = self.get_all_data()
        valid_dict = loader.validate_config(configdata)

        # warn user
        if not valid_dict['path']:
            tk.messagebox.showinfo(
                'Warning', 'Filepath is invalid. Please choose a new filepath.')
        elif not valid_dict['subreddits']:
            tk.messagebox.showinfo(
                'Warning', 'Please choose at least one subreddit.')
        elif not valid_dict['postsave']:
            tk.messagebox.showinfo(
                'Warning', 'Please choose a method by which to have your posts saved.')
        elif not valid_dict['timing']:
            tk.messagebox.showinfo(
                'Warning', 'Please enter an integer in the \"time between runs\" window.')
        elif not valid_dict['other']:
            tk.messagebox.showinfo(
                'Warning', 'There was an error in your \'other\' section. Please contact the app developer.')
        else:
            self.installation_completed = True
            self.root.destroy()


if __name__ == '__main__':
    """DEPRECATED"""
    # TODO : Move testing for GUI package back into GUI package
    print("DEPRECATED")
