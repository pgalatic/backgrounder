# author: Paul Galatic github.com/pgalatic
#
# file designed to access Reddit via the PRAW API
#

import praw
import oauth_info

class Reddit():
	"""Class used in order to access Reddit through the PRAW API."""
	
	def __init__(self):
		"""Initializes and returns the Reddit object."""	
		# Secret info is packaged into executable
		self.write_praw_ini()
		reddit = praw.Reddit(client_id=oauth_info.client_id,
							 client_secret=oauth_info.client_secret,
							 redirect_uri=oauth_info.redirect_uri,
							 user_agent=oauth_info.user_agent)
		reddit.read_only = True
		self.reddit = reddit
	
	def write_praw_ini(self):
		"""
		Creates a praw.ini file if one does not already exist.
		
		The Python-Reddit API Wrapper (PRAW) requires a .ini file in order to run.
		If that file is not present, the executable will fail. This function writes
		that file out for the user if it is not present (as I am not tempted to dig
		into Pyinstaller to figure out why it isn't being included in the exe file
		in the first place). The executable version is temperamental about actually
		writing the file, so temper with this function at your own risk.
		
		For more detail, visit:
		praw.readthedocs.io/en/latest/getting_started/configuration/prawini.html
		"""
		with open('praw.ini', 'w') as out:
			out.write('[DEFAULT]\ncheck_for_updates=True\ncomment_kind=t1\n')
			out.write('message_kind=t4\nredditor_kind=t2\nsubmission_kind=t3\n')
			out.write('subreddit_kind=t5\noauth_url=https://oauth.reddit.com\n')
			out.write('reddit_url=https://www.reddit.com\n')
			out.write('short_url=https://redd.it\n')