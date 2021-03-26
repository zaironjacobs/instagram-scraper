import logging
from instagram_scraper import helper

from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import StaleElementReferenceException
from requests.exceptions import RequestException

from .. import constants
from .. import actions
from .. import retriever

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
            post_box = self._web_driver.find_element_by_css_selector(constants.POST_BOX_CSS)
            img_element = post_box.find_element_by_css_selector(constants.IMG_CSS)
        except (NoSuchElementException, StaleElementReferenceException):
            pass
        else:
            img_url = img_element.get_attribute('src')
            file_name = helper.get_datetime_str(date_time) + '-' + retriever.get_file_name_from_url(img_url)
            self.__download(img_url, self.__output_path, file_name=file_name)
            return

        # Get the video
        post_id = helper.extract_post_id_from_url(self.__link)
        if post_id == '':
            self.on_fail()
        vid_url = actions.GetVidSrcUrl(self._scraper, post_id, False).do()
        file_name = helper.get_datetime_str(date_time) + '-' + retriever.get_file_name_from_url(vid_url)
        self.__download(vid_url, self.__output_path, file_name=file_name)

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
