# author: Paul Galatic github.com/pgalatic

import oauth_info
import installer
import requests
import pickle
import pprint
import praw
import os

class Data(object):
	def __init__(self):
		self.dict = {}

def init():
	write_praw_ini()
	
	reddit = praw.Reddit(client_id=oauth_info.client_id,
						 client_secret=oauth_info.client_secret,
						 redirect_uri=oauth_info.redirect_uri,
						 user_agent=oauth_info.user_agent)
	reddit.read_only = True
	return reddit

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
	
def read_data():
	if os.path.isfile('data.pkl'):
		with open('data.pkl', 'rb') as input:
			dat = pickle.load(input)
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

def combine_paths(dict):
	picture_path = dict['picture_path']
	image_id = dict['image_id']
	image_ext = "/" + str(image_id) + ".png"
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

def main():
	reddit = init()
	
	dat = read_data()
	if dat is None:
		dict = installer.install()
		dat = Data()
		dat.dict = dict
	else:
		dict = dat.dict
	
	combined_path = combine_paths(dict)
	
	subreddits = [] # TODO : import from dict
	subreddits.append(reddit.subreddit('wallpapers'))
	
	top_posts = top_post_list(subreddits)
	for post in top_posts: # TODO : assumes that each post has a media element
		permalink = post.permalink # TODO : log permalink for sourcing
		image_url = post.url
	
		save_image(combined_path, image_url)
	
	dat.dict = dict
	write_data(dat)

if __name__ == '__main__':
	main()