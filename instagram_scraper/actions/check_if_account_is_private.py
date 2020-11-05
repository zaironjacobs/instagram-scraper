from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

from .. import constants
from .. import actions


class CheckIfAccountIsPrivate(actions.Action):
    def __init__(self, scraper, user):
        super().__init__(scraper)
        self.__user = user

    def do(self):
        """ Check if account is private """

        actions.GoToLink(self._scraper, self.__user.profile_link).do()

        try:
            self._web_driver.find_element_by_css_selector(constants.USER_PRIVATE_CSS)
        except (NoSuchElementException, StaleElementReferenceException):
            return False
        else:
            return True

    def on_fail(self):
        pass
