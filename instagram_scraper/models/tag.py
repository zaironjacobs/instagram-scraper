import os

from .. import constants
from .. import helper


class Tag:
    def __init__(self, tagname):
        self.__tagname = tagname
        self.__post_links = []

        self.__output_top_tag_path = constants.TAGS_DIR + '/' + tagname + '/top'
        self.__output_recent_tag_path = constants.TAGS_DIR + '/' + tagname + '/recent'

    def create_tag_output_directories(self):
        if not os.path.exists(self.__output_top_tag_path):
            helper.create_dir(self.__output_top_tag_path)
        if not os.path.exists(self.__output_recent_tag_path):
            helper.create_dir(self.__output_recent_tag_path)

    @property
    def tagname(self):
        return self.__tagname

    @tagname.setter
    def tagname(self, tagname):
        self.__tagname = tagname

    @property
    def post_links(self):
        return self.__post_links

    @post_links.setter
    def post_links(self, post_links):
        self.__post_links = post_links

    @property
    def output_top_tag_path(self):
        return self.__output_top_tag_path

    @output_top_tag_path.setter
    def output_top_tag_path(self, output_top_tag_path):
        self.__output_top_tag_path = output_top_tag_path

    @property
    def output_recent_tag_path(self):
        return self.__output_recent_tag_path

    @output_recent_tag_path.setter
    def output_recent_tag_path(self, output_recent_tag_path):
        self.__output_recent_tag_path = output_recent_tag_path
