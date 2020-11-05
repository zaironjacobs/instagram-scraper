import time

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

from .. import constants
from .. import actions


class CountStories(actions.Action):
    def __init__(self, scraper, user):
        super().__init__(scraper)
        self.__user = user

    def do(self):
        """ Count amount of stories """

        actions.GoToLink(self._scraper, self.__user.stories_link).do()
        time.sleep(2)

        try:
            return len(self._web_driver.find_elements_by_css_selector(constants.STORIES_BAR_CSS))
        except (NoSuchElementException, StaleElementReferenceException):
            return 0

    def on_fail(self):
        pass
