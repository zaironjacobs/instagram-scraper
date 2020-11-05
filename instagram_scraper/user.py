import os

from . import constants
from . import helper


class User:
    def __init__(self, username):
        self.__username = username
        self.__post_links = []
        self.__profile_link = constants.INSTAGRAM_URL + self.__username + '/'
        self.__stories_link = constants.INSTAGRAM_URL + 'stories/' + self.__username + '/'

        self.__output_user_posts_path = constants.USERS_DIR + '/' + username + '/posts'
        self.__output_user_stories_path = constants.USERS_DIR + '/' + username + '/stories'
        self.__output_user_dp_path = constants.USERS_DIR + '/' + username + '/display_photo'

    def create_user_output_directories(self):
        if not os.path.exists(self.__output_user_posts_path):
            helper.create_dir(self.__output_user_posts_path)
        if not os.path.exists(self.__output_user_stories_path):
            helper.create_dir(self.__output_user_stories_path)
        if not os.path.exists(self.__output_user_dp_path):
            helper.create_dir(self.__output_user_dp_path)

    @property
    def username(self):
        return self.__username

    @username.setter
    def username(self, username):
        self.__username = username

    @property
    def post_links(self):
        return self.__post_links

    @post_links.setter
    def post_links(self, post_links):
        self.__post_links = post_links

    @property
    def profile_link(self):
        return self.__profile_link

    @profile_link.setter
    def profile_link(self, profile_link):
        self.__profile_link = profile_link

    @property
    def stories_link(self):
        return self.__stories_link

    @stories_link.setter
    def stories_link(self, stories_link):
        self.__stories_link = stories_link

    @property
    def output_user_posts_path(self):
        return self.__output_user_posts_path

    @output_user_posts_path.setter
    def output_user_posts_path(self, output_user_posts_path):
        self.__output_user_posts_path = output_user_posts_path

    @property
    def output_user_stories_path(self):
        return self.__output_user_stories_path

    @output_user_stories_path.setter
    def output_user_stories_path(self, output_user_stories_path):
        self.__output_user_stories_path = output_user_stories_path

    @property
    def output_user_dp_path(self):
        return self.__output_user_dp_path

    @output_user_dp_path.setter
    def output_user_dp_path(self, output_user_dp_path):
        self.__output_user_dp_path = output_user_dp_path
