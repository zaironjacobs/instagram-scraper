import logging
import time

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import ElementClickInterceptedException
from requests.exceptions import RequestException

from .. import constants
from .. import actions
from .. import retriever
from .. import helper

logger = logging.getLogger('__name__')


class ScrapeMultipleContent(actions.Action):
    def __init__(self, scraper, link, output_path):
        super().__init__(scraper)
        self.__link = link
        self.__output_path = output_path

    def do(self):
        """ Find the src url of images and videos from a post with multiple content and download it """

        def click_next_control():
            """ Go to the next content in a post with multiple content """

            try:
                self._web_driver.find_element_by_css_selector(constants.NEXT_CONTROL_CSS).click()
                time.sleep(1)
            except (NoSuchElementException, StaleElementReferenceException, ElementClickInterceptedException) as error:
                logger.error(error)
                self._scraper.stop()

        # Get the publish date of the post
        date_time = None

        try:
            element = self._web_driver.find_element_by_css_selector(constants.POST_TIME_CSS)
        except (NoSuchElementException, StaleElementReferenceException) as err:
            logger.error(err)
        else:
            date_time = element.get_attribute('datetime')

        # Get amount of content in the post
        try:
            elements = self._web_driver.find_elements_by_css_selector(constants.INDICATOR)
        except (NoSuchElementException, StaleElementReferenceException) as err:
            logger.error(err)
            logger.error('error downloading post: %s' % self.__link)
            self.on_fail()
            return
        else:
            post_content_count = len(elements)

        for post_index in range(post_content_count):
            li_element = None

            # Find the ul element that contains the contents
            try:
                ul_element = self._web_driver.find_element_by_css_selector(constants.MULTIPLE_CONTENT_UL_CSS)
            except (NoSuchElementException, StaleElementReferenceException) as err:
                logger.error(err)
                self.on_fail()
                return

            # First displayed content is found at the first li inside ul
            if post_index == 0:
                try:
                    li_element = ul_element.find_elements_by_css_selector(constants.MULTIPLE_CONTENT_LI_CSS)[0]
                except (NoSuchElementException, StaleElementReferenceException) as err:
                    logger.error(err)
                    self.on_fail()

            # All displayed content that is not first or last is found at the second li inside ul
            elif 0 < post_index < post_content_count:
                try:
                    li_element = ul_element.find_elements_by_css_selector(constants.MULTIPLE_CONTENT_LI_CSS)[1]
                except (NoSuchElementException, StaleElementReferenceException) as err:
                    logger.error(err)
                    self.on_fail()

            # Last displayed content is found at the last li inside ul
            elif post_index == post_content_count - 1:
                try:
                    li_element = ul_element.find_elements_by_css_selector(constants.MULTIPLE_CONTENT_LI_CSS)[-1]
                except (NoSuchElementException, StaleElementReferenceException) as err:
                    logger.error(err)
                    self.on_fail()

            # Get the image src from the li element
            try:
                img_element = li_element.find_element_by_css_selector(constants.IMG_CSS)
            except (NoSuchElementException, StaleElementReferenceException):
                pass
            else:
                img_url = img_element.get_attribute('src')
                file_name = helper.get_datetime_str(date_time) + '-' + retriever.get_file_name_from_url(img_url)
                self.__download(img_url, self.__output_path, file_name=file_name)

                if post_index < post_content_count - 1:
                    click_next_control()
                    continue
                else:
                    return

            # Get the video src from a XHR request
            post_id = helper.extract_post_id_from_url(self.__link)
            if post_id == '':
                self.on_fail()
            vid_url = actions.GetVidSrcUrl(self._scraper, post_id, True, post_index).do()
            file_name = helper.get_datetime_str(date_time) + '-' + retriever.get_file_name_from_url(vid_url)
            self.__download(vid_url, self.__output_path, file_name=file_name)

            if post_index < post_content_count - 1:
                click_next_control()
                continue
            else:
                return

    def on_fail(self):
        print('\nan error occurred while downloading images/videos')
        self._scraper.stop()

    def __download(self, url, output_path, file_name):
        try:
            retriever.download(url, output_path, file_name)
        except (OSError, RequestException) as err:
            print(' error downloading')
            logger.error(err)
            self.on_fail()
