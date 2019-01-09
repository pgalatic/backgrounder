# author: Paul Galatic github.com/pgalatic
#
# file handles downloading images
#

import os
import random
import logging
import datetime
import requests
from PIL import Image
from reddit import Reddit
from PIL import ImageChops
from imgur_album_downloader.imguralbum import ImgurAlbumDownloader

NO_ERROR = 0
ERR_NOT_IMAGE = 1
ERR_DUPLICATE_IMAGE = 2
ERR_DUPLICATE_GALLERY = 3

def get_logger():
    """Initializes and returns the logging object."""
    logger = logging.getLogger('backgrounder')
    logger.setLevel(logging.INFO)

    fh = logging.FileHandler('backgrounder.log')
    fh.setLevel(logging.INFO)

    logger.addHandler(fh)

    return logger
    
def is_image(image_path):
    """
    Checks if an image can be opened. If it can't, that usually means that the
    original post did not contain an image.
    """
    try:
        Image.open(image_path)
    except OSError:
        # could not identify image file
        return False
    return True
    
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

def download_imgur(url, dat):
    """
    Utility for downloading imgur galleries, which have to be handled 
    differently than just a single image.
    
    Arguments:
        url -- the url of the imgur gallery
    Returns:
        True -- operation successfully completed
        False -- there was an error
    """
    # if ignoring duplicates, don't download from the same gallery twice
    if dat.configdata['other']['ignore_duplicates'] == 1:
        if url in dat.userdata['imgur_galleries']:
            return ERR_DUPLICATE_GALLERY
    
    downloader = ImgurAlbumDownloader(url)
    path = dat.configdata['path']['image']
    idx = random.randint(1, downloader.num_images() + 1)

    if dat.configdata['other']['download_gallery'] == 0:
        # download a random image
        downloader.save(path, idx)
    else:
        # download entire gallery
        downloader.save(path)
    
    dat.userdata['imgur_galleries'].add(url)
    
    return NO_ERROR
    
def download_image(id, url, dat):
    """
    Retrieves an image and stores it to disk.

    Arguments:
        id -- The next id to use for an image to download
        url -- The URL of the image to retrieve
    
    Returns:
    True -- image was downloaded
    False  -- image was not downloaded
    """
	# TODO: If download fails, close program gracefully and log stack traces
	
    with open(id, 'wb') as handle:
        response = requests.get(url, stream=True)

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
    
    # check to make sure the image is an image
    if not is_image(id):
        os.remove(id)
        return ERR_NOT_IMAGE
    
    # check to make sure the image isn't a duplicate, if necessary
    if dat.configdata['other']['ignore_duplicates'] == 1:
        if is_duplicate(id, dat.configdata['path']['image']):
            os.remove(id)
            return ERR_DUPLICATE_IMAGE
    
    return NO_ERROR

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
    path = dat.configdata['path']['image']
    image_id = dat.userdata['image_id'] + increment
    image_ext = "/" + str(image_id) + ".png"
    # loop through different extensions to avoid overwriting images
    while os.path.isfile(path + image_ext):
        image_id += 1
        image_ext = "/" + str(image_id) + ".png"
    dat.userdata['image_id'] = image_id
    return path + image_ext

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
    
    if tops == []:
        # subreddit isn't active enough -- no 'top' post
        # try something else
        for submission in subreddit.hot(limit=3):
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
    # TODO : Validate that the image isn't empty

    reddit = Reddit().reddit
    subreddit_names = dat.configdata['subreddits']
    subreddits = [reddit.subreddit(name) for name in subreddit_names]
    log = get_logger() # TODO : make accessible to other functions?

    # use different method to save image depending on user's stated preferencedata['subreddits']
    method = dat.configdata['postsave']
    if method == 0:
        top_posts = topmost_post(subreddits)
    elif method == 1:
        top_posts = all_top_posts(subreddits)
    elif method == 2:
        top_posts = rand_top_post(subreddits)
    else:
        raise Exception('Bad config data (post save method): %s' % (str(method)))

    increment = 0
    for post in top_posts: # TODO : assumes that each post has a media element
        permalink = post.permalink
        url = post.url
        
        combined_path = combine_paths(dat, increment)
        increment += 1
        
        # determine if url is direct image link or link to imgur gallery
        if 'imgur' in url:
            result = download_imgur(url, dat)
            message = str(datetime.datetime.now()) + ': gallery saved --' +   \
                        '\n\tsource: \t' + str(permalink) + '\n\tresult: '
                              
        else:
            result = download_image(combined_path, url, dat)
            message = str(datetime.datetime.now()) + ': image saved --' +     \
                        '\n\tsource: \t' + str(permalink) +                   \
                        '\n\tlocation: \t' + combined_path + '\n\tresult: \t'
                    
        # TODO if download is unsuccessful, try something else
        if result == NO_ERROR:
            message += 'SUCCESSFULLY SAVED\n'
        elif result == ERR_NOT_IMAGE:
            message += 'UNSUCCESSFUL -- POST WAS NOT IMAGE\n'
        elif result == ERR_DUPLICATE_IMAGE:
            message += 'UNSUCCESSFUL -- POST WAS DUPLICATE\n'
        elif result == ERR_DUPLICATE_GALLERY:
            message += 'UNSUCCESSFUL -- ALREADY VISITED THIS GALLERY\n'
        else:
            message += 'CRITICAL ERROR -- CONTACT DEVELOPER\n'

        log.info(message)