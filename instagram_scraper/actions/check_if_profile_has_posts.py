from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException

from instagram_scraper import constants
from instagram_scraper import actions


class CheckIfProfileHasPosts(actions.Action):
    def __init__(self, scraper, user):
        super().__init__(scraper)
        self.__user = user

    def do(self):
        """ Check if there are posts in the profile """

        actions.GoToLink(self._scraper, self.__user.profile_link).do()

        try:
            self._web_driver.find_element_by_css_selector(constants.POSTS_CSS)
        except (NoSuchElementException, StaleElementReferenceException):
            return False
        else:
            return True

    def _on_fail(self):
        pass
