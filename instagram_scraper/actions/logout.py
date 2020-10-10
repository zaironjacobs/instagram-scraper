import time
import logging

from instagram_scraper import constants
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import StaleElementReferenceException

from instagram_scraper import actions

logger = logging.getLogger('__name__')


class Logout(actions.Action):
    def __init__(self, scraper, login_username):
        super().__init__(scraper)
        self.__login_username = login_username

    def do(self):
        """ Logout """

        actions.GoToLink(self._scraper, constants.INSTAGRAM_URL + self.__login_username).do()

        # Click settings and then logout
        try:
            self._web_driver.find_element_by_css_selector(constants.SETTINGS_CSS).click()
            self._web_driver.find_elements_by_css_selector(constants.SETTINGS_BUTTONS_CSS)[8].click()
        except (NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException) as err:
            logger.error(err)
            self.on_fail()
            return
        else:
            self._scraper.is_logged_in = False
            time.sleep(2)

    def on_fail(self):
        print('logout failed')
