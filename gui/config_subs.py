# author: Paul Galatic github.com/pgalatic
#
# Manages GUI for default subreddits and custom subreddits
#

# extra junk to make sure we can import from a parent directory
from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from reddit import Reddit

import tkinter as tk

# Default options available to users
DEFAULTS = {'Wallpaper'				: 'General wallpapers',
            'Wallpapers'			: 'General pop culture wallpapers',
            'MinimalWallpaper'		: 'Minimalist wallpapers',
            'Hi_Res'				: 'High resolution wallpapers',
            'EarthPorn'				: 'Images of nature',
            'BackgroundArt'			: 'Images of art'}

PADX = 20
PADY = 10


class Config_Subs():
    """
    Creates GUI elements and stores state related to the user selecting default
    or custom subreddits to pull images from.
    """

    def __init__(self, frame):
        """
        Generates the GUI elements and places them into the provided frame.
        """
        # Get input for subreddit preferences

        subreddits_frame = tk.Frame(frame)
        subreddits_frame.pack(fill=tk.X, pady=PADY)

        subreddits_lbl = tk.Label(
            subreddits_frame, text='Select which subreddits to pull images from.')
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

        # Get input for custom subreddit

        customsub_frame = tk.Frame(frame)
        customsub_frame.pack(fill=tk.X, pady=PADY)

        customsub_lbl = tk.Label(
            customsub_frame, text='BETA: (Optional) Enter a custom subreddit.')
        customsub_lbl.grid(row=0, column=0, sticky=tk.W)

        customsub_input = tk.StringVar(customsub_frame)

        customsub_txt = tk.Entry(
            customsub_frame, textvariable=customsub_input, width=30)
        customsub_txt.grid(row=1, column=0, sticky=tk.W)

        customsub_btn = tk.Button(
            customsub_frame, text='Add', width=10, command=lambda: self.add_custom_subreddit())
        customsub_btn.grid(row=1, column=1, sticky=tk.E)

        # Store relevant state

        self.subreddit_vars = subreddit_vars
        self.customsub_txt = customsub_txt
        self.customsub_frame = customsub_frame
        self.customsub_input = customsub_input

        self.reddit = Reddit().reddit
        self.customsub_num = 0
        self.customsubs = {}

    def add_custom_subreddit(self):
        """TODO"""

        # TODO : Make sure the subreddit only has image posts

        subname = self.customsub_input.get()

        # determine if subreddit exists
        subreddit_valid = True

        if subname == "" or subname is None:
            subreddit_valid = False

        if subname in self.customsubs:
            subreddit_valid = False

        try:
            self.reddit.subreddits.search_by_name(subname, exact=True)
        except:
            subreddit_valid = False

        if not subreddit_valid:
            tk.messagebox.showinfo(
                'Warning',
                'It does not appear that the subreddit you is valid.\n\n' +
                'If you think this is an error, please contact the app creator.'
            )
            return

        # add checkbox for custom subreddit

        var = tk.IntVar()
        var.set(1)
        customsub_box = tk.Checkbutton(
            self.customsub_frame, text=subname, variable=var)
        customsub_box.grid(row=2+self.customsub_num, column=0, sticky=tk.W)
        self.customsubs[subname] = var

        customsub_lbl = tk.Label(self.customsub_frame, text='Custom subreddit')
        customsub_lbl.grid(row=2+self.customsub_num, column=1, sticky=tk.E)

        self.customsub_num += 1
        self.customsub_txt.delete(0, 'end')
        return

    def get_subreddit_input(self):
        """Returns a list of strings -- subreddits the user chose"""
        subreddits = []
        i = 0
        for subreddit in DEFAULTS:
            if self.subreddit_vars[i].get() == 1:
                if subreddit not in subreddits:
                    subreddits.append(subreddit)
            i += 1

        for name in self.customsubs:
            if self.customsubs[name].get():
                if name not in subreddits:
                    subreddits.append(name)

        return subreddits
