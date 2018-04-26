# author: Paul Galatic github.com/pgalatic

import pprint
import praw

def init():
	reddit = praw.Reddit()
	

def main():
	
	r_wallpapers = praw.subreddit('wallpapers')
	pprint.pprint(vars(r_wallpapers))

reddit = init()
main()