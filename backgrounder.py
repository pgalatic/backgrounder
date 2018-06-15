# author: Paul Galatic github.com/pgalatic
#
# main file
#

import os
import pprint
import loader
import random
import logging
import datetime
import requests
from PIL import Image
from data import Data
from reddit import Reddit
from PIL import ImageChops

ENFORCE_RUNTIME_LIMIT = True

def get_logger():
    """Initializes and returns the logging object."""
    logger = logging.getLogger('backgrounder')
    logger.setLevel(logging.INFO)

    fh = logging.FileHandler('backgrounder.log')
    fh.setLevel(logging.INFO)

    logger.addHandler(fh)

    return logger
    
def is_duplicate(image_path, filepath):
    """
    Checks if the given image is a duplicate of any existing image in the 
    specified directory (normally where the user has chosen backgrounds to be 
    stored).
    
    Arguments:
        image_path -- the absolute path to the image in question
        filepath -- the directory to inspect
    Returns:
        True -- the image specified by image_path is a duplicate
        False -- the image specified by image_path isn't a duplicate
    """
    BLOCKSIZE = 65536
        
    im1 = Image.open(image_path)
    
    for filename in os.listdir(filepath):
        if filename.endswith('.png') or filename.endswith('.jpg'):
            full_path = filepath + '/' + filename
            if full_path == image_path:
                # don't compare the image to itself
                continue
            
            im2 = Image.open(full_path)
            
            try:
                diff = ImageChops.difference(im1, im2).getbbox()
                if not diff:
                    # boundary box doesn't exist -- images are identical
                    return True
                
            except ValueError:
                # images aren't of the same dimension
                continue
            
            
            
    return False

def save_image(combined_path, image_url, dat):
    """
    Retrieves an image and stores it to disk.

    Arguments:
    combined_path -- The path containing the pwd of the image as well as its
        filename
    image_url -- The URL of the image to retrieve
    
    Returns:
    True -- image was downloaded
    False  -- image was not downloaded
    """
    with open(combined_path, 'wb') as handle:
        response = requests.get(image_url, stream=True)

        if not response.ok:
            print(response)
            raise Exception(
                    'There was an issue downloading the image. ' +
                    'Please double-check your internet connection.'
                )

        for block in response.iter_content(1024):
            if not block:
                break

            handle.write(block)
            
    # check to make sure the image isn't a duplicate, if necessary
    if dat.configdata['other']['ignore_duplicates'] == 1:
        if is_duplicate(combined_path, dat.configdata['filepath']):
            os.remove(combined_path)
            return False
    
    return True

def combine_paths(dat, increment=0):
    """
    Determines the precise location where the new image will be written.

    This procedure takes the user-specified file path where images will be
    stored and searches for an unused filename based on the last-used filename
    in the save data. This is to avoid overwriting images.

    Arguments:
    dat -- save data
    increment -- for saving multiple images, allows the id to be increased
    Returns:
    a viable path for the new image
    """
    filepath = dat.configdata['filepath']
    image_id = dat.userdata['image_id'] + increment
    image_ext = "/" + str(image_id) + ".png"
    # loop through different extensions to avoid overwriting images
    while os.path.isfile(filepath + image_ext):
        image_id += 1
        image_ext = "/" + str(image_id) + ".png"
    dat.userdata['image_id'] = image_id
    return filepath + image_ext

def topmost_post(subreddits):
    """Returns the highest-upvoted post of all subreddits."""
    tops = all_top_posts(subreddits)
    top = tops[0]
    for submission in tops:
        if submission.score > top.score:
            top = submission
    return [top]

def all_top_posts(subreddits):
    """Returns a list of top posts, one for each in subreddits."""
    tops = []
    for subreddit in subreddits:
        # TODO : Maybe change this limit?
        # WARN : If the subreddit has low activity, this function may fail
        for submission in subreddit.top(time_filter='day', limit=1):
            tops.append(submission)
    return tops

def rand_top_post(subreddits):
    """Chooses a random subreddit and grabs the top post from that."""
    tops = []
    subreddit = subreddits[random.randint(0, len(subreddits) - 1)]
    for submission in subreddit.top(time_filter='day', limit=1):
        tops.append(submission)
    return tops

def grab_images(dat):
    """
    Retrieves a set of images to save.

    Reaches out to Reddit and retrieves a set of top images to store in the
    user-specified location.

    Arguments:
    dat -- save data
    """
    # TODO : Grab images by resolution / resolution minimum

    reddit = Reddit().reddit
    subreddit_names = dat.configdata['subreddits']
    subreddits = [reddit.subreddit(name) for name in subreddit_names]
    log = get_logger() # TODO : make accessible to other functions?

    # use different method to save image depending on user's stated preference
    if dat.configdata['postsave'] == 0:
        top_posts = topmost_post(subreddits)
    elif dat.configdata['postsave'] == 1:
        top_posts = all_top_posts(subreddits)
    elif dat.configdata['postsave'] == 2:
        top_posts = rand_top_post(subreddits)
    else:
        raise Exception('Bad config data (post save method)')

    increment = 0
    # TODO : assumes that top post isn't a gallery (fails if it is)
    for post in top_posts: # TODO : assumes that each post has a media element
        permalink = post.permalink
        image_url = post.url

        combined_path = combine_paths(dat, increment)
        increment += 1

        successful = save_image(combined_path, image_url, dat)            

        message = str(datetime.datetime.now()) + ': image saved --' +     \
                  '\n\tlocation: \t' + combined_path +                    \
                  '\n\tsource: \t' + str(permalink) +                     \
                  '\n\tresult: '
        
        if successful:
            message += 'SUCCESSFULLY SAVED\n'
        else:
            message += 'DELETED -- DUPLICATE\n'

        log.info(message)

def main():
    """
    Main function. Prompts for installation, reads data, and checks time.

    If there is no save data, run the loader and generate save data.
    Once data is available, check to see if sufficient time has passed since
    the last run. If so, grab images. Otherwise, return.
    """
    # grab data from save file
    dat = loader.read_data()

    if dat is None:
        return # installation failed

    timing_pref = dat.configdata['timing']
    
    # run this script only if one of the following conditions is true:
    #    * it has been <config_seconds> since last run
    #    * the script has just been installed
    # TODO : Make this configurable without duplicating images
    datetime_difference = datetime.datetime.now() - dat.userdata['last_run_datetime']
    if ENFORCE_RUNTIME_LIMIT:
        if not (datetime_difference.total_seconds() > timing_pref or datetime_difference.total_seconds() < 10):
            print('Too soon since last run. Aborting') # TODO: log this
            return

    grab_images(dat)

    dat.userdata['last_run_datetime'] = datetime.datetime.now()

    loader.write_data(dat)

if __name__ == '__main__':
    main()
