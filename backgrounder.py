# author: Paul Galatic github.com/pgalatic

import oauth_info
import requests
import pickle
import pprint
import praw
import os

picture_path = 'C:\\Users\\Essence\\Documents\\Backgrounds' #TODO : Have user set this path
file_path = 'C:\\Users\\Essence\\Documents\\Python Scripts\\backgrounder' #TODO : Make more general

class Data(object):
	def __init__(self, dict):
		self.dict = dict

def init():
	reddit = praw.Reddit(client_id=oauth_info.client_id,
						 client_secret=oauth_info.client_secret,
						 redirect_uri=oauth_info.redirect_uri,
						 user_agent=oauth_info.user_agent)
	reddit.read_only = True
	return reddit

def read_data():
	dict = None
	if (os.path.isfile('data.pkl')):
		with open('data.pkl', 'rb') as input:
			dict = pickle.load(input)
	return dict
	
def write_data(dict):
	with open('data.pkl', 'wb') as out:
		pickle.dump(dict, out, pickle.HIGHEST_PROTOCOL)

def save_image(picture_path, image_url):
	with open(picture_path, 'wb') as handle:
		response = requests.get(image_url, stream=True)
		
		if not response.ok:
			print(response)
		
		for block in response.iter_content(1024):
			if not block:
				break
			
			handle.write(block)

def main(reddit):
	# if read_data is none
	#	prompt user a la initial installation
	# else
	#	picture_path = dict.picture_path
	#	image_id = dict.image_id + 1
	#	dict.image_id = image_id
	
	r_wallpapers = reddit.subreddit('wallpapers')
	
	top_submission = None
	# grabs top submission
	for wallpaper in r_wallpapers.top(time_filter='day', limit=1):
		top_submission = wallpaper
	
	permalink = top_submission.permalink
	image_url = top_submission.url
	
	image_id = "/2.png"
	
	save_image(picture_path + image_id, image_url)
	
	
	


reddit = init()

main(reddit)