import os

from instagram_scraper import constants
from instagram_scraper import helper


class Tag:
    def __init__(self, tagname):
        self.tagname = tagname
        self.post_links = []

        self.output_top_tag_path = constants.TAGS_DIR + '/' + tagname + '/top'
        self.output_recent_tag_path = constants.TAGS_DIR + '/' + tagname + '/recent'

    def create_tag_output_directories(self):
        if not os.path.exists(self.output_top_tag_path):
            helper.create_dir(self.output_top_tag_path)
        if not os.path.exists(self.output_recent_tag_path):
            helper.create_dir(self.output_recent_tag_path)
