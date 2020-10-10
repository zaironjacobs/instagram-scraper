import logging

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

from instagram_scraper import constants
from instagram_scraper import actions

logger = logging.getLogger('__name__')


class InitScrape(actions.Action):
    def __init__(self, scraper, link, output_path, userid=None):
        super().__init__(scraper)
        self.__database = scraper.database
        self.__link = link
        self.__output_path = output_path
        self.__userid = userid

    def do(self):
        """
        Load the post page and check whether to start scraping a post with single content or multiple content.
        """

        actions.GoToLink(self._scraper, self.__link).do()

        try:
            self._web_driver.find_element_by_css_selector(constants.PAGE_USERNAME)
        except (NoSuchElementException, StaleElementReferenceException):
            logger.warning('page not available at %s', self.__link)
            self._on_fail()

        if actions.PostHasMultipleContent(self._scraper, self.__link).do():
            actions.ScrapeMultipleContent(self._scraper, self.__link, self.__output_path).do()
            self.__database.insert_post(self.__link, True, self.__userid)
        else:
            actions.ScrapeSingleContent(self._scraper, self.__link, self.__output_path).do()
            self.__database.insert_post(self.__link, False, self.__userid)

    def _on_fail(self):
        print('page not available at %s', self.__link)
        self._scraper.stop()
