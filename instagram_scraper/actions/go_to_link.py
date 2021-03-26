import logging
import time

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import WebDriverException

from .. import constants
from .. import actions

logger = logging.getLogger('__name__')


class GoToLink(actions.Action):
    def __init__(self, scraper, link, force=False):
        super().__init__(scraper)
        self.__link = link
        self.__force = force
        self.__page_reload_tries = 0

    def do(self):
        """ Navigate to link """

        if self.__page_reload_tries > 5:
            logger.error('page load timeout')
            self.on_fail()

        current_link = self._web_driver.current_url
        current_link = current_link.strip('/')
        link = self.__link.strip('/')

        if not self.__force:
            if current_link == link:
                return

        try:
            self._web_driver.get(link)

            WebDriverWait(
                self._web_driver, 10).until(lambda d: d.execute_script('return document.readyState') == 'complete')
            time.sleep(3)

            # Check for page load failure
            try:
                self._web_driver.find_element_by_id(constants.CHROME_RELOAD_BUTTON_ID)
                self.__page_reload_tries += 1
                logger.warning('chrome could not load page')
                self.do()
            except (NoSuchElementException, StaleElementReferenceException):
                pass
            try:
                self._web_driver.find_element_by_id(constants.SORRY_ID)
                self.__page_reload_tries += 1
                logger.warning('facebook error')
                self.do()
            except (NoSuchElementException, StaleElementReferenceException):
                pass

        except (TimeoutException, WebDriverException) as err:
            logger.error(err)
            logger.error('page load timeout')
            self.on_fail()

        if not self._scraper.cookies_accepted:
            actions.AcceptCookies(self._scraper).do()

    def on_fail(self):
        print('\npage load timeout')
        self._scraper.stop()
