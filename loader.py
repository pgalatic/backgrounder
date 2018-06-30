# author: Paul Galatic github.com/pgalatic
#
# functionality for saving / loading data
#

import os
import shutil
import pickle
import datetime
import configparser
from data import Data
from ast import literal_eval
from gui import config_gui
from tkinter import messagebox
from win32com.client import Dispatch

VERSION = '0.7'
MIN_RUN_TIME = 300 # min five minutes between runs

def create_shortcut(dat):
    """
    Creates a shortcut for the program.
    
    In order for the program to be run on startup automatically, we create and
    insert a shortcut into the Start folder of the Windows computer. When the
    computer starts, the shortcut invokes the program
    """
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
    
def write_config_file(configdata):
    """
    Takes config data and writes it to an ini file.
    
    Arguments:
    configdata -- configuration data; assumes it is filled
    """
    config = configparser.ConfigParser(allow_no_value=True)
    
    # file path preferences
    
    path = configdata['path']
    config.add_section('path')
    config.set('path', '# path to image directory')
    config.set('path', 'image', str(path['image']))
    
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
    
    # timing preferences
    
    seconds = configdata['timing']

    config.add_section('timing')
    config.set('timing', '# min number of seconds between saving images')
    config.set('timing', 'seconds', str(seconds))
    
    # other preferences
    
    other = configdata['other']
    config.add_section('other')
    config.set('other', '# other options')
    config.set('other', 'ignore_duplicates', str(other['ignore_duplicates']))
    config.set('other', 'download_gallery', str(other['download_gallery']))
    
    with open ('backgrounder.ini', 'w') as file:
        config.write(file)

def validate_config(configdata):
    """
    Takes configdata and returns a str:bool dict that explains which items are
    valid and which are not.
    """
    dict = {}
    dict['path'] = False
    dict['subreddits'] = False
    dict['postsave'] = False
    dict['timing'] = False
    dict['other'] = True

    # are the designated paths valid directories?
    path = configdata['path']
    if os.path.isdir(path['image']):
        dict['path'] = True

    # was at least one subreddit chosen?
    subreddits = configdata['subreddits']
    try:
        list = literal_eval(subreddits)
    
        if len(list) > 0:
            dict['subreddits'] = True
    except (ValueError, SyntaxError) as e:
        pass # string can't parse as a list

    # was a valid postsave setting selected?
    postsave = configdata['postsave']
    if postsave.isdigit() and 0 <= int(postsave) <= 2:
        dict['postsave'] = True

    # is the timing an integer with a valid accompanying unit?
    timing = configdata['timing']
    if timing.isdigit(): # -1 sentinel val for conversion error
        dict['timing'] = True
    
    # make sure other options are valid
    other = configdata['other']
    for key, val in other.items():
        if not (val == '0' or val == '1'):
            dict['other'] = False
            
    return dict

def process_configdata(configdata):
    """
    Post-processes configdata to bring it into the form the program expects.
    Should only be done once the configdata is validated.
    """
    configdata['subreddits'] = literal_eval(configdata['subreddits'])
    configdata['postsave'] = int(configdata['postsave'])
    configdata['other']['ignore_duplicates'] = int(configdata['other']['ignore_duplicates'])
    configdata['other']['download_gallery'] = int(configdata['other']['download_gallery'])
    
    return configdata

def read_config_file():
    """Reads the backgrounder.ini file and imports settings from it."""
    
    MIN_RUN_TIME = 300 # min five minutes between runs
    
    config = configparser.ConfigParser(allow_no_value=True)
    configdata = {}
    
    config.read('backgrounder.ini')
    
    configdata['path'] = {}
    configdata['path']['image'] = config['path']['image']
    configdata['subreddits'] = config['subreddits']['subreddits']
    configdata['postsave'] = config['postsave']['method']
    configdata['timing'] = config['timing']['seconds']
    configdata['other'] = {}
    configdata['other']['ignore_duplicates'] = config['other']['ignore_duplicates']
    configdata['other']['download_gallery'] = config['other']['download_gallery']
    
    # validate user-entered config
    valid_dict = validate_config(configdata)
    for key, val in valid_dict.items():
        if val is False:
            messagebox.showinfo('Warning', 'There was an error reading backgrounder.ini.\n\nPlease delete your data.pkl file and rerun the program.'
                % (key))
            return None
    
    process_configdata(configdata)
        
    return configdata
    
def install(DEBUG):
    """Runs installation procedures."""
    dat = Data()
    GUI = config_gui.Config_GUI()
    
    dat.configdata = GUI.activate()
    process_configdata(dat.configdata)
    
    # check to make sure the user didn't exit the installer manually
    if not GUI.installation_completed:
        print('WARN: Installation could not successfully validate. Aborting.')
        return None
    
    # TODO: Move to install dir, need a better way though
    # if DEBUG:
    #     copy_to_install_dir(dat)
    # else:
    #     move_to_install_dir(dat)
    
    write_config_file(dat.configdata)
    
    dat.userdata['image_id'] = 0
    dat.userdata['imgur_galleries'] = set()
    
    create_shortcut(dat) # TODO : make this optional
    
    return dat

def read_data(DEBUG):
    """
    Reads and returns save data. If no save data exists, runs and returns the
    result of the installation procedure.
    
    return: a Dat object representing all user save and configuration data
    """    
    if os.path.isfile('data.pkl'):
        with open('data.pkl', 'rb') as input:
            dat = pickle.load(input)
            # use user config file if that file exists
            if os.path.isfile('backgrounder.ini'):
                configdata = read_config_file()
                if configdata:
                    # config was found and is valid
                    dat.configdata = configdata
                else:
                    # config was found, but is invalid
                    quit() # FIXME getting some funky bugs when I try to rerun the installer
            else:
                # config was not found, write previous data
                write_config_file(dat.configdata)
            return dat
    else:
        return install(DEBUG)

def write_data(dat):
    """Writes save data to disk. Overwrites any existing data."""
    with open('data.pkl', 'wb') as out:
        pickle.dump(dat, out, pickle.HIGHEST_PROTOCOL)
    
def main():
    """Runs the GUI and reports what the user enters, for debugging."""
    
    configdata = config_gui.Config_GUI().activate()
    
    for key, value in configdata.items():
        print(str(key) + ' : ' + str(value))
    
if __name__ == '__main__':
    main()