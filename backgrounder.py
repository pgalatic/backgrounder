# author: Paul Galatic github.com/pgalatic
#
# main file
#

from data import Data
import oauth_info
import datetime
import requests
import logging
import loader
import pickle
import pprint
import praw
import os

def get_reddit():
	"""Initializes and returns the Reddit object."""
	write_praw_ini()
	
	# Secret info is packaged into executable
	reddit = praw.Reddit(client_id=oauth_info.client_id,
						 client_secret=oauth_info.client_secret,
						 redirect_uri=oauth_info.redirect_uri,
						 user_agent=oauth_info.user_agent)
	reddit.read_only = True
	return reddit

def get_logger():
	"""Initializes and returns the logging object."""
	logger = logging.getLogger('backgrounder')
	logger.setLevel(logging.INFO)
	
	fh = logging.FileHandler('backgrounder.log')
	fh.setLevel(logging.INFO)
	
	logger.addHandler(fh)
	
	return logger

def write_praw_ini():
	"""
	Creates a praw.ini file if one does not already exist.
	
	The Python-Reddit API Wrapper (PRAW) requires a .ini file in order to run.
	If that file is not present, the executable will fail. This function writes
	that file out for the user if it is not present (as I am not tempted to dig
	into Pyinstaller to figure out why it isn't being included in the exe file
	in the first place).
	
	For more detail, visit:
	praw.readthedocs.io/en/latest/getting_started/configuration/prawini.html
	"""
	if not os.path.isfile('praw.ini'):
		with open('praw.ini', 'w') as out:
			message = (
				'[DEFAULT]\ncheck_for_updates=True\ncomment_kind=t1\n',
				'message_kind=t4\nredditor_kind=t2\nsubmission_kind=t3\n',
				'subreddit_kind=t5\noauth_url=https://oauth.reddit.com\n',
				'subreddit_kind=t5\noauth_url=https://oauth.reddit.com\n',
				'reddit_url=https://www.reddit.com\n',
				'short_url=https://redd.it\n'
			)
			out.write(message)
	


def save_image(combined_path, image_url):
	"""
	Retrieves an image and stores it to disk.
	
	Arguments:
	combined_path -- The path containing the pwd of the image as well as its 
		filename
	image_url -- The URL of the image to retrieve
	"""
	with open(combined_path, 'wb') as handle:
		response = requests.get(image_url, stream=True)
		
		if not response.ok:
			print(response)
		
		for block in response.iter_content(1024):
			if not block:
				break
			
			handle.write(block)

def combine_paths(dat):
	"""
	Determines the precise location where the new image will be written.
	
	This procedure takes the user-specified file path where images will 
	be stored and searches for an unused filename based on the last-used
	filename in the save data. This is to avoid overwriting images.
	
	Arguments:
	dat -- save data
	Returns:
	a viable path for the new image
	"""
	filepath = dat.configdata['filepath']
	image_id = dat.userdata['image_id']
	image_ext = "/" + str(image_id) + ".png"
	# loop through different extensions to avoid overwriting images
	while os.path.isfile(filepath + image_ext):
		image_id += 1
		image_ext = "/" + str(image_id) + ".png"
	dat.userdata['image_id'] = image_id
	return filepath + image_ext

def top_post_list(subreddits):
	"""Returns a list of top posts, one for each in subreddit_list."""
	tops = []
	for subreddit in subreddits:
		# TODO : Maybe change this limit?
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
	reddit = get_reddit()
	subreddit_names = dat.configdata['subreddits']
	subreddits = [reddit.subreddit(name) for name in subreddit_names]
	
	log = get_logger() # TODO : make accessible to other functions?
	
	combined_path = combine_paths(dat)
	
	top_posts = top_post_list(subreddits)
	
	
	
	for post in top_posts: # TODO : assumes that each post has a media element
		permalink = post.permalink # TODO : log permalink for sourcing
		image_url = post.url
	
		save_image(combined_path, image_url)
		
		message = str(datetime.datetime.now()) + ': image saved --' + 	\
				  '\n\tlocation: \t' + combined_path +					\
				  '\n\tsource: \t' + str(permalink) +					\
				  '\n'
		
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
	
	# run this script only if one of the following conditions is true:
	#	* it has been 24hrs since last run
	#	* the script has just been installed
	# TODO : Make this configurable without duplicating images
	datetime_difference = datetime.datetime.now() - dat.userdata['last_run_datetime']
	if not (datetime_difference.total_seconds() > 86400 or datetime_difference.total_seconds() < 60):
		print('Too soon since last run. Aborting') # TODO: log this
		return
	
	grab_images(dat)
	
	dat.userdata['last_run_datetime'] = datetime.datetime.now()
	
	loader.write_data(dat)

if __name__ == '__main__':
	main()
