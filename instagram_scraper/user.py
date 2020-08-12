import os
import sys

from instagram_scraper import constants
from instagram_scraper import helper


class User:
    def __init__(self, username):
        self.username = username
        self.post_links = []
        self.profile_link = constants.INSTAGRAM_URL + self.username + '/'
        self.stories_link = constants.INSTAGRAM_URL + 'stories/' + self.username + '/'

        self.output_user_posts_path = constants.USERS_DIR + '/' + username + '/posts'
        self.output_user_stories_path = constants.USERS_DIR + '/' + username + '/stories'
        self.output_user_dp_path = constants.USERS_DIR + '/' + username + '/display_photo'

    def create_user_output_directories(self):
        if not os.path.exists(self.output_user_posts_path):
            helper.create_dir(self.output_user_posts_path)
        if not os.path.exists(self.output_user_stories_path):
            helper.create_dir(self.output_user_stories_path)
        if not os.path.exists(self.output_user_dp_path):
            helper.create_dir(self.output_user_dp_path)
