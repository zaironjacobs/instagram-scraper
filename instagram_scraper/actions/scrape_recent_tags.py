import logging

import colorama

from .. import constants
from .. import actions
from ..progress_bar import ProgressBar

logger = logging.getLogger('__name__')


class ScrapeRecentTags(actions.Action):
    def __init__(self, scraper, link, tag):
        super().__init__(scraper)
        self.__c_fore = colorama.Fore
        self.__c_style = colorama.Style
        colorama.init()

        self.__link = link
        self.__tag = tag
        self.__max_download = scraper.max_download
        self.__database = scraper.database

    def do(self):
        """ Find the post links from the recent tags """

        print('retrieving post links from explore, please wait... ')

        actions.GoToLink(self._scraper, self.__link).do()

        self.__tag.post_links = actions.GrabPostLinks(self._scraper, self.__link, constants.RECENT_TAGS_XPATH).do()

        if len(self.__tag.post_links) < 1:
            print(self.__c_fore.RED + 'no posts found' + self.__c_style.RESET_ALL)
            return

        print(self.__c_fore.GREEN + str(len(self.__tag.post_links)) +
              ' recent post(s) will be downloaded: ' + self.__c_style.RESET_ALL)

        progress_bar = ProgressBar(len(self.__tag.post_links), show_count=True)
        for post_link in self.__tag.post_links:
            actions.InitScrape(self._scraper, post_link, self.__tag.output_recent_tag_path).do()
            self.__database.insert_tag_post(post_link, self.__tag.tagname, in_recent=True)
            progress_bar.update(1)
        progress_bar.close()

    def on_fail(self):
        pass
