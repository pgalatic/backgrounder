# author: Paul Galatic github.com/pgalatic

import oauth_info
import installer
import datetime
import requests
import logging
import pickle
import pprint
import praw
import os

class Data(object):
	def __init__(self):
		self.dict = {}

def get_reddit():
	write_praw_ini()
	
	reddit = praw.Reddit(client_id=oauth_info.client_id,
						 client_secret=oauth_info.client_secret,
						 redirect_uri=oauth_info.redirect_uri,
						 user_agent=oauth_info.user_agent)
	reddit.read_only = True
	return reddit

def get_logger():
	logger = logging.getLogger('backgrounder')
	logger.setLevel(logging.INFO)
	
	fh = logging.FileHandler('backgrounder.log')
	fh.setLevel(logging.INFO)
	
	logger.addHandler(fh)
	
	return logger

def write_praw_ini():
	"""
	The Python-Reddit API Wrapper (PRAW) requires a .ini file in order to run.
	If that file is not present, the executable will fail. This function writes
	that file out for the user if it is not present (as I am not tempted to dig
	into Pyinstaller to figure out why it isn't being included in the exe file
	in the first place).
	
	You can find out what these INI values mean by looking them up in the PRAW
	package.
	"""
	if not os.path.isfile('praw.ini'):
		with open('praw.ini', 'w') as out:
			out.write('[DEFAULT]\ncheck_for_updates=True\ncomment_kind=t1\n')
			out.write('message_kind=t4\nredditor_kind=t2\nsubmission_kind=t3\n')
			out.write('subreddit_kind=t5\noauth_url=https://oauth.reddit.com\n')
			out.write('reddit_url=https://www.reddit.com\n')
			out.write('short_url=https://redd.it\n')
			out.close()
	
def read_data():
	if os.path.isfile('data.pkl'):
		with open('data.pkl', 'rb') as input:
			dat = pickle.load(input)
			input.close()
			return dat
	return None
	
def write_data(dat):
	with open('data.pkl', 'wb') as out:
		pickle.dump(dat, out, pickle.HIGHEST_PROTOCOL)

def save_image(combined_path, image_url):
	with open(combined_path, 'wb') as handle:
		response = requests.get(image_url, stream=True)
		
		if not response.ok:
			print(response)
		
		for block in response.iter_content(1024):
			if not block:
				break
			
			handle.write(block)
		
		handle.close()

def combine_paths(dict):
	picture_path = dict['picture_path']
	image_id = dict['image_id']
	image_ext = "/" + str(image_id) + ".png"
	# loop through different extensions to avoid overwriting images
	while os.path.isfile(picture_path + image_ext):
		image_id += 1
		image_ext = "/" + str(image_id) + ".png"
	dict['image_id'] = image_id
	return picture_path + image_ext

def top_post_list(subreddit_list):
	tops = []
	for subreddit in subreddit_list:
		# TODO : Maybe change this limit?
		for submission in subreddit.top(time_filter='day', limit=1):
			tops.append(submission)
	return tops

def grab_image(dict):
	reddit = get_reddit()
	subreddits = [] # TODO : import from dict
	subreddits.append(reddit.subreddit('wallpapers'))
	
	log = get_logger() # TODO : make accessible to other functions?
	
	combined_path = combine_paths(dict)
	
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
	# grab data from save file
	# install if there is no data
	dat = read_data()
	if dat is None:
		dict = installer.install()
		dat = Data()
		dat.dict = dict
	else:
		dict = dat.dict
	
	# run this script only if one of the following conditions is true:
	#	* it has been 24hrs since last run
	#	* the script has just been installed
	# TODO : Make this configurable without duplicating images
	datetime_difference = datetime.datetime.now() - dict['last_run_datetime']
	if not (datetime_difference.total_seconds() > 86400 or datetime_difference.total_seconds() < 60):
		print('Too soon since last run. Aborting') # TODO: log this
		return
	
	grab_image(dict)
	
	dict['last_run_datetime'] = datetime.datetime.now()
	
	dat.dict = dict
	write_data(dat)

if __name__ == '__main__':
	main()