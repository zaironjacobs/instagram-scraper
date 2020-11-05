from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

from .. import constants
from .. import actions


class PostHasMultipleContent(actions.Action):
    def __init__(self, scraper, link):
        super().__init__(scraper)
        self.__link = link

    def do(self):
        """ Check if post has multiple content """

        actions.GoToLink(self._scraper, self.__link).do()

        try:
            self._web_driver.find_element_by_css_selector(constants.NEXT_CONTROL_CSS)
            return True
        except (NoSuchElementException, StaleElementReferenceException):
            return False

    def on_fail(self):
        pass
