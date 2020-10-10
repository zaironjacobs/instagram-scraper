import time
import logging

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import ElementClickInterceptedException

from instagram_scraper import constants
from instagram_scraper import actions

logger = logging.getLogger('__name__')


class GrabPostLinks(actions.Action):
    def __init__(self, scraper, link, xpath=None):
        super().__init__(scraper)
        self.__link = link
        self.__max_download = scraper.max_download
        self.__xpath = xpath

    def do(self):
        """
        Scroll all the way down to the bottom of the page
        When xpath is given, only links inside the xpath will be retrieved
        """

        actions.GoToLink(self._scraper, self.__link).do()

        post_links = []

        increment_browser_height = True

        while True:

            def grab_links():
                """ Search for links on the page and retrieve them """

                links = []

                # Grab post links inside the xpath only
                if self.__xpath:
                    try:
                        element_box = self._web_driver.find_element_by_xpath(self.__xpath)
                        posts_element = element_box.find_elements_by_css_selector(constants.POSTS_CSS + ' [href]')
                        links += [post_element.get_attribute('href') for post_element in posts_element]
                    except (NoSuchElementException, StaleElementReferenceException) as err1:
                        logger.error(err1)
                        return []

                # Grab all post links
                else:
                    try:
                        elements = self._web_driver.find_elements_by_css_selector(constants.POSTS_CSS + ' [href]')
                    except (NoSuchElementException, StaleElementReferenceException) as err2:
                        logger.error(err2)
                        return []

                    try:
                        links += [post_element.get_attribute('href') for post_element in elements]
                    except StaleElementReferenceException as err3:
                        logger.error(err3)
                        return []

                # Remove all duplicate links in the list and keep the list order
                links = sorted(set(links), key=lambda index: links.index(index))

                return links

            post_links += grab_links()

            # Remove any duplicates and return the list if maximum was reached
            post_links = sorted(set(post_links), key=lambda index: post_links.index(index))
            if len(post_links) >= self.__max_download:
                self._web_driver.maximize_window()
                return post_links[:self.__max_download]

            # Scroll down to bottom
            self._web_driver.execute_script('window.scrollTo(0, document.body.scrollHeight);')
            time.sleep(0.5)

            # If instagram asks to show more posts, click it
            try:
                show_more_posts = self._web_driver.find_element_by_css_selector(constants.SHOW_MORE_POSTS_CSS)
            except (NoSuchElementException, StaleElementReferenceException):
                pass
            else:
                try:
                    show_more_posts.click()
                except ElementClickInterceptedException as err:
                    logger.error(err)
                    self._on_fail()

            try:
                self._web_driver.find_element_by_css_selector(constants.SCROLL_LOAD_CSS)
            except (NoSuchElementException, StaleElementReferenceException):
                # Reached the end, grab links for the last time, remove any duplicates and return the list
                post_links += grab_links()
                self._web_driver.maximize_window()
                return sorted(set(post_links), key=lambda index: post_links.index(index))[:self.__max_download]
            else:
                # Change the browser height to prevent randomly being stuck while scrolling down
                height = self._web_driver.get_window_size()['height']
                if increment_browser_height:
                    height += 25
                    increment_browser_height = False
                else:
                    height -= 25
                    increment_browser_height = True

                width = self._web_driver.get_window_size()['width']
                self._web_driver.set_window_size(width, height)

    def _on_fail(self):
        print('error while retrieving post links')
        self._scraper.stop()
