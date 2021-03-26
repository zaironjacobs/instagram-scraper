import logging
import time

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import ElementClickInterceptedException
from requests.exceptions import RequestException

from .. import constants
from .. import actions
from .. import retriever
from ..progress_bar import ProgressBar

logger = logging.getLogger('__name__')


class ScrapeStories(actions.Action):
    def __init__(self, scraper, user, stories_count):
        super().__init__(scraper)
        self.__user = user
        self.__stories_count = stories_count

    def do(self):
        """ Find the src urls of images and videos from stories and save """

        actions.GoToLink(self._scraper, self.__user.stories_link).do()

        try:
            self._web_driver.find_element_by_css_selector(constants.STORIES_VIEW_CSS).click()
        except (NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException) as err:
            logger.error(err)
            self.on_fail()
        else:
            time.sleep(2)

        progress_bar = ProgressBar(self.__stories_count, show_count=True)
        for i in range(self.__stories_count):

            # Check if the story is a video and download it
            try:
                vid_elements = self._web_driver.find_element_by_css_selector(constants.STORIES_VID_CSS)
            except (NoSuchElementException, StaleElementReferenceException):
                pass
            else:
                vid_elements_src = vid_elements.find_elements_by_tag_name('source')
                vid_url = vid_elements_src[0].get_attribute('src')

                try:
                    retriever.download(vid_url, self.__user.output_user_stories_path)
                except (OSError, RequestException) as err:
                    logger.error(err)
                    self.on_fail()

                progress_bar.update(1)

                # Go to the next story
                if i < self.__stories_count - 1:
                    try:
                        next_story_button = self._web_driver.find_element_by_css_selector(constants.STORIES_NEXT_CSS)
                    except (NoSuchElementException, StaleElementReferenceException):
                        logger.error('Error scraping stories')
                        self.on_fail()
                    else:
                        next_story_button.click()
                        time.sleep(1)
                continue

            # Check if the story is an image and download it
            try:
                img_element = self._web_driver.find_element_by_css_selector(
                    'img[class="' + constants.STORIES_IMG_CSS[1:] + '"]')
            except (NoSuchElementException, StaleElementReferenceException):
                pass
            else:
                img_url = img_element.get_attribute('src')

                try:
                    retriever.download(img_url, self.__user.output_user_stories_path)
                except (OSError, RequestException) as err:
                    logger.error(err)
                    self.on_fail()

                progress_bar.update(1)

                # Go to the next story
                if i < self.__stories_count - 1:
                    try:
                        next_story_button = self._web_driver.find_element_by_css_selector(constants.STORIES_NEXT_CSS)
                    except (NoSuchElementException, StaleElementReferenceException):
                        logger.error('Error scraping stories')
                        self.on_fail()
                    else:
                        next_story_button.click()
                        time.sleep(1)
                continue

        progress_bar.close()

    def on_fail(self):
        print('\nan error occurred while downloading images/videos')
        self._scraper.stop()
