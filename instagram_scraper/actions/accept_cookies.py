import logging

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import StaleElementReferenceException

from .. import constants
from .. import actions

logger = logging.getLogger('__name__')


class AcceptCookies(actions.Action):
    def __init__(self, scraper):
        super().__init__(scraper)

    def do(self):
        """ Accept cookies """

        try:
            self._web_driver.find_element_by_css_selector(constants.ACCEPT_COOKIES_CSS).click()
        except (NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException) as err:
            pass
        else:
            self._scraper.cookies_accepted = True

    def on_fail(self):
        pass
