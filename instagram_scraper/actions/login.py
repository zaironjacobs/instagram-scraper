import time
import getpass
import logging

from instagram_scraper import constants
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import ElementClickInterceptedException
from selenium.common.exceptions import StaleElementReferenceException

from instagram_scraper import actions

logger = logging.getLogger('__name__')


class Login(actions.Action):
    def __init__(self, scraper, login_username, login_password):
        super().__init__(scraper)
        self.__login_username = login_username
        self.__login_password = login_password

    def do(self):
        """ Login """

        actions.GoToLink(self._scraper, constants.INSTAGRAM_URL).do()
        time.sleep(2)

        # Enter username and password and click login
        try:
            credential_elements = self._web_driver.find_elements_by_css_selector(constants.CREDENTIALS_CSS)

            username_element = credential_elements[0]
            username_element.click()
            username_element.send_keys(self.__login_username)

            password_element = credential_elements[1]
            password_element.click()
            password_element.send_keys(self.__login_password)

            self._web_driver.find_element_by_css_selector(constants.LOGIN_BUTTON_CSS).click()

            time.sleep(4)

        except (NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException) as err:
            logger.error(err)
            self.on_fail()

        # Enter security code if asked for
        try:
            security_input_box = self._web_driver.find_element_by_css_selector(constants.SECURITY_INPUT_BOX_CSS)
            security_input_box.click()
        except (NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException):
            pass
        else:
            time.sleep(2)

            try:
                security_code = getpass.getpass(prompt='enter security code: ')
                security_input_box.send_keys(security_code)
                self._web_driver.find_element_by_css_selector(constants.SECURITY_BOX_BUTTON).click()
            except (NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException) as err:
                logger.info(err)
                self.on_fail()
            else:
                time.sleep(4)

        # Click no if asked to save login info
        try:
            self._web_driver.find_element_by_css_selector(constants.BUTTON_NO_SAVE_LOGIN_INFO_CSS).click()
        except(NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException):
            pass
        else:
            time.sleep(2)

        # Check for failed login message
        try:
            self._web_driver.find_element_by_css_selector(constants.FAILED_LOGIN_MESSAGE_CSS)
        except (NoSuchElementException, StaleElementReferenceException):
            pass
        else:
            logger.error('failed login message appeared')
            self.on_fail()

        # Click no on message asking to turn on notifications
        try:
            self._web_driver.find_element_by_css_selector(constants.NO_NOTIFICATIONS_BUTTON_CSS).click()
        except (NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException):
            pass

        self._scraper.is_logged_in = True

    def on_fail(self):
        print('login failed')
        self._scraper.stop()
