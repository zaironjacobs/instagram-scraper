import logging
from instagram_scraper import helper

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from requests.exceptions import RequestException

from instagram_scraper import constants
from instagram_scraper import retriever
from instagram_scraper import actions

logger = logging.getLogger('__name__')


class ScrapeSingleContent(actions.Action):
    def __init__(self, scraper, link, output_path):
        super().__init__(scraper)
        self.__link = link
        self.__output_path = output_path

    def do(self):
        """ Find the src url of an image or video from a post with a single content and download it"""

        # Get the publish date of the post
        date_time = None

        try:
            element = self._web_driver.find_element_by_css_selector(constants.POST_TIME_CSS)
        except (NoSuchElementException, StaleElementReferenceException) as err:
            logger.error(err)
        else:
            date_time = element.get_attribute('datetime')

        # Get the image
        try:
            element = self._web_driver.find_element_by_css_selector(constants.IMG_CSS)
        except (NoSuchElementException, StaleElementReferenceException):
            pass
        else:
            img_url = element.get_attribute('src')
            file_name = helper.get_datetime_str(date_time) + '-' + retriever.get_file_name_from_url(img_url)

            try:
                retriever.download(img_url, self.__output_path, file_name=file_name)
            except (OSError, RequestException) as err:
                logger.error(err)
                self.on_fail()

        # Get the video
        try:
            element = self._web_driver.find_element_by_css_selector(constants.VID_CSS)
        except (NoSuchElementException, StaleElementReferenceException):
            pass
        else:
            vid_url = element.get_attribute('src')
            file_name = helper.get_datetime_str(date_time) + '-' + retriever.get_file_name_from_url(vid_url)

            try:
                retriever.download(vid_url, self.__output_path, file_name=file_name)
            except (OSError, RequestException) as err:
                logger.error(err)
                self.on_fail()

    def on_fail(self):
        print('an error occurred while downloading images/videos')
        self._scraper.stop()
