import logging

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from requests.exceptions import RequestException

from .. import constants
from .. import actions
from ..import retriever

logger = logging.getLogger('__name__')


class ScrapeDisplay(actions.Action):
    def __init__(self, scraper, user):
        super().__init__(scraper)
        self.__user = user

    def do(self):
        """ Download the user display photo """

        actions.GoToLink(self._scraper, self.__user.profile_link).do()

        display_picture_url = None

        try:
            element = self._web_driver.find_element_by_css_selector(constants.DISPLAY_PIC_PUBLIC_CSS)
            display_picture_url = element.get_attribute('src')
        except (NoSuchElementException, StaleElementReferenceException):
            pass

        try:
            element = self._web_driver.find_element_by_css_selector(constants.DISPLAY_PIC_PRIVATE_CSS)
            display_picture_url = element.get_attribute('src')
        except (NoSuchElementException, StaleElementReferenceException):
            pass

        try:
            retriever.download(display_picture_url, output_path=self.__user.output_user_dp_path)
        except (OSError, RequestException) as err:
            logger.error(err)
            self.on_fail()

    def on_fail(self):
        print('error downloading display picture')
